#!/usr/local/bin/python
# -*- encoding: utf-8 -*-

import MySQLdb # sudo pip install MySQL-python
import sys
import pprint
import math
import csv

# オブジェクトの標準出力をインデント化
pp = pprint.PrettyPrinter(indent=2)
  
# DBへログイン
connection = MySQLdb.connect(user="hatena", host="localhost", passwd="hatena", db="hatena_bookmark", charset='utf8')
cursor = connection.cursor()

# テーブル存在の確認
cursor.execute("SHOW TABLES FROM hatena_bookmark like 'stoplist'")
if(cursor.fetchone() == None):
    cursor.execute("CREATE TABLE stoplist (id int(11) NOT NULL AUTO_INCREMENT, name varchar(128) NOT NULL, morpheme_id int(11), PRIMARY KEY (id))")

# 既存データの削除
print(">> stoplistテーブルのデータをtruncate（削除）します．")
cursor.execute("TRUNCATE TABLE stoplist");

# _dic_stoplist.dat を morphemeテーブルに登録
# _dic_stoplist.dat: [morpheme]
print(">> ./data/stoplist.datの各形態素について，morpheme_idを取得します．")
stopmorpheme_morphemeId = []
f = open("./data/stoplist.dat", 'rU')
reader = csv.reader(f, delimiter=' ')
for line in reader:
  stopmorpheme = line[0]
  cursor.execute(
    "SELECT id FROM morpheme WHERE name = %s", 
    [stopmorpheme])
  res = cursor.fetchone()
  morpheme_id = -1
  if isinstance(res, tuple):
    morpheme_id = res[0]
  print(stopmorpheme + '\t' + str(morpheme_id))
  stopmorpheme_morphemeId += [[stopmorpheme, morpheme_id]]
f.close()

print(">> stoplistテーブルに登録します．")
for line in stopmorpheme_morphemeId:
  print line
  if line[1] != -1:
    cursor.execute(
      "INSERT INTO stoplist (id, name, morpheme_id) VALUES (null, %s, %s)", 
      [line[0], line[1]])
  else:
    cursor.execute(
      "INSERT INTO stoplist (id, name, morpheme_id) VALUES (null, %s, null)",
      [line[0]])
connection.commit()

# DBから切断
cursor.close()
connection.close()

print(">> stoplistテーブルに登録が完了しました．")
