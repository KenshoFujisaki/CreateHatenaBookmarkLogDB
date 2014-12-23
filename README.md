CreateHatenaBookmarkLogDB
=========================

はてブRSSファイルに対して，そのそれぞれのWebページについて本文抽出と形態素解析をし，  
その結果をMySQLのDBに登録します．結果，次のようなDB（MySQL）状態が出来上がります．
![ER図](http://cdn-ak.f.st-hatena.com/images/fotolife/n/ni66ling/20141223/20141223153137.png)  

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
