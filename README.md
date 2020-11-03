# Sitebot 

## Installation 
To run synthesizer file typecheck and train, you need to have installed genie and thingtalk on the following branches: 
- genie: `next`
- thingtalk: `wip/nn-syntax-assignments-for-nancy`

And run the following in order: 
- Clone thingtalk 
- Switch to `wip/nn-syntax-assignments-for-nancy` branch 
- Run `npm install`
- Clone genie 
- Switch to `next`
- Run `npm install`
- Run `npm link ../thingtalk`
- Run `npm link` 
- Restart the terminal 

In the genie directory, run `ls -la node_modules` and make sure there is a symlink to the right thingtalk directory, and that both genie and thingtalk are on the right branch. May be necessary to run `npx make` if you screw up and need to remake without reinstalling all dependencies (ie you switch a branch).  

## To Train: 

Requirements: You need to run on: 
- Python 1.6 

```
genienlp train --data /home/nancyxu97/SiteBot/synthesis/dataset --embeddings ./embeddings --save /home/nancyxu97/SiteBot/synthesis/save --dimension 768 --transformer_hidden 768 --trainable_decoder_embeddings 50 --encoder_embeddings=bert-base-uncased --decoder_embeddings= --seq2seq_encoder=Identity --rnn_layers 1 --transformer_heads 12 --transformer_layers 0 --rnn_zero_state=average --train_encoder_embeddings --transformer_lr_multiply 0.1 --train_batch_tokens 2000 --append_question_to_context_too --val_batch_size 64 --almond_preprocess_context --override_question . --cache /home/nancyxu97/SiteBot/synthesis/cache --train_tasks almond --preserve_case --save_every 1000 --log_every 100 --val_every 1000 --exist_ok --skip_cache --no_commit 
```
See the training experiment spreadsheet here: https://docs.google.com/spreadsheets/d/1O7E0ipTqzBm8gXoxpoosVryC84wykes4OoQRM_rxdo0/edit?usp=sharing

## To Typecheck Run: 
```
genie typecheck path-to-file --dropped dropped --output out --thingpedia \@webagent/manifest.tt --cache typecheck-cache.txt --interactive
```

The file you wish you typecheck needs to be of the form (per line) : 
- hash_id \t utterance \t NN syntax thingtalk 
- all tokens must have " " around them including , / . / " etc 
- text in double quotes in thingtalk must come directly from tokens in the utterance
- don't use single quotes 
- remove all special tokens such as emojis and trademark symbols 

## Misc 
### Splitting Train / Eval 
Currently we run the synthesis 1M times which produces ~2M datapoints. Split 90/10 train/eval with something like `(head -1789594 > train.tsv; cat > eval.tsv) < synth1M-2.txt`
