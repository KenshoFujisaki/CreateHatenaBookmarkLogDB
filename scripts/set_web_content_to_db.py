#!/usr/local/bin/python
# -*- encoding: utf-8 -*-

import feedparser
import MySQLdb # sudo pip install MySQL-python
import sys
import pprint
import subprocess
import os
import re
import codecs
reload(sys)
sys.setdefaultencoding('utf-8')
sys.stdout = codecs.getwriter('utf_8')(sys.stdout)
sys.stdin = codecs.getreader('utf_8')(sys.stdin)

# オブジェクトの標準出力をインデント化
pp = pprint.PrettyPrinter(indent=2)

# DBへログイン
connection = MySQLdb.connect(user="hatena", host="localhost", passwd="hatena", db="hatena_bookmark")
cursor = connection.cursor()

# DBからurlを取得
cursor.execute('SELECT * FROM url')
rows = cursor.fetchall()
N = len(rows)
counter = 0
for row in rows:
	# 各種情報をキャッシュ
	url_id = row[0]
	url = row[1]
	title = row[2]

	# 処理の進捗を標準出力
	counter += 1
	print "(%s/%s) %s" % (counter, N, title)

	# 各種ファイルに応じて本文抽出処理
	root, ext = os.path.splitext(url)
	content = ""
	proc = None
	if ext==".pdf": # PDFから本文取得
		
		# PDFダウンロード
		proc = subprocess.Popen(
				["wget", url, "-O", "./_tmp.pdf"],
				shell = False,
				stdin = subprocess.PIPE,
				stdout = subprocess.PIPE,
				stderr = subprocess.PIPE)
		proc.wait()
		
		# PDF本文抽出
		proc = subprocess.Popen(
				["pdftotext", "./_tmp.pdf" , "-"],
				shell = False,
				stdin = subprocess.PIPE,
				stdout = subprocess.PIPE,
				stderr = subprocess.PIPE)
		content = "".join(proc.stdout.readlines())
		proc.wait()

		# PDF削除
		subprocess.call("rm ./_tmp.pdf", shell = True)

	else: # URLから本文取得
		proc = subprocess.Popen(
				["ruby", "scrape_webpage.rb", url],
				shell = False,
				stdin = subprocess.PIPE,
				stdout = subprocess.PIPE,
				stderr = subprocess.PIPE)
	
		# Webページ本文
		content = "".join(proc.stdout.readlines())

	# エラーは標準出力
	scrape_err_msg = proc.stderr.readlines()
	if len(scrape_err_msg) != 0:
		pp.pprint(scrape_err_msg)
		continue

	# タイトルを先頭に追加
	content = title + "\n" + content

	# DBに登録
	print "  %s 文字" % (len(content))
	cursor.execute(
		"INSERT INTO url_content (url_id, content) VALUES (%s, %s)",
		(url_id, content))

	# DBにコミット
	connection.commit()

# DBから切断
cursor.close()
connection.close()
