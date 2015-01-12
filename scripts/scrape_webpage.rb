# -*- encoding: utf-8 -*-
# 引数のURLの本文を抽出します．
# example:
# ruby webpage_scrape.rb http://labs.cybozu.co.jp/blog/nakatani/2007/09/web_1.html

require "open-uri"
require "./extractcontent.rb"

if ARGV.length != 1
	puts "Usage: ruby __FILE__ [URL]"
	exit
end

# 第一引数のURLについて処理
URL = ARGV[0]

# 文字コードを取得
charset = URI.parse(URL).read.charset.to_s.downcase

# iso-8859-1/何もなしの場合は，誤認識の可能性が高いので，他の文字コードとして処理
if charset == "iso-8859-1" || charset == ""
	# 各文字コードの候補に対して本文抽出（各文字コードを試して，例外がでなければそれを標準出力）
	charset_list = ["rb:utf-8", "rb:Shift_JIS", "rb:eucJP"]
	charset_list.each do |charset_est|
		open(URL, charset_est) do |io|
			begin
				html = io.read.encode("UTF-8")
				body, title = ExtractContent.analyse(html)
				puts body
			rescue
				next
			end
		end
	end
else
	# charsetから，open-uriにおける文字コードに換言
	charset_hash = {
		"euc-jp" => "rb:eucJP",
		"shift_jis" => "rb:Shift_JIS",
		"shift-jis" => "rb:Shift_JIS",
		"utf-8"	=> "rb:utf-8"}
	if charset_hash.has_key?(charset)
		charset_est = charset_hash[charset]

		# 本文抽出
		open(URL, charset_est) do |io|
			html = io.read
			# ExtractContentがUTF-8しか受け付けないのでエンコード．
			# ただし，普通に.encode("UTF-8")するとinvalid なバイト列が…と起こられるので，
			# http://d.hatena.ne.jp/yarb/20110112/p1 に従って一旦UTF-16BEに変換の後にUTF-8に変換．
			html = html.encode("UTF-16BE", :invalid => :replace, :undef => :replace, :replace => '?').encode("UTF-8")
			body, title = ExtractContent.analyse(html)
			puts body
		end
	else
		# 本文抽出
		open(URL) do |io|
			html = io.read
			# ExtractContentがUTF-8しか受け付けないのでエンコード．
			# ただし，普通に.encode("UTF-8")するとinvalid なバイト列が…と起こられるので，
			# http://d.hatena.ne.jp/yarb/20110112/p1 に従って一旦UTF-16BEに変換の後にUTF-8に変換．
			html = html.encode("UTF-16BE", :invalid => :replace, :undef => :replace, :replace => '?').encode("UTF-8")
			body, title = ExtractContent.analyse(html)
			puts body
		end
	end
end
