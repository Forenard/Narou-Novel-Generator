# coding: UTF-8
import time
import re
import os
import MeCab
from urllib.request import urlopen
from bs4 import BeautifulSoup

tagger = MeCab.Tagger('-Owakati')
save_folder = 'save'
narou_url = 'https://ncode.syosetu.com'


def make_bsobj(url):
    '''
    引数:(str)対象のURL
    返り値:(BeautifulSoup)BeautifulSoupオブジェクト
    サーバーへの負担軽減の為アクセスの間隔を1秒開けます
    '''
    time.sleep(1)
    return BeautifulSoup(urlopen(url).read().decode(
        'utf-8', 'ignore'), "html.parser")


def format_text(t):
    '''
    引数:(str)テキスト
    返り値:(str)フォーマット後のテキスト
    markovifyが読み込むとエラーを吐き出す文字があるので、それを除去する
    '''
    t = re.sub(r'[0-9０-９a-zA-Zａ-ｚＡ-Ｚ]+', "", t)
    return re.sub(r'[\．_－―─！＠＃＄％＾＆\-‐|\\＊\“（）＿■×+α※÷⇒—●★☆〇◎◆▼◇△□(：〜～＋=)／*&^%$#@!~`){}［］…\[\]\"\'\”\’:;<>?＜＞〔〕〈〉？、。・,\./『』【】「」→←○《》≪≫\r\u3000\u2000]+', "", t)


def get_bodies_from_url(url):
    '''
    引数:(str)なろう小説の各ページのURL(リゼロならhttps://ncode.syosetu.com/n2267be/1/ など)
    返り値:(str)分かち書き後、文章単位で改行された本文
    '''
    bsobj = make_bsobj(url)
    bodies = ''
    for body in bsobj.findAll("div", {"id": "novel_honbun"})[0].findAll("p"):
        formatted = format_text(body.get_text())
        if formatted == '':
            continue
        bodies += tagger.parse(formatted)+'\n'
    return bodies


def get_num_of_pages(url):
    '''
    引数:(str)なろう小説のトップページのURL(リゼロならhttps://ncode.syosetu.com/n2267be/)
    返り値:(int)ページ数
    '''
    bsobj = make_bsobj(url+'/1')
    return int(bsobj.select('#novel_no')[0].get_text().replace('1/', ''))


def main():
    url = input(
        "Enter the URL of the novel.\n(ex:https://ncode.syosetu.com/n2267be)\n>")  # url
    pages_num = int(
        input("Enter the number of pages you want to save.\n>"))  # 保存するページ数
    id = url[url.strip('/').rfind('/'):len(url)]  # saveフォルダ構成用に識別番号を取得
    all_pages_num = get_num_of_pages(url)  # 全ページ数の取得
    for i in range(1, pages_num+1):
        if i > all_pages_num:
            break
        bodies = get_bodies_from_url(url+'/'+str(i))  # 本文の取得
        folder_path = save_folder+id
        os.makedirs(folder_path, exist_ok=True)  # 保存用フォルダの構成
        with open(folder_path+'/'+str(i)+'.txt', mode="w", encoding='utf-8') as f:
            f.write(bodies)


if __name__ == '__main__':
    main()
