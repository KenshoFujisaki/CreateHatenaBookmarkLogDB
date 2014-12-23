#!/usr/local/bin/python
# -*- encoding: utf-8 -*-

import MySQLdb # sudo pip install MySQL-python
import sys
import pprint
import MeCab # install: http://salinger.github.io/blog/2013/01/17/1/
import re
import unicodedata
from nltk import stem # sudo pip install nltk
# 頻度分布：http://qiita.com/raydive@github/items/80a36a7f40f526441456
from collections import Counter
import pickle

def main_process():
	# オブジェクトの標準出力をインデント化
	pp = pprint.PrettyPrinter(indent=2)
	
	# DBへログイン
	connection = MySQLdb.connect(
		user="hatena", host="localhost", passwd="hatena", db="hatena_bookmark")
	cursor = connection.cursor()

	# 計算結果の辞書データ
	# 後にバイナリファイルとして書き出す．（過去にはMySQLで対応していたが，速度が出ないため変更）
	# 特徴語をDBに登録
	# dic_morpheme = {形態素名: {idf: IDF値, ridf: 残差IDF値}}
	# list_url_morpheme = [{url_id: ID@MySQL-urlテーブル,
	#                       morpheme: 形態素名@dic_morpheme,
	#                       nof_morphemes: TermFrequency値,
	#                       nof_words: URLにおける単語数（形態素数）}]
	dic_morpheme = {}
	list_url_morpheme = []

	# DBからurl_idとcontent（本文）を取得
	cursor.execute('SELECT url_id, content FROM url_content')
	rows = cursor.fetchall()

	# DBから切断
	cursor.close()
	connection.close()

	N = len(rows)
	counter = 0
	for row in rows:
		# 各種情報をキャッシュ
		url_id = row[0]
		content = row[1]
		
		# 処理の進捗を標準出力
		counter += 1
		print "(%s/%s) url_id = %s" % (counter, N, url_id)
	
		# contentを各文について形態素解析し，特徴語を取得
		mecab = MeCab.Tagger("-Ochasen")
		sentences = re.split(
				'[\n\r\.．。\?？！\!]'.decode('utf-8'), 
				content.decode('utf-8'))
		sentences = filter(lambda s: s!="", sentences)
		sentences = map(lambda s: s.encode('utf-8'), sentences)
		keywords = []
		for sentence in sentences:
			node = mecab.parseToNode(sentence)
			while node:
				morpheme = node.surface
				feature = node.feature
				morpheme = normalize(morpheme)

				# 特徴語となる形態素を取得
				if is_feature_morpheme(morpheme, feature):
					keywords.append(morpheme)
				node = node.next

		# 特徴語から頻度分布を取得
		cnt = Counter()
		for keyword in keywords:
			cnt[keyword] += 1
		nof_words = len(keywords)
		nof_vocabularies = len(cnt)
		#sorted_cnt = cnt.most_common()
		#for key_count in sorted_cnt:
		#	print key_count[0], '=', key_count[1]
		print "  特徴語彙数：%s, 特徴語数：%s" % (nof_vocabularies, nof_words)
		
		# 特徴語を辞書に登録
		# dic_morpheme = {形態素名: {idf: IDF値, ridf: 残差IDF値}}
		# list_url_morpheme = [{url_id: ID@MySQL-urlテーブル,
		#                       morpheme: 形態素名@dic_morpheme,
		#                       nof_morphemes: TermFrequency値,
		#                       nof_words: URLにおける単語数（形態素数）}]
		for morpheme, nof_morphemes in cnt.iteritems():
			# dic_morphemeに存在しているか確認.
			# なければキー（morpheme）を追加
			if not dic_morpheme.has_key(morpheme):
				dic_morpheme.update({morpheme: {}})

			# url_morphemeのマッピングをlist_url_morphemeに追加
			list_url_morpheme.append({
					"url_id": url_id,
					"morpheme": morpheme,
					"nof_morphemes": nof_morphemes,
					"nof_words": nof_words})

		# 辞書をバイナリ書き出し
		with open('./dic_morpheme.obj', 'wb') as f:
			pickle.dump(dic_morpheme, f)
		with open('./list_url_morpheme.obj', 'wb') as f:
			pickle.dump(list_url_morpheme, f)

	
# 正規化
# http://blog.khlog.net/2010/09/python-unicodedatanormalize.html
# http://haya14busa.com/python-nltk-natural-language-processing/
def normalize(string):
	# NFKC正規化
	normalized = unicodedata.normalize('NFKC', string.decode('utf-8'))
	# 小文字化
	normalized = normalized.lower()
	# ステミング
	#stemmer = stem.PorterStemmer()
	#normalized = stemmer.stem(normalized)
	# 見出し語化
	#lemmatizer = stem.WordNetLemmatizer()
	#normalized = lemmatizer.lemmatize(normalized)
	return normalized.encode('utf-8')
	
# 特徴語判別
def is_feature_morpheme(morpheme, feature):
	features = feature.split(",")
	if features[0].decode('utf-8')==u"名詞":
		if features[1].decode('utf-8')==u"一般" or \
				features[1].decode('utf-8')==u"固有名詞":
			if len(morpheme) > 1 or \
					re.search(
							'[^0-9あ-んぁ-ぉゃ-ょア-ンァ-ォャ-ョa-z]'.decode('utf-8'), 
							morpheme.decode('utf-8')) != None:
				if morpheme.decode('utf-8')!=u"笑" and morpheme.decode('utf-8')!=u"ー":
					return True
	return False

# メイン関数
if __name__ == '__main__':
	main_process()
