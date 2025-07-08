#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VET-Assistant2 高度重複監視システム
数か月の過去投稿との厳重な内容重複チェック
"""

import sqlite3
import hashlib
import re
import json
import os
import difflib
from datetime import datetime, timedelta
from collections import Counter
from typing import List, Dict, Tuple, Optional

class AdvancedDuplicateMonitor:
    def __init__(self, db_path: str = "vet_assistant2_posts.db"):
        self.db_path = db_path
        self.similarity_threshold = 0.65  # 65%以上の類似度で重複と判定
        self.init_database()
        self.load_existing_tweets()
    
    def init_database(self):
        """投稿履歴データベースを初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 投稿履歴テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS post_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                normalized_content TEXT NOT NULL,
                post_type TEXT,
                animal_type TEXT,
                topic TEXT,
                keywords TEXT,
                main_points TEXT,
                char_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source TEXT DEFAULT 'generated'
            )
        ''')
        
        # 重複検出履歴テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS duplicate_detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                attempted_content TEXT NOT NULL,
                similar_post_id INTEGER,
                similarity_score REAL,
                detection_reason TEXT,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (similar_post_id) REFERENCES post_history (id)
            )
        ''')
        
        # インデックス作成
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_hash ON post_history(content_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_animal_type ON post_history(animal_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_topic ON post_history(topic)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON post_history(created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_normalized_content ON post_history(normalized_content)')
        
        conn.commit()
        conn.close()
    
    def load_existing_tweets(self):
        """既存のツイートデータを読み込み"""
        tweets_file = r"C:\Users\souhe\Desktop\X過去投稿\data\tweets.js"
        
        if os.path.exists(tweets_file):
            try:
                with open(tweets_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                json_match = re.search(r'window\.YTD\.tweets\.part0\s*=\s*(\[.*\]);?', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    tweets_data = json.loads(json_str)
                    
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    # 既存データがあるかチェック
                    cursor.execute('SELECT COUNT(*) FROM post_history WHERE source = "archive"')
                    if cursor.fetchone()[0] == 0:
                        # 過去投稿を保存
                        for tweet_obj in tweets_data:
                            if 'tweet' in tweet_obj and 'full_text' in tweet_obj['tweet']:
                                full_text = tweet_obj['tweet']['full_text']
                                
                                # 猫または犬の投稿のみ
                                if '#猫のあれこれ' in full_text or '#獣医が教える犬のはなし' in full_text:
                                    self.save_historical_post(full_text, cursor)
                        
                        conn.commit()
                    
                    conn.close()
                    
            except Exception as e:
                print(f"⚠️ 既存ツイート読み込みエラー: {e}")
    
    def save_historical_post(self, content: str, cursor):
        """過去投稿を履歴に保存"""
        content_hash = self.calculate_content_hash(content)
        normalized_content = self.normalize_content(content)
        keywords = json.dumps(self.extract_keywords(content), ensure_ascii=False)
        main_points = json.dumps(self.extract_main_points(content), ensure_ascii=False)
        
        animal_type = "cat" if '#猫のあれこれ' in content else "dog"
        topic = self.extract_topic(content)
        
        cursor.execute('''
            INSERT OR IGNORE INTO post_history 
            (content, content_hash, normalized_content, animal_type, topic, 
             keywords, main_points, char_count, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (content, content_hash, normalized_content, animal_type, topic,
              keywords, main_points, len(content), 'archive'))
    
    def normalize_content(self, content: str) -> str:
        """投稿内容を正規化"""
        # 改行、空白、絵文字、記号を除去
        normalized = re.sub(r'[\n\r\s]', '', content)
        normalized = re.sub(r'[^\w\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', '', normalized)
        normalized = re.sub(r'#\w+', '', normalized)
        return normalized.lower()
    
    def extract_keywords(self, content: str) -> List[str]:
        """投稿内容からキーワードを抽出"""
        keywords = []
        
        # 疾患・症状パターン
        disease_patterns = [
            r'(腎臓病|腎不全|心臓病|糖尿病|甲状腺|肝臓|膀胱|尿路|結石|感染症|アレルギー)',
            r'(白内障|緑内障|結膜炎|皮膚炎|外耳炎|歯周病|口内炎|関節炎)',
            r'(嘔吐|下痢|便秘|発熱|食欲不振|体重減少|呼吸困難|多飲多尿)',
            r'(血尿|よだれ|口臭|歩行異常|震え|痙攣|意識障害)'
        ]
        
        # 猫種・犬種パターン
        breed_patterns = [
            r'(アメリカンショートヘア|ペルシャ|ロシアンブルー|スコティッシュフォールド|マンチカン)',
            r'(メインクーン|ラグドール|ベンガル|アビシニアン|ブリティッシュ)',
            r'(トイプードル|チワワ|ダックスフント|ポメラニアン|シーズー)',
            r'(ゴールデンレトリーバー|ラブラドール|柴犬|フレンチブルドッグ)'
        ]
        
        # 医療・ケア用語
        medical_patterns = [
            r'(診断|治療|手術|薬|ワクチン|検査|血液検査|レントゲン|エコー|MRI)',
            r'(症状|予防|ケア|管理|観察|対処法|応急処置|健康診断)',
            r'(フード|食事|給餌|水分|栄養|サプリメント|おやつ)',
            r'(トイレ|排尿|排便|グルーミング|ブラッシング|爪切り)'
        ]
        
        all_patterns = disease_patterns + breed_patterns + medical_patterns
        
        for pattern in all_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            keywords.extend(matches)
        
        return list(set(keywords))
    
    def extract_main_points(self, content: str) -> List[str]:
        """主要ポイントを抽出"""
        points = []
        
        # 箇条書きポイント
        bullet_patterns = [
            r'✅\s*([^\n]+)',
            r'💡\s*([^\n]+)',
            r'🐾\s*([^\n]+)',
            r'⚠️\s*([^\n]+)',
            r'🏥\s*([^\n]+)',
            r'①\s*([^\n]+)',
            r'②\s*([^\n]+)',
            r'③\s*([^\n]+)',
            r'④\s*([^\n]+)'
        ]
        
        for pattern in bullet_patterns:
            matches = re.findall(pattern, content)
            points.extend(matches)
        
        # 重要文の抽出
        important_patterns = [
            r'【([^】]+)】',
            r'注意[^\n]*?[。！？]',
            r'重要[^\n]*?[。！？]',
            r'必要[^\n]*?[。！？]',
            r'症状[^\n]*?[。！？]'
        ]
        
        for pattern in important_patterns:
            matches = re.findall(pattern, content)
            points.extend(matches)
        
        return [point.strip() for point in points if point.strip()]
    
    def extract_topic(self, content: str) -> str:
        """トピックを抽出"""
        # 【】内のトピック
        topic_match = re.search(r'【([^】]+)】', content)
        if topic_match:
            return topic_match.group(1)
        
        # 疾患名の抽出
        diseases = [
            '腎臓病', '腎不全', '心臓病', '糖尿病', '甲状腺', '歯周病', '関節炎',
            '尿路結石', '皮膚炎', '外耳炎', '白内障', '緑内障'
        ]
        
        for disease in diseases:
            if disease in content:
                return disease
        
        # 猫種・犬種の抽出
        breeds = [
            'アメリカンショートヘア', 'ペルシャ', 'マンチカン', 'スコティッシュフォールド',
            'トイプードル', 'チワワ', 'ゴールデンレトリーバー', '柴犬'
        ]
        
        for breed in breeds:
            if breed in content:
                return breed
        
        return "一般"
    
    def calculate_content_hash(self, content: str) -> str:
        """コンテンツハッシュ値を計算"""
        normalized = self.normalize_content(content)
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def calculate_similarity(self, content1: str, content2: str) -> float:
        """2つの投稿の類似度を計算"""
        norm1 = self.normalize_content(content1)
        norm2 = self.normalize_content(content2)
        
        if norm1 == norm2:
            return 1.0
        
        # 文字列の類似度
        text_similarity = difflib.SequenceMatcher(None, norm1, norm2).ratio()
        
        # キーワードの類似度
        keywords1 = set(self.extract_keywords(content1))
        keywords2 = set(self.extract_keywords(content2))
        
        if keywords1 or keywords2:
            keyword_similarity = len(keywords1 & keywords2) / len(keywords1 | keywords2)
        else:
            keyword_similarity = 0.0
        
        # 主要ポイントの類似度
        points1 = set(self.extract_main_points(content1))
        points2 = set(self.extract_main_points(content2))
        
        if points1 or points2:
            points_similarity = len(points1 & points2) / len(points1 | points2)
        else:
            points_similarity = 0.0
        
        # 重み付き平均
        final_similarity = (
            text_similarity * 0.4 +
            keyword_similarity * 0.4 +
            points_similarity * 0.2
        )
        
        return final_similarity
    
    def check_duplicate_comprehensive(self, content: str, animal_type: str = None, 
                                    topic: str = None, months_back: int = 6) -> Tuple[bool, List[Dict]]:
        """包括的な重複チェック"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 完全一致チェック
        content_hash = self.calculate_content_hash(content)
        cursor.execute('SELECT * FROM post_history WHERE content_hash = ?', (content_hash,))
        exact_match = cursor.fetchone()
        
        if exact_match:
            duplicate_info = {
                'type': 'exact_match',
                'similarity': 1.0,
                'content': exact_match[1],
                'topic': exact_match[6],
                'created_at': exact_match[10],
                'source': exact_match[11]
            }
            
            # 重複検出記録
            cursor.execute('''
                INSERT INTO duplicate_detections 
                (attempted_content, similar_post_id, similarity_score, detection_reason)
                VALUES (?, ?, ?, ?)
            ''', (content, exact_match[0], 1.0, 'exact_match'))
            
            conn.commit()
            conn.close()
            return True, [duplicate_info]
        
        # 類似度チェック（過去数か月）
        cutoff_date = datetime.now() - timedelta(days=months_back * 30)
        
        # 動物種とトピックでフィルタリング
        where_conditions = ["created_at > ?"]
        params = [cutoff_date.strftime('%Y-%m-%d %H:%M:%S')]
        
        if animal_type:
            where_conditions.append("animal_type = ?")
            params.append(animal_type)
        
        if topic:
            where_conditions.append("topic = ?")
            params.append(topic)
        
        query = f'''
            SELECT * FROM post_history 
            WHERE {' AND '.join(where_conditions)}
            ORDER BY created_at DESC
            LIMIT 200
        '''
        
        cursor.execute(query, params)
        candidate_posts = cursor.fetchall()
        
        duplicates = []
        for post in candidate_posts:
            similarity = self.calculate_similarity(content, post[1])
            
            if similarity >= self.similarity_threshold:
                duplicate_info = {
                    'type': 'similar_content',
                    'similarity': similarity,
                    'content': post[1],
                    'topic': post[6],
                    'created_at': post[10],
                    'source': post[11]
                }
                duplicates.append(duplicate_info)
                
                # 重複検出記録
                cursor.execute('''
                    INSERT INTO duplicate_detections 
                    (attempted_content, similar_post_id, similarity_score, detection_reason)
                    VALUES (?, ?, ?, ?)
                ''', (content, post[0], similarity, 'similar_content'))
        
        # 類似度でソート
        duplicates.sort(key=lambda x: x['similarity'], reverse=True)
        
        conn.commit()
        conn.close()
        
        return len(duplicates) > 0, duplicates
    
    def save_approved_post(self, content: str, animal_type: str = None, 
                          topic: str = None, post_type: str = None) -> bool:
        """承認された投稿を保存"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            content_hash = self.calculate_content_hash(content)
            normalized_content = self.normalize_content(content)
            keywords = json.dumps(self.extract_keywords(content), ensure_ascii=False)
            main_points = json.dumps(self.extract_main_points(content), ensure_ascii=False)
            
            if not topic:
                topic = self.extract_topic(content)
            
            if not animal_type:
                animal_type = "cat" if '#猫のあれこれ' in content else "dog"
            
            cursor.execute('''
                INSERT INTO post_history 
                (content, content_hash, normalized_content, post_type, animal_type, 
                 topic, keywords, main_points, char_count, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (content, content_hash, normalized_content, post_type, animal_type,
                  topic, keywords, main_points, len(content), 'generated'))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ 投稿保存エラー: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """統計情報を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 総投稿数
        cursor.execute('SELECT COUNT(*) FROM post_history')
        total_posts = cursor.fetchone()[0]
        
        # 動物種別
        cursor.execute('SELECT animal_type, COUNT(*) FROM post_history GROUP BY animal_type')
        animal_counts = dict(cursor.fetchall())
        
        # 重複検出数
        cursor.execute('SELECT COUNT(*) FROM duplicate_detections')
        duplicate_detections = cursor.fetchone()[0]
        
        # 最近の投稿数（30日間）
        cursor.execute('''
            SELECT COUNT(*) FROM post_history 
            WHERE created_at > datetime('now', '-30 days')
        ''')
        recent_posts = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_posts': total_posts,
            'animal_counts': animal_counts,
            'duplicate_detections': duplicate_detections,
            'recent_posts': recent_posts
        }
    
    def clean_old_posts(self, days_to_keep: int = 180):
        """古い投稿を削除"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM post_history 
            WHERE created_at < datetime('now', '-{} days')
            AND source = 'generated'
        '''.format(days_to_keep))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted_count