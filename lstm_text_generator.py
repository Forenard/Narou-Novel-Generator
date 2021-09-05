from __future__ import print_function
import save_novel
import tensorflow as tf
import os
import sys
import random
import numpy as np
import re
import MeCab
from glob import glob
from keras.optimizers import RMSprop
from keras.layers import LSTM
from keras.layers import Dense
from keras.models import Sequential
from keras.callbacks import LambdaCallback
physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    for k in range(len(physical_devices)):
        tf.config.experimental.set_memory_growth(physical_devices[k], True)
        print('memory growth:', tf.config.experimental.get_memory_growth(
            physical_devices[k]))
else:
    print("Not enough GPU hardware devices available")
# ----------------------------------------------------------------
tagger = MeCab.Tagger("-Owakati")


def make_wakati(sentence):
    sentence = tagger.parse(sentence)
    sentence = re.sub(r'[0-9０-９a-zA-Zａ-ｚＡ-Ｚ]+', " ", sentence)
    sentence = re.sub(
        r'[\．_－―─！＠＃＄％＾＆\-‐|\\＊\“（）＿■×+α※÷⇒—●★☆〇◎◆▼◇△□(：〜～＋=)／*&^%$#@!~`){}［］…\[\]\"\'\”\’:;<>?＜＞〔〕〈〉？、。・,\./『』【】「」→←○《》≪≫\n\u3000]+', "", sentence)
    wakati = sentence.split(" ")
    wakati = list(filter(("").__ne__, wakati))
    return wakati


bodies = ''
url = input(
    'Enter the URL of the novel.\n(ex:https://ncode.syosetu.com/n2267be)\n>')
id = url[url.strip('/').rfind('/'):len(url)]
if not os.path.exists(save_novel.save_folder+id):
    print('Path does not exist.')
    exit()
for file in glob(save_novel.save_folder+id+'/*.txt'):
    with open(file, mode="r", encoding='utf-8') as f:
        bodies += f.read()
text = make_wakati(bodies)
print(len(text))
text = text[0:min(len(text), 25000)]
chars = text
count = 0
char_indices = {}
indices_char = {}

for word in chars:
    if not word in char_indices:
        char_indices[word] = count
        count += 1
indices_char = dict([(value, key) for (key, value) in char_indices.items()])

maxlen = 5
step = 1
sentences = []
next_chars = []
for i in range(0, len(text) - maxlen, step):
    sentences.append(text[i: i + maxlen])
    next_chars.append(text[i + maxlen])
print('nb sequences:', len(sentences))
print('Vectorization...')
x = np.zeros((len(sentences), maxlen, len(chars)), dtype=np.bool)
y = np.zeros((len(sentences), len(chars)), dtype=np.bool)
for i, sentence in enumerate(sentences):
    for t, char in enumerate(sentence):
        x[i, t, char_indices[char]] = 1
    y[i, char_indices[next_chars[i]]] = 1

print('Build model...')
model = Sequential()
model.add(LSTM(128, input_shape=(maxlen, len(chars))))
model.add(Dense(len(chars), activation='softmax'))

optimizer = RMSprop(lr=0.01)
model.compile(loss='categorical_crossentropy', optimizer=optimizer)


def sample(preds, temperature=1.0):
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)


def on_epoch_end(epoch, _):
    print()
    print('----- Generating text after Epoch: %d' % epoch)
    start_index = random.randint(0, len(text) - maxlen - 1)
    start_index = 0
    for diversity in [0.2]:
        print('----- diversity:', diversity)
        generated = ''
        sentence = text[start_index: start_index + maxlen]
        generated += "".join(sentence)
        print(sentence)
        print('----- Generating with seed: "' + "".join(sentence) + '"')
        sys.stdout.write(generated)
        for i in range(400):
            x_pred = np.zeros((1, maxlen, len(chars)))
            for t, char in enumerate(sentence):
                x_pred[0, t, char_indices[char]] = 1.
            preds = model.predict(x_pred, verbose=0)[0]
            next_index = sample(preds, diversity)
            next_char = indices_char[next_index]
            generated += next_char
            sentence = sentence[1:]
            sentence.append(next_char)
            sys.stdout.write(next_char)
            sys.stdout.flush()
        print()


print_callback = LambdaCallback(on_epoch_end=on_epoch_end)
model.summary()
model.fit(x, y,
          batch_size=128,
          epochs=30,
          callbacks=[print_callback])
