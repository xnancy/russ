# Sitebot 

## To Train: 
```genienlp train --data /home/nancyxu97/SiteBot/synthesis/dataset --embeddings ./embeddings --save /home/nancyxu97/SiteBot/synthesis/save --dimension 768 --transformer_hidden 768 --trainable_decoder_embeddings 50 --encoder_embeddings=bert-base-uncased --decoder_embeddings= --seq2seq_encoder=Identity --rnn_layers 1 --transformer_heads 12 --transformer_layers 0 --rnn_zero_state=average --train_encoder_embeddings --transformer_lr_multiply 0.1 --train_batch_tokens 2000 --append_question_to_context_too --val_batch_size 64 --almond_preprocess_context --override_question . --cache /home/nancyxu97/SiteBot/synthesis/cache --train_tasks almond --preserve_case --save_every 1000 --log_every 100 --val_every 1000 --exist_ok --skip_cache --no_commit 
```
