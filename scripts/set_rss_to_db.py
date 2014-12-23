#!/usr/local/bin/python
# -*- encoding: utf-8 -*-

import feedparser
import MySQLdb # sudo pip install MySQL-python
import sys
import pprint

# オブジェクトの標準出力をインデント化
pp = pprint.PrettyPrinter(indent=2)

# DBへログイン
connection = MySQLdb.connect(user="hatena", host="localhost", passwd="hatena", db="hatena_bookmark")
cursor = connection.cursor()

# RSSをパース
feed= feedparser.parse('./data/hatena_bookmark_rss.htm')
for entry in feed.entries:
	
	# 各種情報をキャッシュ
	title = entry.title
	url = entry.link
	print(title)
	if hasattr(entry, "tags"):
		tags = map(lambda elm: elm.term, entry.tags) # ["tag1", "tag2",...]
	update_date = entry.updated[0:10] + " " + entry.updated[12:19]
	
	# urlをDBに登録
	cursor.execute(
			'INSERT INTO url (url, title, update_date) VALUES (%s, %s, %s)',
			[url, title, update_date])

	# tagをDBに登録
	for tag in tags:
		# DBにtagが存在しているか確認
		cursor.execute(
				'SELECT * FROM tag WHERE name = %s',
				[tag])
		rows = cursor.fetchall()
		# DBにtagが存在しないなら追加
		if len(rows) == 0:
			cursor.execute(
					'INSERT INTO tag (name) VALUES (%s)',
					[tag])

	# url_tagのマッピングをDBに登録
	# urlテーブルのidを取得
	cursor.execute(
			'SELECT * FROM url ORDER BY id DESC LIMIT 1')
	url_id = cursor.fetchone()[0]
	# tagテーブルのidを取得
	for tag in tags:
		cursor.execute(
				'SELECT * FROM tag WHERE name = %s',
				[tag])
		tag_id = cursor.fetchone()[0]
		# DBにurl_tagのマッピングを登録
		cursor.execute(
			'INSERT INTO url_tag (url_id, tag_id) VALUES (%s, %s)',
			[url_id, tag_id])

# DBにコミット
connection.commit()

# DBから切断
cursor.close()
connection.close()
