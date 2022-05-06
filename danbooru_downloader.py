import os
import requests

headers = {
    'referer': 'https://danbooru.donmai.us',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)\
        Chrome/91.0.4472.114 Safari/537.36'
}


# --------------------------------------------------
# メイン関数
# --------------------------------------------------
def main():
    from bs4 import BeautifulSoup as bs4

    urls = config()
    if urls == []:
        print('E: URLが見つかりません')
        return
    print('\n-----------------------------------------------')
    for url in urls:
        print('M: 探索:', url)
        page = requests.get(url, headers=headers)
        soup = bs4(page.text, 'html5lib')

        # メタデータを取得
        # index:id, series:原作品名またはオリジナル, artsit:絵師名
        index = url.split('/')[-1]
        series = get_tag(soup, 'copyright-tag-list')
        artist = get_tag(soup, 'artist-tag-list')

        # メタデータに基づきディレクトリの作成
        try:  # 版権モノの場合
            charas = get_tag(soup, 'character-tag-list')  # キャラ名
            img_dir = os.path.join('danbooru', series, charas, artist)
        except Exception:  # オリジナルの場合
            img_dir = os.path.join('danbooru', series, artist)
        os.makedirs(img_dir, exist_ok=True)

        # 画像データの取得
        link = soup.find('img', {'class': 'fit-width'})
        src = link.get('src').replace('sample-', '')
        src = src.replace('sample', 'original')  # 元データを参照
        fp = rel2abs_path(os.path.join(img_dir, index), 'exe')
        if os.path.isfile(f'{fp}.jpg') or os.path.isfile(f'{fp}.png'):
            print('W: ファイルは既に存在しています')
            continue
        save_img(src, fp)
        print(f'M: {img_dir} に保存しました')

        # 元画像へのリンク
        pixiv_url = soup.find('a', {'rel': 'external noreferrer nofollow'})
        print(f'{artist} | https://www.{pixiv_url.get_text()}')
        print('-----------------------------------------------')


# --------------------------------------------------
# 絶対パスを相対パスに [入:相対パス, 実行ファイル側or展開フォルダ側 出:絶対パス]
# --------------------------------------------------
def rel2abs_path(filename, attr):
    import sys

    if attr == 'temp':  # 展開先フォルダと同階層
        datadir = os.path.dirname(__file__)
    elif attr == 'exe':  # exeファイルと同階層の絶対パス
        datadir = os.path.dirname(sys.argv[0])
    else:
        raise print(f'E: 相対パスの引数ミス [{attr}]')
    return os.path.join(datadir, filename)


# --------------------------------------------------
# .URLの読み込み
# --------------------------------------------------
def config():
    import glob
    import configparser

    config_ini = configparser.ConfigParser(interpolation=None)
    urls = []  # URLの集合
    for config_path in glob.glob(rel2abs_path('./URL/*.URL', 'exe')):
        # iniファイルが存在する場合、ファイルを読み込む
        with open(config_path, encoding='utf-8') as fp:
            config_ini.read_file(fp)
            url = config_ini['InternetShortcut']['URL']
            url = url.split('?')
            urls.append(url[0])
    return urls


# --------------------------------------------------
# メタデータの取得 複数ある場合はカンマ区切り
# --------------------------------------------------
def get_tag(soup, find_cls):
    data = soup.find('ul', {'class': find_cls})
    tags = ''
    for elem in data.find_all('a', {'class': 'search-tag'}):
        tags = f'{tags}, {elem.get_text()}'
    return tags[2:]


# --------------------------------------------------
# 画像の保存
# --------------------------------------------------
def save_img(url, fp):
    try:
        with open(f'{fp}.jpg', 'wb') as savefile:
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            savefile.write(res.content)
    except requests.exceptions.RequestException:
        with open(f'{fp}.png', 'wb') as savefile:
            res = requests.get(f'{url[:-4]}.png', headers=headers)
            res.raise_for_status()
            savefile.write(res.content)
    except Exception as e:
        print(f'E: 画像のダウンロードでエラー | {e}')


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print('E: ', e)
    print('M: 終了しました')
    os.system('PAUSE')
