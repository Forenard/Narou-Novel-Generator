# coding: UTF-8
import save_novel
import os
from glob import glob
import markovify


def main(url, word_size,  out_max, out_min, out_num, first_word):
    id = url[url.strip('/').rfind('/'):len(url)]  # saveフォルダ識別番号
    bodies = ''
    if not os.path.exists(save_novel.save_folder+id):
        print('Path does not exist.')
        exit()
    for file in glob(save_novel.save_folder+id+'/*.txt'):
        with open(file, mode="r", encoding='utf-8') as f:
            bodies += f.read()  # txtファイルを読み込んで結合
    markov_model = markovify.NewlineText(
        bodies, state_size=word_size, well_formed=False)
    for _ in range(out_num):
        if(first_word != 'none'):
            try:
                sentence = markov_model.make_sentence_with_start(
                    max_words=out_max, min_words=out_min, tries=100, beginning=first_word).replace(' ', '')
            except:
                print(
                    'The word you entered may not exist in the novel.\nOr it may contain unidentifiable characters.')
                exit()
        else:
            sentence = markov_model.make_sentence(
                max_words=out_max, min_words=out_min, tries=100).replace(' ', '')
        print('out', sentence)


if __name__ == '__main__':
    print('If you haven\'t generated the data for your novel yet, run save_novel.py and run.')
    url = input(
        'Enter the URL of the novel.\n(ex:https://ncode.syosetu.com/n2267be)\n>')
    word_size = int(input(
        'Enter the state history (the more, the closer to the original).\n>'))
    out_max = int(
        input('Enter the maximum length of the text to be generated.\n>'))
    out_min = int(
        input('Enter the minimum length of the text to be generated.\n>'))
    out_num = int(input('Enter the number of texts to be generated.\n>'))
    first_word = input(
        'Enter the first word of the sentence to be generated.To generate randomly, enter "none".\n>')
    main(url, word_size,  out_max, out_min, out_num, first_word)
