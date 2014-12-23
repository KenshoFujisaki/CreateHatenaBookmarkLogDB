#include <mysql.h>
#include <stdio.h>
#include <mecab.h>
#include <iostream>
#include <vector>
#include <string.h>
#include <map>
#include <stdlib.h>
#include <fstream>
#include <time.h>
#include <omp.h>
#include <ctype.h>

#define MAX_SENTENCE_ITEM 8192
#define MAX_SENTENCE_LEN 2048
#define MAX_MORPHEME_ITEM 32768
#define MAX_CONTENT_LEN 262144

typedef struct url_morpheme {
  int url_id;
  std::string morpheme;
  int term_freq;
} url_morpheme;

/**
 * 文字列長の取得
 */
int string_length(const char *s) {
  int n = 0;
  while (*s++ != '\0') {
    n++;
  }
  return n;
}

/**
 * 文章の文分解
 */
int split(char *str, const char *delim, char **outlist) {
  char    *tk;
  int     cnt = 0;
  tk = strtok( str, delim );
  while( tk != NULL && cnt < MAX_SENTENCE_ITEM) {
    outlist[cnt] = tk;
    cnt++;
    tk = strtok( NULL, delim );
  }
  return cnt;
}

/**
 * 文字列の小文字化
 */
int lower_normalize(char *str) {
  int len = string_length(str);
  for (int i=0; i<len; i++) {
    str[i] = tolower(str[i]);
  }
}

/**
 * 形態素解析する関数
 */
int morphemize(char *content, char **morpheme_list) 
{  
  /* 文章の文分解 */
  char **sentences = new char*[MAX_SENTENCE_ITEM];
  int nof_sentences = split(content, ".!?\n\r", sentences);
  int morpheme_counter = 0;

  /* 各文について形態素解析 */
#pragma omp parallel for num_threads(8)
  for(int i=0; i<nof_sentences; i++) {
    
    /* MeCab */
    MeCab::Tagger *tagger = MeCab::createTagger("-Ochasen");
    const MeCab::Node *node = tagger->parseToNode(sentences[i]);
    while (node) {
      
      // 形態素取得
      char* surface = new char[node->length+1];
      strncpy(surface, node->surface, node->length);
      surface[node->length] = '\0';

      // 品詞取得
      char **features = new char*[/*詳細情報の数*/12];
      char *feature = new char[/*詳細情報の文字列長*/256];
      strcpy(feature, node->feature);
#pragma omp critical
      {
        int nof_features = split(feature, ",", features);
      }
      
      // 品詞選択
      if (strcmp(features[0], "名詞")==0) {
        if(strcmp(features[1], "一般")==0 || strcmp(features[1], "固有名詞")==0) {
          if (strlen(surface) > 2) {
            // 返却値に登録
#pragma omp critical
            {
              // 大文字小文字正規化
              lower_normalize(surface);
              morpheme_list[morpheme_counter++] = surface;
            }
          }
        }
      }
      node = node->next;
      delete feature;
      delete[] features;
    }
    delete tagger;
  }
  delete[] sentences;
  return morpheme_counter;
}


/**
 * メイン関数
 */
int main(void)
{
  // 処理時間計測
  clock_t t1, t2;
  t1 = clock();
  
  // MySQL設定
  MYSQL *db_connection;
  MYSQL_RES *db_result;
  MYSQL_ROW db_row;
  char *server = (char*)"localhost";
  char *user = (char*)"hatena";
  char *password = (char*)"hatena";
  char *database = (char*)"hatena_bookmark";
  
  /* MySQL接続 */
  db_connection = mysql_init(NULL);
  if (!mysql_real_connect(
        db_connection, server, user, password, database, 0, NULL, 0)) {
    fprintf(stderr, "%s\n", mysql_error(db_connection));
    return 1;
  }
  
  /* MySQLクエリ */
  if (mysql_query(
        db_connection, "SELECT url_id,content FROM url_content")) {
    fprintf(stderr, "%s\n", mysql_error(db_connection));
    return 1;
  }
  db_result = mysql_use_result(db_connection);

  /* 生成する辞書 */
  // dic_morpheme = {形態素名: IDF}
  // dic_url = {url_id: 特徴語数}
  // vec_url_morpheme = [url_morpheme]
  //   url_morpheme = {url_id, morpheme, TF}
  std::map<std::string, int> dic_morpheme;
  std::map<int, int> dic_url;
  std::vector<url_morpheme> vec_url_morpheme;
  std::vector<url_morpheme>::iterator um_it;
  
  /* MySQLの各レコードについて処理 */
  int row_counter = 0;
  while ((db_row = mysql_fetch_row(db_result)) != NULL) {
    // 各種情報をキャッシュ
    int url_id = atoi(db_row[0]);
    char* content = db_row[1];

    // 進捗状況を標準出力
    printf("(%d) url_id:%05d\t", ++row_counter, url_id);    
    
    // 形態素解析（特徴語抽出）
    char **morpheme_list = new char*[MAX_MORPHEME_ITEM];
    int morpheme_counter = morphemize(content, morpheme_list);
    int nof_words = morpheme_counter;
    printf("#words:%06d\t", nof_words);

    // 特徴語の頻度分布
    std::map<std::string, int> freq_morpheme;
    for (int i=0; i<morpheme_counter; i++) {
      //int morpheme_len = string_length(morpheme_list[i]);
      // char *morpheme = new char[morpheme_len + 1];
      // strcpy(morpheme, morpheme_list[i]);
      std::string keyword = std::string(morpheme_list[i]);
      if (freq_morpheme.find(keyword)!=freq_morpheme.end()) {
        // 特徴語が既に存在するならインクリメント
        freq_morpheme[keyword] += 1;
      }
      else {
        // 存在しないなら追加
        freq_morpheme[keyword] = 1;
      }
    }
    int nof_keywords = freq_morpheme.size();
    printf("#morphemes:%05d\n", nof_keywords);

    // 辞書登録
    std::map<std::string, int>::iterator fm_it = freq_morpheme.begin();
    for(; fm_it!=freq_morpheme.end(); ++fm_it) {
      std::string keyword = (*fm_it).first;
      int term_freq = (*fm_it).second;

      // dic_morphemeに存在しないなら特徴語を追加
      // ただし，IDF値は暫定的に-1にしておく
      // dic_morpheme = {形態素名: IDF}
      if (dic_morpheme.find(keyword)==dic_morpheme.end()) {
        dic_morpheme[keyword] = -1;
      }

      // vec_url_morphemeに追加
      // vec_url_morpheme = [url_morpheme]
      //   url_morpheme = {url_id, morpheme, term_freq}
      struct url_morpheme um = { url_id, keyword, term_freq };
      vec_url_morpheme.push_back(um);
    }

    // 辞書登録
    // dic_urlに追加
    // dic_url = {url_id: 特徴語数}
    dic_url[url_id] = nof_words;

    // 後処理
    delete[] morpheme_list;
  }

  /* MySQL接続切断 */
  mysql_free_result(db_result);
  mysql_close(db_connection);

  /* IDF・検索語重み付けを計算 */
  // 各morphemeについて計算
  int nof_keywords = dic_morpheme.size();
  std::map<std::string, int>::iterator m_it;
  std::vector<std::string> dic_morpheme_mapping;
  dic_morpheme_mapping.reserve(nof_keywords);
  int morpheme_counter = 0;
  
  // dictを並列化するための準備（イテレータをomp parallel forできないので）
  int tmp=0;
  for(m_it = dic_morpheme.begin(); m_it!=dic_morpheme.end(); m_it++) {
    dic_morpheme_mapping.push_back((*m_it).first);
  }

  // 並列化
#pragma omp parallel for num_threads(12)
  for(int i=0; i<nof_keywords; i++) {
    std::string morpheme = dic_morpheme_mapping[i];
    
    // morphemeが存在するURL数を計算
    // vec_url_morpheme = [{url_id, morpheme, term_freq}]
    int idf_counter = 0;
    std::vector<url_morpheme>::iterator _um_it = vec_url_morpheme.begin();
    while( _um_it != vec_url_morpheme.end() ) {
      if ((*_um_it).morpheme == morpheme) {
        idf_counter++;
      }
      ++_um_it;
    }
    
#pragma omp critical
    {    
      // IDF値を辞書に登録
      dic_morpheme[morpheme] = idf_counter;
      
      // 進捗状況を標準出力
      printf("(%d/%d) %s\tIDF%d\n",
             ++morpheme_counter, nof_keywords, morpheme.c_str(), idf_counter);
    }
  }
  
  /* 各種辞書をファイル書き出し */
  // dic_morpheme
  // MySQLにおけるmorphemeテーブルに対応
  std::map<std::string, int> dic_morpheme_id;
  std::ofstream out_dic_morpheme;
  out_dic_morpheme.open("./_tmp/_dic_morpheme_morphemeID_IDF.dat");
  m_it = dic_morpheme.begin();
  int morpheme_id_counter = 1;
  while( m_it != dic_morpheme.end() ) {
    std::string morpheme = (*m_it).first;
    int idf = (*m_it).second;
    out_dic_morpheme << morpheme.c_str() << " "
                     << morpheme_id_counter << " "
                     << idf << std::endl;
    // morpheme_idを記憶（morpheme -> morpheme_id へのmapping）
    dic_morpheme_id[morpheme.c_str()] = morpheme_id_counter++;
    ++m_it;
  }
  out_dic_morpheme.close();

  // dic_url
  std::ofstream out_dic_url;
  out_dic_url.open("./_tmp/_dic_url_nofWords.dat");
  std::map<int, int>::iterator u_it = dic_url.begin();
  while( u_it != dic_url.end() ) {
    int url_id = (*u_it).first;
    int nof_words = (*u_it).second;
    out_dic_url << url_id << " " << nof_words << std::endl;
    ++u_it;
  }
  out_dic_url.close();

  // vec_url_morpheme = [{url_id, morpheme, term_freq}]
  // _vec_url_morpheme: [{url_id, morpheme_id, term_freq}]
  std::ofstream out_vec_url_morpheme;
  out_vec_url_morpheme.open("./_tmp/_dic_urlID_morphemeID_TF.dat");
  um_it = vec_url_morpheme.begin();
  while( um_it != vec_url_morpheme.end() ) {
    out_vec_url_morpheme << (*um_it).url_id << " "
                         << dic_morpheme_id[(*um_it).morpheme.c_str()] << " "
                         << (*um_it).term_freq << std::endl;
    ++um_it;
  }
  out_vec_url_morpheme.close();

  // 処理終了
  std::cout << "処理が正常に終了しました．" << std::endl;
  t2 = clock();
  std::cout << "特徴語抽出の処理時間: "
            << (double)(t2 - t1) /CLOCKS_PER_SEC
            << "秒" << std::endl;
}
