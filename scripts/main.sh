#!/bin/bash

# 最新のはてブRSSを取得します
echo "> DBに登録するはてブRSSを./data/hatena_bookmark_rss.htmに保存して下さい．"
echo "> 処理を開始すると，現在のDBは初期化されます．"
echo "> 処理を実行してもよろしいですか？(y/n)"
read is_yes
if [ $is_yes != "y" ]; then
  echo "> 処理が中断されました．"
  exit 1
fi

# MySQLにテーブル定義します．
echo "> DBにテーブルを登録します．"
mysql -uhatena -phatena -Dhatena_bookmark < hatena_bookmark_table_def_foreigenkey.sql
if [ $? -eq 0 ]; then
  echo "> 正常に終了しました．"
else
  echo "> テーブルをDBに登録する際に問題が発生しました．"
  echo "> MySQLにてユーザーhatena(パスワードはhatena)が存在し，同ユーザーにてデータベースhatena_bookmarkにアクセスできることを確認してください．"
  exit 1
fi

# RSSファイルから各種URL・タグ情報をDBに登録します．
echo "> RSSファイルからURL・タグ情報をDBに登録します．"
python set_rss_to_db.py
if [ $? -eq 0 ]; then
  echo "> 正常に終了しました. "
else
  echo "> 問題が発生しました．"
  exit 1
fi

# URLから本文情報を取得し，DBに登録します．
echo "> URLから本文情報を取得し，DBに登録します．"
python set_web_content_to_db.py
if [ $? -eq 0 ]; then
  echo "> 正常に終了しました．"
else
  echo "> 問題が発生しました．"
  exit 1
fi

# 本文情報を形態素解析し，TF/IDF(+残差IDF)をdatファイルに書き出します．
echo "> 本文情報を形態素解析し，TF/IDF(+残差IDF)をdatファイルに出力します．"
mkdir ./_tmp
./parse_web_content_to_morpheme.o
if [ $? -eq 0 ]; then
  echo "> 正常に終了しました．"
else
  echo "> 問題が発生しました．"
  exit 1
fi

# datファイルに書きだされた結果をDB(MySQL)に登録します．
# ここから実行再開する場合、以下のMySQLを実行する。
#   set foreign_key_checks = 0;
#   truncate table morpheme;
#   truncate talbe url_morpheme;
#   truncate table stoplist;
#   set foreign_key_checks = 1;
echo "> datファイルをDBに登録します．"
python set_dat_to_db.py
if [ $? -eq 0 ]; then
  echo "> 正常に終了しました．"
else
  echo "> 問題が発生しました．"
  exit 1
fi

# ストップワードをDBに登録します．
# ここから実行再開する場合、以下のMySQLを実行する。
#   truncate table stoplist;
echo "> ストップワード(./data/stoplist.dat)をDBに登録します．"
python set_stoplist_to_db.py
if [ $? -eq 0 ]; then
  echo "> 正常に終了しました．"
else
  echo "> 問題が発生しました．"
  exit 1
fi

echo "complete !!"
