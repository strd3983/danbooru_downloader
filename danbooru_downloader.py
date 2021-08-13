import os
import glob
import requests
import urllib
import configparser
from bs4 import BeautifulSoup as bs4

# import pandas as pd


# --------------------------------------------------
# メイン関数
# --------------------------------------------------
def main():
    urls = config()
    if urls == []:
        print('URLが見つかりません')
        return
    for url in urls:
        print('\n探索:', url)
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        page = requests.get(url, headers=headers)
        soup = bs4(page.text, 'html5lib')
        index = url.split('/')[-1]  # danbooruのidをファイル名に
        series = get_tag(soup, 'copyright-tag-list')  # 原作品名またはオリジナル
        artist = get_tag(soup, 'artist-tag-list')  # 絵師名
        # メタデータに基づきディレクトリの作成
        try:  # 版権モノの場合
            charas = get_tag(soup, 'character-tag-list')  # キャラ名
            img_dir = os.path.join('danbooru', series, charas, artist)
            os.makedirs(img_dir, exist_ok=True)
        except Exception:  # オリジナルの場合
            img_dir = os.path.join('danbooru', series, artist)
            os.makedirs(img_dir, exist_ok=True)

        # 画像データの取得
        link = soup.find('img', {'class': 'fit-width'})
        src = link.get('src').replace('sample-',
                                      '').replace('sample', 'original')
        save_img(src, os.path.join(img_dir, index))
        print(img_dir, 'に保存しました')


# --------------------------------------------------
# 設定iniファイルの読み込み
# --------------------------------------------------
def config():
    config_ini = configparser.ConfigParser(interpolation=None)
    i = 0
    urls = []
    for config_path in glob.glob('./URL/*.URL'):
        i += 1
        # iniファイルが存在する場合、ファイルを読み込む
        with open(config_path, encoding='utf-8') as fp:
            config_ini.read_file(fp)
            # iniの値取得
            url = config_ini['InternetShortcut']['URL']
            url = url.split('?')
            urls.append(url[0])
        os.remove(config_path)
    # 設定出力
    return urls


# --------------------------------------------------
# メタデータの取得 複数ある場合はカンマ区切り
# --------------------------------------------------
def get_tag(soup, find_cls):
    data = soup.find('ul', {'class': find_cls})
    tags = ''
    for elem in data.find_all('a', {'class': 'search-tag'}):
        tags = tags + ', ' + elem.get_text()
    return tags[2:]


# --------------------------------------------------
# 画像の保存
# --------------------------------------------------
def save_img(url, dir_path):
    try:  # jpgの場合
        with urllib.request.urlopen(url) as web_file:
            data = web_file.read()
            with open(dir_path + '.jpg', mode='wb') as local_file:
                local_file.write(data)
    except urllib.error.URLError:  # pngの場合
        with urllib.request.urlopen(url.replace('.jpg', '.png')) as web_file:
            data = web_file.read()
            with open(dir_path + '.png', mode='wb') as local_file:
                local_file.write(data)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
    # print('終了しました')
    # os.system('PAUSE')
