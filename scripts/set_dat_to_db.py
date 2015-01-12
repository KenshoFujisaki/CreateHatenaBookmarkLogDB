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

# _dic_morpheme.dat を morphemeテーブルに登録
# _dic_morpheme.dat: [morpheme morpheme_id, IDF]
print(">> morphemeテーブルへの登録開始")
f = open("./_tmp/_dic_morpheme_morphemeID_IDF.dat", 'rU')
reader = csv.reader(f, delimiter=' ')
for line in reader:
        morpheme = " ".join(line[0:len(line)-2])
        idf = line[-1]
	cursor.execute(
		"INSERT INTO morpheme (id, name, idf, ridf) VALUES (null, %s, %s, null)", 
		[morpheme, idf])
connection.commit()
f.close()
print(">> morphemeテーブルへの登録完了")

# _dic_urlID_morphemeID_TF.dat を url_morphemeテーブルに登録
# _dic_urlID_morphemeID_TF.dat: [url_id, morpheme_id, TF]
print(">> url_morphemeテーブルへの登録開始")
f = open("./_tmp/_dic_urlID_morphemeID_TF.dat", 'rU')
reader = csv.reader(f, delimiter=' ')
for line in reader:
	cursor.execute(
		"INSERT INTO url_morpheme (id, url_id, morpheme_id, morpheme_count) VALUES (null, %s, %s, %s)",
		[line[0], line[1], line[2]])
connection.commit()
f.close()
print(">> url_morphemeテーブルへの登録完了")

# DBから切断
cursor.close()
connection.close()
