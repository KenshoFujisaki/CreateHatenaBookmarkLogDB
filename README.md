CreateHatenaBookmarkLogDB
=========================

はてブRSSファイルに対して，そのそれぞれのWebページについて本文抽出と形態素解析をし，  
その結果をMySQLのDBに登録します．結果，次のようなDB（MySQL）状態が出来上がります．
![ER図](http://cdn-ak.f.st-hatena.com/images/fotolife/n/ni66ling/20141223/20141223184030.png)  

# 事前準備
MacOSX環境にてgcc-4.8, mecab, python, pip, rubyが事前にインストールされていることを前提とします．
### 1. Cコードのコンパイル
```bash
$ cd scripts
$ gcc-4.8 `mysql_config --include` `mecab-config --cflags` parse_web_content_to_morpheme.cpp `mysql_config --libs` `mecab-config --libs` -fopenmp -o parse_web_content_to_morpheme.o
```
### 2. pdftotextコマンドのインストール
```bash
$ brew install xpdf
```
詳細設定は[PDF文書からテキストを抽出する](http://d.hatena.ne.jp/uchiuchiyama/20060509/1147184615 "PDF文書からテキストを抽出する")を参照
### 3. MySQL-pythonのインストール
```bash
$ sudo pip install MySQL-python
```
### 3. MySQLのユーザー登録・hatena_bookmarkデータベースへの権限付与
```bash
$ mysql -u root -p
```
```sql
> CREATE USER 'hatena'@'localhost' IDENTIFIED BY 'hatena';
> GRANT ALL PRIVILEGES ON hatena_bookmark.* TO 'hatena'@'localhost' IDENTIFIED BY 'hatena'; 
```

# 使い方
### 1. はてブRSSファイルのダウンロード
```
1. はてブのページを開く
2. 画面上部の[設定] → [データ管理]を開く
3. [RSS 1.0形式でダウンロード]を右クリックして「別名でリンク先を保存」し,
   ｢./scripts/data/hatena_bookmark_rss.htm」に保存
```

### 2. ストップワードの修正（任意）
```bash
$ vim scripts/data/stoplist.dat
```
デフォルトのストップワードの詳細は[HTML特殊文字を含めたストップワード](http://d.hatena.ne.jp/ni66ling/20141130 "HTML特殊文字を含めたストップワード")を参照
### 3. 実行
```bash
$ cd scripts
$ ./main.sh
```

# テーブル定義について
##### urlテーブル（URLを保持）
|カラム名|内容|
|---|---|
|id|ID|
|url|URL|
|title|ページタイトル|
|update_date|更新日時|

##### tagテーブル（タグを保持）
|カラム名|内容|
|---|---|
|id|ID|
|name|タグ名|

##### morphemeテーブル（webページの本文に含まれる形態素，IDFを保持）
|カラム名|内容|
|---|---|
|id|ID|
|name|形態素名|
|idf|IDF（この形態素が存在するwebページ数）|

##### stoplistテーブル（ストップワード，形態素とのマッピングを保持）
|カラム名|内容|
|---|---|
|id|ID|
|name|ストップワード名|
|morpheme_id|morphemeテーブルのid|

##### url_contentテーブル（webページの本文情報を保持）
|カラム名|内容|
|---|---|
|id|ID|
|url_id|urlテーブルのid|
|content|webページurl_idの本文情報|

##### url_tagテーブル（URLとタグのマッピングを保持）
|カラム名|内容|
|---|---|
|id|ID|
|url_id|urlテーブルのid|
|tag_id|tagテーブルのid|

##### url_morphemeテーブル（URLと形態素のマッピング，TFを保持）
|カラム名|内容|
|---|---|
|id|ID|
|url_id|urlテーブルのid|
|morpheme_id|morphemeテーブルのid|
|morpheme_count|TF（webページurl_idにおける形態素morpheme_idの出現回数）|

# ライセンス
extractcontent.rbはBSDライセンスにて配布されたコードであり，Nakatani Shuyoさんが著作権を保持しており，無保証です．
