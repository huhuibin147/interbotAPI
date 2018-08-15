# -*- coding: utf-8 -*-
"""
Created on Tue Aug  7 17:20:40 2018

@author: inter
"""

import jieba
import copy
import pickle
import tensorflow as tf
import numpy as np
from tensorflow.python.layers.core import Dense


Q_file = 'data/questions.txt'
A_file = 'data/answers.txt'
vocab = {"<PAD>": 1, "<UNK>": 2, "<GO>": 3, "<EOS>": 4}


def get_data():
    with open(Q_file, 'r', encoding='utf-8') as f:
        ques = f.read()
    with open(A_file, 'r', encoding='utf-8') as f:
        ans = f.read()
    return ques, ans
        
ques, ans = get_data()

def get_vocab(data):
    word2int = copy.deepcopy(vocab)
    lines = data.split('\n')
    v_index = len(word2int)

    for line in lines:
        words = jieba.lcut(line)
        for w in words:
            if w.strip() != '' and w not in word2int:
                word2int[w] = v_index
                v_index += 1

    int2word = {v:k for k,v in word2int.items()}
    return word2int, int2word


ques_word2int, ques_int2word = get_vocab(ques)
ans_word2int, ans_int2word= get_vocab(ans)

with open('ques_vocab.pkl', 'wb') as f:
    f.write(pickle.dumps(ques_word2int))

with open('ans_vocab.pkl', 'wb') as f:
    f.write(pickle.dumps(ans_word2int))

def data2int():
    ques_data2int = [[ques_word2int.get(word, vocab["<UNK>"]) 
        for word in jieba.lcut(lines)] for lines in ques.split('\n')]
    ans_data2int = [[ans_word2int.get(word, vocab["<UNK>"]) 
        for word in jieba.lcut(lines)] + [vocab["<EOS>"]] for lines in ans.split('\n')]
    return ques_data2int, ans_data2int

ques_data2int, ans_data2int = data2int()



def get_inputs_placeholder():
    lr = tf.placeholder(tf.float32, name='lr')
    inputs = tf.placeholder(tf.int32, [None, None], name='inputs')
    targets = tf.placeholder(tf.int32, [None, None], name='targets')
    input_seq_len = tf.placeholder(tf.int32, (None,), name='input_seq_len')
    target_seq_len = tf.placeholder(tf.int32, (None,), name='target_seq_len')
    max_target_seq_len = tf.reduce_max(target_seq_len, name='max_target_seq_len')
    return inputs, targets, lr, input_seq_len, target_seq_len, max_target_seq_len

ques_vocab_len = len(ques_word2int)
ans_vocab_len = len(ans_word2int)
encoder_embed_size = 15
decoder_embed_size = 15
rnn_size = 50
num_layers = 2
batch_size = 2
lean_rate = 0.001
epochs = 500

def get_encoder_layer(inputs, input_seq_len):
    encoder_embed = tf.contrib.layers.embed_sequence(inputs, ques_vocab_len, encoder_embed_size)
    lstm_cell = lambda size: tf.contrib.rnn.LSTMCell(rnn_size, 
                initializer=tf.random_uniform_initializer(-0.1, 0.1))
    cell = tf.contrib.rnn.MultiRNNCell([lstm_cell(rnn_size) for _ in range(num_layers)])
    encoder_output, encoder_state = tf.nn.dynamic_rnn(cell, encoder_embed, 
                      sequence_length=input_seq_len, dtype=tf.float32)
    return encoder_output, encoder_state

def get_decoder_layer(target_pad_input, target_seq_len, encoder_state, max_target_seq_len):
    decoder_embed = tf.Variable(tf.random_uniform([ans_vocab_len, decoder_embed_size]))
    decoder_embed_input = tf.nn.embedding_lookup(decoder_embed, target_pad_input)
    lstm_cell = lambda size: tf.contrib.rnn.LSTMCell(rnn_size, 
                initializer=tf.random_uniform_initializer(-0.1, 0.1))
    cell = tf.contrib.rnn.MultiRNNCell([lstm_cell(rnn_size) for _ in range(num_layers)])
    output_layer = Dense(ans_vocab_len, 
          kernel_initializer=tf.truncated_normal_initializer(mean=0.0,stddev=0.1))

    with tf.variable_scope("decode"):
        train_helper = tf.contrib.seq2seq.TrainingHelper(decoder_embed_input, 
                                        target_seq_len, time_major=False)
        train_decoder = tf.contrib.seq2seq.BasicDecoder(cell, train_helper, 
                                        encoder_state, output_layer)
        train_output, _, _ = tf.contrib.seq2seq.dynamic_decode(train_decoder, 
                    impute_finished=True, maximum_iterations=max_target_seq_len)

    with tf.variable_scope("decode", reuse=True):
        start_tokens = tf.tile(tf.constant([ans_word2int['<GO>']], dtype=tf.int32), [batch_size], 
                               name='start_tokens')
        predict_helper = tf.contrib.seq2seq.GreedyEmbeddingHelper(decoder_embed,
                                                 start_tokens,
                                                 ans_word2int["<GO>"])
        predict_decoder = tf.contrib.seq2seq.BasicDecoder(cell, predict_helper,
                                                          encoder_state, output_layer)
        predict_output, _, _ = tf.contrib.seq2seq.dynamic_decode(predict_decoder, 
                                          impute_finished=True,
                                          maximum_iterations=max_target_seq_len)
        
    
    return train_output, predict_output


def process_decoder_input(data, word2int, batch_size):
    ending = tf.strided_slice(data, [0, 0], [batch_size, -1], [1, 1])
    decoder_input = tf.concat([tf.fill([batch_size, 1], word2int["<GO>"]), ending], 1)
    return decoder_input


def s2s_model(inputs, input_seq_len, targets, batch_size, target_seq_len, max_target_seq_len):
    _, encoder_state = get_encoder_layer(inputs, input_seq_len)
    decoder_input = process_decoder_input(targets, ans_word2int, batch_size)
    train_output, predict_output = get_decoder_layer(decoder_input, target_seq_len, 
                                     encoder_state, max_target_seq_len)
    return train_output, predict_output
    


def get_batches(inputs, targets, batch_size, inputs_pad_int, target_pad_int):
    for i in range(len(inputs)//batch_size):
        start_idx = i * batch_size
        inputs_batch = inputs[start_idx: start_idx+batch_size]
        targets_batch = targets[start_idx: start_idx+batch_size]
        inputs_pad_batch, inputs_batch_len = pad_batch(inputs_batch, inputs_pad_int)
        target_pad_batch, target_batch_len = pad_batch(targets_batch, target_pad_int)
        yield np.array(inputs_pad_batch), inputs_batch_len, np.array(target_pad_batch), target_batch_len


def pad_batch(inputs_batch, inputs_pad_int):
    inputs_pad_batch = []
    inputs_batch_len = []
    max_input_batch_len = max([len(x) for x in inputs_batch])
    for batch in inputs_batch:
        l = len(batch)
        inputs_batch_len.append(l)
        inputs_pad_batch.append(batch + (max_input_batch_len - l) * [inputs_pad_int])

    return inputs_pad_batch, inputs_batch_len

checkpoint = "./model/train_model.ckpt"
outFlag = 50

def main():
    train_graph = tf.Graph()
    with train_graph.as_default():
        inputs, targets, lr, input_seq_len, target_seq_len, \
            max_target_seq_len = get_inputs_placeholder()
        train_output, predict_output = s2s_model(inputs, input_seq_len, targets, 
                                                 batch_size, target_seq_len,
                                                 max_target_seq_len)
        train_logits = tf.identity(train_output.rnn_output, name='logits')
        predict_logits = tf.identity(predict_output.sample_id, name='predictions')
        mask = tf.sequence_mask(target_seq_len, max_target_seq_len, 
                                dtype=tf.float32, name='mask')
        with tf.name_scope("optimization"):
            cost = tf.contrib.seq2seq.sequence_loss(train_logits, targets, mask)
            optimizer = tf.train.AdamOptimizer(lr)
            gradients = optimizer.compute_gradients(cost)
            capped_gradients = [(tf.clip_by_value(grad, -5., 5.), var) 
                for grad,var in gradients if grad is not None]
            train_op = optimizer.apply_gradients(capped_gradients)

    with tf.Session(graph=train_graph) as sess:
        sess.run(tf.global_variables_initializer())
        stopFlag = 0
        for epoch_i in range(epochs):
            for batch_i, (inputs_pad_batch, inputs_batch_len, target_pad_batch, target_batch_len) in \
                enumerate(get_batches(ques_data2int, ans_data2int, batch_size, 
                    ques_word2int["<PAD>"], ans_word2int["<PAD>"])):
                _, loss = sess.run([train_op, cost],
                        feed_dict={
                            inputs: inputs_pad_batch,
                            targets: target_pad_batch,
                            lr: lean_rate,
                            input_seq_len: inputs_batch_len,
                            target_seq_len: target_batch_len
                        })
                if batch_i % outFlag == 0:
                    print('Epoch {:>3}/{} Batch {:>4}/{} - Traning Loss: {:>6.5f}'.format(
                            epoch_i, epochs, batch_i, len(target_pad_batch)//batch_size,loss 
                        ))
                if loss < 0.00001:
                    stopFlag = 1
            if stopFlag == 1:
                break

        saver = tf.train.Saver()
        saver.save(sess, checkpoint)
        print('Model Trained and Saved')

main()


