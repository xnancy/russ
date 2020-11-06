import json
import logging
import os
import re
from pprint import pformat
from collections import defaultdict
import copy
import shutil

# multiprocessing with CUDA
from torch.multiprocessing import Process, set_start_method
try:
     set_start_method('spawn')
except RuntimeError:
    pass

import torch

from genienlp import models
from genienlp.data_utils.embeddings import load_embeddings
from genienlp.tasks.registry import get_tasks
from genienlp.util import set_seed, preprocess_examples, load_config_json, make_data_loader, log_model_size, init_devices, have_multilingual, combine_folders_on_disk, split_folder_on_disk, get_part_path
from genienlp.validate import generate_with_model, calculate_and_reduce_metrics

import argparse

from genienlp import arguments, train, predict, server, cache_embeddings, export


logger = logging.getLogger(__name__)

def get_all_splits(args):
    splits = []
    if len(args.pred_languages) == 1 and len(args.tasks) > 1:
        args.pred_languages *= len(args.tasks)
    for i, task in enumerate(args.tasks):
        task_languages = args.pred_languages[i]
        logger.info(f'Loading {task}')
        kwargs = {'train': None}
        if args.evaluate == 'valid':
            kwargs['test'] = None
            if args.pred_set_name is not None:
                kwargs['validation'] = args.pred_set_name
        elif args.evaluate == 'test':
            kwargs['validation'] = None
        else:
            raise ValueError('Split used for prediction should be either valid or test')
        
        kwargs.update({'skip_cache': args.skip_cache, 'subsample': args.subsample,
                       'cached_path': os.path.join(args.cache, task.name), 'all_dirs': task_languages,
                       'almond_lang_as_question': args.almond_lang_as_question})
        
        kwargs['separate_eval'] = args.separate_eval
        task_splits = task.get_splits(root=args.data, lower=args.lower, **kwargs)
        if not isinstance(task_splits, list):
            task_splits = [task_splits]
        task_split_processed = []
        for split in task_splits:
            assert (split.eval or split.test) and not split.train and not split.aux
            split = split.eval if split.eval else split.test
            preprocess_examples(args, [task], [split], train=False)
            task_split_processed.append(split)
        splits.append(task_split_processed)
    return splits


def prepare_data(args, numericalizer, embeddings):
    splits = get_all_splits(args)
    logger.info(f'Vocabulary has {numericalizer.num_tokens} tokens from training')
    new_words = []
    for task_splits in splits:
        for split in task_splits:
            new_words += numericalizer.grow_vocab(split)
            logger.info(f'Vocabulary has expanded to {numericalizer.num_tokens} tokens')

    for emb in embeddings:
        emb.grow_for_vocab(numericalizer.vocab, new_words)

    return splits


def run(args, device):
    numericalizer, context_embeddings, question_embeddings, decoder_embeddings = load_embeddings(args.embeddings, args.context_embeddings, args.question_embeddings, args.decoder_embeddings,
                        args.max_generative_vocab, logger)
    numericalizer.load(args.path)
    for emb in set(context_embeddings + question_embeddings + decoder_embeddings):
        emb.init_for_vocab(numericalizer.vocab)

    logger.info(f'Initializing Model')
    Model = getattr(models, args.model)
    model = Model.from_pretrained(args.path,
                                  numericalizer=numericalizer,
                                  context_embeddings=context_embeddings,
                                  question_embeddings=question_embeddings,
                                  decoder_embeddings=decoder_embeddings,
                                  args=args,
                                  device=device
                                  )
    val_sets = prepare_data(args, numericalizer, set(context_embeddings + question_embeddings + decoder_embeddings))

    logger.info(f'Preparing iterators')
    if len(args.val_batch_size) == 1 and len(val_sets) > 1:
        args.val_batch_size *= len(val_sets)
    iters = []
    task_index = 0
    for task, bs, val_set in zip(args.tasks, args.val_batch_size, val_sets):
        task_iter = []
        task_languages = args.pred_languages[task_index]
        if task_languages is not None and args.separate_eval:
            task_languages = task_languages.split('+')
            assert len(task_languages) == len(val_set)
            for index, set_ in enumerate(val_set):
                loader = make_data_loader(set_, numericalizer, bs, device,
                                          append_question_to_context_too=args.append_question_to_context_too,
                                          override_question=args.override_question, override_context=args.override_context)
                task_iter.append((task, task_languages[index], loader))
        # single language task or no separate eval
        else:
           loader = make_data_loader(val_set[0], numericalizer, bs, device,
                                     append_question_to_context_too=args.append_question_to_context_too,
                                     override_question=args.override_question, override_context=args.override_context)
           task_iter.append((task, task_languages, loader))

        iters.extend(task_iter)
        task_index += 1

    log_model_size(logger, model, args.model)
    model.to(device)

    decaScore = []
    task_scores = defaultdict(list)
    model.eval()

    eval_dir = os.path.join(args.eval_dir, args.evaluate)
    os.makedirs(eval_dir, exist_ok=True)

    with torch.no_grad():
        for task, language, it in iters:
            logger.info(task.name)
            # single language task
            if language is None:
                prediction_file_name = os.path.join(eval_dir, task.name + '.tsv')
                results_file_name = os.path.join(eval_dir, task.name + '.results.json')
            # multi language task
            else:
                prediction_file_name = os.path.join(eval_dir, task.name + '_{}.tsv'.format(language))
                results_file_name = os.path.join(eval_dir, task.name + '_{}.results.json'.format(language))
            if os.path.exists(prediction_file_name):
                if args.overwrite:
                    logger.warning(f'{prediction_file_name} already exists -- overwriting **')
                else:
                    raise OSError(f'{prediction_file_name} already exists')
            if os.path.exists(results_file_name):
                if args.overwrite:
                    logger.warning(f'{results_file_name} already exists -- overwriting **')
                else:
                    raise OSError(f'{results_file_name} already exists')
            
            _, predictions, answers, contexts, _ = generate_with_model(model, it, numericalizer, task, args, prediction_file_name)
            
            parseds = [] 
            for prediction in predictions : 
                parseds.append(prediction[0])

            # list of strings, each a parsed set of instructions
            return parseds

def adjust_multilingual_eval(args):
    if (have_multilingual(args.task_names) and args.pred_languages is None) or (
            args.pred_languages and len(args.task_names) != len(args.pred_languages)):
        raise ValueError('You have to define prediction languages when you have a multilingual task'
                         'Use None for single language tasks. Also provide languages in the same order you provided the tasks.')

    if args.pred_languages is None:
        args.pred_languages = [None for _ in range(len(args.task_names))]

    # preserve backward compatibility for single language tasks
    for i, task_name in enumerate(args.task_names):
        if 'multilingual' in task_name and args.pred_languages[i] is None:
            raise ValueError('You have to define prediction languages for this multilingual task: {}'.format(task_name))
        elif 'multilingual' not in task_name and args.pred_languages[i] is not None:
            logger.warning('prediction languages should be empty for single language tasks')
            args.pred_languages[i] = None
            
            
def check_and_update_generation_args(args):
    """
    checks all generation commandline arguments. Since these arguments are all lists and shorthand can be used, we expand them to match the expected length
    for instance, [1.0] becomes [1.0 1.0] if all other generation arguments are of length 2
    """
    hyperparameters = ['num_outputs', 'temperature', 'top_k', 'top_p', 'repetition_penalty', 'num_beams', 'no_repeat_ngram_size']
    max_hyperparameter_len = max([len(getattr(args, h)) for h in hyperparameters])
    valid_len = [1, max_hyperparameter_len]
    for h in hyperparameters:
        if (len(getattr(args, h)) not in valid_len):
            logger.error('Hyperparameters should either have the same number of values as others or have exactly one value.')
        # If only one value is provided, use the same value for all samples
        setattr(args, h, getattr(args, h) * (max_hyperparameter_len // len(getattr(args, h))))

    logger.info('Will output %d sequences for each input.', sum(args.num_outputs))
    # logger.info('Effective batch size for each GPU is %d', args.batch_size * max(args.num_outputs))

def parse_argv(parser):
    parser.add_argument('--path', default='/Users/nancy/Documents/PhD/Multi-Modal/SiteBot/SiteBot/representation/save')
    parser.add_argument('--evaluate', type=str, default='test',
                        help='Which dataset to do predictions for (test or dev)')
    parser.add_argument('--pred_set_name', type=str, help='Name of dataset to run prediction for; will be ignored if --evaluate is test')
    parser.add_argument('--tasks',
                        default=['almond'], dest='task_names', nargs='+')
    parser.add_argument('--devices', default=None, nargs='+', type=int,
                        help='a list of devices that can be used for prediction. By default, all devices will be used.')
    parser.add_argument('--seed', default=123, type=int, help='Random seed.')
    parser.add_argument('--data', default='/Users/nancy/Documents/PhD/Multi-Modal/SiteBot/SiteBot/representation/dataset', type=str, help='where to load data from.')
    parser.add_argument('--embeddings', default='.embeddings/', type=str, help='where to save embeddings.')
    parser.add_argument('--checkpoint_name', default='best.pth',
                        help='Checkpoint file to use (relative to --path, defaults to best.pth)')
    parser.add_argument('--bleu', action='store_true', help='whether to use the bleu metric (always on for iwslt)')
    parser.add_argument('--rouge', action='store_true',
                        help='whether to use the bleu metric (always on for cnn, dailymail, and cnn_dailymail)')
    parser.add_argument('--overwrite', action='store_true', help='whether to overwrite previously written predictions')
    parser.add_argument('--silent', action='store_true', help='whether to print predictions to stdout')

    parser.add_argument('--skip_cache', action='store_true',
                        help='whether use exisiting cached splits or generate new ones')
    parser.add_argument('--eval_dir', type=str, default='predict', help='use this directory to store eval results')
    parser.add_argument('--cache', default='.cache', type=str, help='where to save cached files')

    parser.add_argument('--saved_models', default='./saved_models', type=str,
                        help='directory where cached models should be loaded from')
    parser.add_argument('--subsample', default=20000000, type=int,
                        help='subsample the eval/test datasets (experimental)')
                        
    parser.add_argument('--pred_languages', type=str, nargs='+',
                        help='used to specify dataset languages used during prediction for multilingual tasks'
                        'multiple languages for each task should be concatenated with +')
    parser.add_argument('--separate_eval', action='store_true',
                        help='evaluate on each language eval set separately')
    
    parser.add_argument('--main_metric_only', action='store_true', help='If True, we only calculate the deca score metric for each task.')
    # If not None, these values will override the values saved in the trained model's config file
    parser.add_argument('--val_batch_size', nargs='+', default=None, type=int,
                        help='Batch size for validation corresponding to tasks in val tasks')
    parser.add_argument("--reduce_metrics", type=str, default='max', choices=['max'], help='How to calculate the metric when there are multiple outputs per input.')

    # These are generation hyperparameters. Each one can be a list of values in which case, we generate `num_outputs` outputs for each set of hyperparameters.
    parser.add_argument("--num_outputs", type=int, nargs='+', default=[1], help='number of sequences to output per input')
    parser.add_argument("--temperature", type=float, nargs='+', default=[0.0],
                        help="temperature of 0 implies greedy sampling")
    parser.add_argument("--repetition_penalty", type=float, nargs='+', default=[1.0],
                        help="primarily useful for CTRL model; in that case, use 1.2")
    parser.add_argument("--top_k", type=int, nargs='+', default=[0], help='0 disables top-k filtering')
    parser.add_argument("--top_p", type=float, nargs='+', default=[1.0], help='1.0 disables top-p filtering')
    parser.add_argument("--num_beams", type=int, nargs='+', default=[1], help='1 disables beam seach')
    parser.add_argument("--no_repeat_ngram_size", type=int, nargs='+', default=[0], help='ngrams of this size cannot be repeated in the output. 0 disables it.')


def commands_to_webtalk(commands):
    try:
        os.remove("/Users/nancy/Documents/PhD/Multi-Modal/SiteBot/SiteBot/representation/predict/test/almond.tsv")
    except OSError:
        pass

    try:
        os.remove("/Users/nancy/Documents/PhD/Multi-Modal/SiteBot/SiteBot/representation/dataset/almond/test.tsv")
    except OSError:
        pass
    
    with open('/Users/nancy/Documents/PhD/Multi-Modal/SiteBot/SiteBot/representation/dataset/almond/test.tsv', 'w') as f:
        for command in commands: 
            command = re.sub(' +' ,  ' ' ,  command.lower().replace(",", " , ").replace("?", " ? ")).strip()
            if command[-1] == ".": 
                command = command[:-1] + " ."
            f.write('123' + "\t" + command + "\t" + "."  + "\n")

    import argparse
    parser = argparse.ArgumentParser()
    parse_argv(parser)
    args = parser.parse_args()

    load_config_json(args)
    check_and_update_generation_args(args)
    adjust_multilingual_eval(args)
    set_seed(args)
    args.tasks = list(get_tasks(args.task_names, args).values())

    print(f'Arguments:\n{pformat(vars(args))}')
    print(f'Loading from {args.best_checkpoint}')

    devices = init_devices(args)
    if args.devices is not None:
        devices = [devices[i] for i in args.devices]

    return run(args, devices[0])


print(commands_to_webtalk(['got to amazon.com', 'click me']))
