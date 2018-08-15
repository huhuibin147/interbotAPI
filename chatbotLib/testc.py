# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 16:20:10 2018

@author: inter
"""

import tensorflow as tf
import jieba
import copy
import os
import pickle


Q_file = 'chatbotLib/data/questions.txt'
A_file = 'chatbotLib/data/answers.txt'
Q_pkl = 'chatbotLib/data/ques_vocab.pkl'
A_pkl = 'chatbotLib/data/ans_vocab.pkl'
vocab = {"<PAD>": 1, "<UNK>": 2, "<GO>": 3, "<EOS>": 4}

batch_size = 2

with open(Q_file, 'r', encoding='utf-8') as f:
    source_data = f.read()

with open(A_file, 'r', encoding='utf-8') as f:
    target_data = f.read()
 

def get_data():
    with open(Q_file, 'r', encoding='utf-8') as f:
        ques = f.read()
    with open(A_file, 'r', encoding='utf-8') as f:
        ans = f.read()
    return ques, ans
        

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


if os.path.exists(Q_pkl):
    with open(Q_pkl, 'rb') as f:
        ques_word2int = pickle.loads(f.read())
        ques_int2word = {v:k for k,v in ques_word2int.items()}
    with open(A_pkl, 'rb') as f:
        ans_word2int = pickle.loads(f.read())
        ans_int2word = {v:k for k,v in ans_word2int.items()}
else:
    ques, ans = get_data()
    ques_word2int, ques_int2word = get_vocab(ques)
    ans_word2int, ans_int2word= get_vocab(ans)


def source_to_seq(cutwords):
    sequence_length = 10
    return [ques_word2int.get(word, ques_word2int['<UNK>']) 
        for word in cutwords] + [ques_word2int['<PAD>']]*(sequence_length-len(cutwords))


def getAnswer(input_seq):
    cutwords = jieba.lcut(input_seq)
    ccword = [w for w in cutwords if w.strip() != '']
    text = source_to_seq(ccword)

    checkpoint = "chatbotLib/model/train_model.ckpt"

    loaded_graph = tf.Graph()
    with tf.Session(graph=loaded_graph) as sess:
        loader = tf.train.import_meta_graph(checkpoint + '.meta')
        loader.restore(sess, checkpoint)

        input_data = loaded_graph.get_tensor_by_name('inputs:0')
        logits = loaded_graph.get_tensor_by_name('predictions:0')
        source_sequence_length = loaded_graph.get_tensor_by_name('input_seq_len:0')
        target_sequence_length = loaded_graph.get_tensor_by_name('target_seq_len:0')
        
        answer_logits = sess.run(logits, {input_data: [text]*batch_size, 
                                          target_sequence_length: [len(ccword)]*batch_size, 
                                          source_sequence_length: [len(ccword)]*batch_size})[0] 


    pad = ques_word2int["<PAD>"] 

    return '{}'.format("".join([ans_int2word[i] for i in answer_logits if i != pad]))

if __name__ == '__main__':
    print(getAnswer('无敌'))