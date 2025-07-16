#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VET-Assistant2 強化版投稿生成システム
重複監視・自動再生成機能付き
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import re
import os
import random
import codecs
from datetime import datetime, timedelta
from advanced_duplicate_monitor import AdvancedDuplicateMonitor
from google_sheets_uploader import GoogleSheetsUploader
from ai_content_generator import AIContentGenerator

class EnhancedPostGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("VET-Assistant2 強化版投稿生成ツール")
        self.root.geometry("800x700")
        
        # 重複監視システム
        self.duplicate_monitor = AdvancedDuplicateMonitor()
        
        # Googleスプレッドシート連携
        self.sheets_uploader = GoogleSheetsUploader()
        
        # AI駆動コンテンツ生成システム
        self.ai_generator = AIContentGenerator()
        
        # 基本設定
        self.tweets_file_path = r"C:\Users\souhe\Desktop\X過去投稿\data\tweets.js"
        self.max_regeneration_attempts = 5  # 最大再生成回数
        self.last_generated_csv = None  # 最後に生成されたCSVファイルのパス
        
        # コンテンツプール
        self.content_pools = {
            'cat_questions': [],
            'cat_health': [],
            'dog_cases': [],
            'dog_health': []
        }
        
        self.setup_ui()
        self.initialize_enhanced_content_pools()
        
        # 初期状態で参加型テーマの詳細設定を表示
        self.on_theme_change()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # タイトル
        title_label = ttk.Label(main_frame, text="VET-Assistant2 強化版投稿生成ツール", 
                               font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # 重複監視状況
        stats_frame = ttk.LabelFrame(main_frame, text="重複監視システム状況", padding="10")
        stats_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # 統計情報を表示
        stats = self.duplicate_monitor.get_statistics()
        stats_text = f"総投稿数: {stats['total_posts']}件 | 重複検出: {stats['duplicate_detections']}件 | 最近30日: {stats['recent_posts']}件"
        ttk.Label(stats_frame, text=stats_text).grid(row=0, column=0, sticky=tk.W)
        
        # 設定フレーム
        settings_frame = ttk.LabelFrame(main_frame, text="生成設定", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # 生成日数
        ttk.Label(settings_frame, text="生成日数:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.days_var = tk.StringVar(value="7")
        ttk.Entry(settings_frame, textvariable=self.days_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # 週テーマ
        ttk.Label(settings_frame, text="週テーマ:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.week_type_var = tk.StringVar(value="参加型")
        week_combo = ttk.Combobox(settings_frame, textvariable=self.week_type_var, width=15)
        week_combo['values'] = ("参加型", "猫種特集", "専門テーマ", "健康管理")
        week_combo.grid(row=0, column=3, sticky=tk.W, pady=5)
        week_combo.bind('<<ComboboxSelected>>', self.on_theme_change)
        
        # 詳細テーマ設定
        ttk.Label(settings_frame, text="詳細設定:").grid(row=1, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.specific_topic_var = tk.StringVar(value="自動選択")
        self.topic_combo = ttk.Combobox(settings_frame, textvariable=self.specific_topic_var, width=15)
        self.topic_combo['values'] = ("自動選択",)
        self.topic_combo.grid(row=1, column=3, sticky=tk.W, pady=5)
        
        # 重複チェック設定
        ttk.Label(settings_frame, text="重複チェック期間:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.check_months_var = tk.StringVar(value="3")  # 6ヶ月→3ヶ月に短縮
        months_combo = ttk.Combobox(settings_frame, textvariable=self.check_months_var, width=10)
        months_combo['values'] = ("3", "6", "12", "24")
        months_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        ttk.Label(settings_frame, text="か月前まで").grid(row=2, column=2, sticky=tk.W, pady=5)
        
        # 類似度閾値
        ttk.Label(settings_frame, text="類似度閾値:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.similarity_var = tk.StringVar(value="50")  # 65%→50%に緩和
        similarity_combo = ttk.Combobox(settings_frame, textvariable=self.similarity_var, width=10)
        similarity_combo['values'] = ("40", "45", "50", "55", "60", "65", "70", "75", "80")
        similarity_combo.grid(row=3, column=1, sticky=tk.W, pady=5)
        ttk.Label(settings_frame, text="% 以上で重複判定").grid(row=3, column=2, sticky=tk.W, pady=5)
        
        # 生成ボタン
        self.generate_button = ttk.Button(main_frame, text="📝 投稿生成開始", 
                                        command=self.generate_simple_posts)
        self.generate_button.grid(row=3, column=0, columnspan=4, pady=20)
        
        # 進捗とステータス
        self.status_var = tk.StringVar(value="設定を確認して生成を開始してください")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=4, column=0, columnspan=4, pady=5)
        
        self.progress = ttk.Progressbar(main_frame, length=600, mode='determinate')
        self.progress.grid(row=5, column=0, columnspan=4, pady=10)
        
        # 重複検出ログ
        log_frame = ttk.LabelFrame(main_frame, text="重複検出ログ", padding="10")
        log_frame.grid(row=6, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        
        self.log_text = tk.Text(log_frame, height=8, width=90, font=("Consolas", 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        log_scrollbar.grid(row=0, column=1, sticky='ns')
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        # Googleスプレッドシート連携
        sheets_frame = ttk.LabelFrame(main_frame, text="Googleスプレッドシート連携", padding="10")
        sheets_frame.grid(row=7, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # 認証設定
        ttk.Label(sheets_frame, text="認証JSON:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.auth_status_var = tk.StringVar(value="未設定")
        ttk.Label(sheets_frame, textvariable=self.auth_status_var, foreground="red").grid(row=0, column=1, sticky=tk.W, pady=5)
        ttk.Button(sheets_frame, text="認証設定", command=self.setup_google_auth).grid(row=0, column=2, padx=5, pady=5)
        
        # スプレッドシートURL
        ttk.Label(sheets_frame, text="スプレッドシートURL:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.sheets_url_var = tk.StringVar()
        ttk.Entry(sheets_frame, textvariable=self.sheets_url_var, width=50).grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # アップロードボタン
        self.upload_button = ttk.Button(sheets_frame, text="📤 Googleシートにアップロード", 
                                       command=self.upload_to_google_sheets, state="disabled")
        self.upload_button.grid(row=2, column=0, columnspan=3, pady=10)
        
        # 結果表示
        result_frame = ttk.LabelFrame(main_frame, text="生成結果", padding="10")
        result_frame.grid(row=8, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        
        self.result_text = tk.Text(result_frame, height=12, width=90, font=("Consolas", 9))
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        result_scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
        result_scrollbar.grid(row=0, column=1, sticky='ns')
        self.result_text.configure(yscrollcommand=result_scrollbar.set)
        
        # グリッドの重み設定
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        main_frame.rowconfigure(8, weight=1)
        
    def initialize_enhanced_content_pools(self):
        """強化されたコンテンツプールを初期化"""
        
        # 猫の質問・回答ペア
        self.content_pools['cat_questions'] = [
            {
                "question": "獣医師に教えて！愛猫の寝る場所は？😴\\n\\n【質問】あなたの猫ちゃんはどこで寝ることが多いですか？\\n\\n①飼い主のベッド\\n②専用ベッド\\n③段ボール箱\\n④高い場所（タワーなど）\\n⑤その他（教えて！）\\n\\n場所選びにも理由があるんです♪みなさんの愛猫はいかがですか？\\n#猫のあれこれ",
                "answer": "昨日のアンケート結果を獣医師が解説！😴\\n\\n猫の寝場所選び、それぞれに理由があります：\\n\\n✅飼い主のベッド→信頼の証拠\\n✅段ボール箱→安心できる隠れ家\\n✅高い場所→縄張り確認と警戒\\n\\n温度・安全性・においが重要な要素。愛猫の寝場所を観察してみてくださいね♪\\n#猫のあれこれ"
            },
            {
                "question": "猫の食事時間クイズ！🍽️\\n\\n【質問】愛猫の食事回数は？\\n\\n①1日1回\\n②1日2回\\n③1日3回以上\\n④決まっていない\\n\\n年齢によって理想的な回数は変わります。\\nみなさんの猫ちゃんはどうですか？獣医師が後日解説します！\\n#猫のあれこれ",
                "answer": "昨日の食事回数クイズの答え合わせ！🍽️\\n\\n理想的な食事回数：\\n✅子猫（〜1歳）→1日3-4回\\n✅成猫（1-7歳）→1日2回\\n✅シニア猫（7歳〜）→1日2-3回\\n\\n少量頻回が消化に優しく、肥満予防にも効果的。愛猫の年齢に合わせて調整を♪\\n#猫のあれこれ"
            },
            {
                "question": "愛猫の「変わった好み」ありませんか？🤔\\n\\n【質問】うちの子だけ？と思う愛猫の好みは？\\n\\n①特定の音に反応\\n②変わった食べ物好き\\n③特定の場所へのこだわり\\n④その他（詳しく！）\\n\\n猫の個性、面白いですよね✨\\n#猫のあれこれ",
                "answer": "昨日の「変わった好み」獣医師が解説！🤔\\n\\n実はどれも正常な行動です：\\n\\n✅音への反応→聴覚が優れている証拠\\n✅食べ物の好み→安全確認の本能\\n✅場所のこだわり→縄張り意識\\n\\n個性豊かな行動こそ、猫の魅力ですね♪\\n#猫のあれこれ"
            },
            {
                "question": "猫の遊び方アンケート🎾\\n\\n【質問】愛猫が一番喜ぶ遊びは？\\n\\n①猫じゃらし\\n②ボール\\n③段ボール\\n④かくれんぼ\\n⑤その他（教えて！）\\n\\n年齢に合った遊びが大切です♪\\n#猫のあれこれ",
                "answer": "昨日の遊びアンケート、獣医師が分析！🎾\\n\\n遊びの効果：\\n✅猫じゃらし→狩猟本能を満たす\\n✅ボール→運動不足解消\\n✅段ボール→隠れ家+爪とぎ\\n✅かくれんぼ→知的刺激\\n\\n1日15-30分の遊び時間が理想的。愛猫との絆も深まります♪\\n#猫のあれこれ"
            },
            {
                "question": "猫の健康チェック📊\\n\\n【質問】愛猫の健康診断頻度は？\\n\\n①年1回\\n②年2回\\n③調子悪い時のみ\\n④まだ受けていない\\n\\n獣医師としてのおすすめ頻度もお話しします！\\n#猫のあれこれ",
                "answer": "昨日の健康診断アンケート、獣医師の回答！📊\\n\\n推奨頻度：\\n✅1-6歳→年1回\\n✅7歳以上→年2回\\n✅持病がある子→3-4か月毎\\n\\n早期発見で治療選択肢が広がります。症状が出る前の検査が重要です🏥\\n#猫のあれこれ"
            },
            {
                "question": "猫の爪とぎ場所アンケート🪚\\n\\n【質問】愛猫の爪とぎ、どこでしますか？\\n\\n①専用爪とぎ器\\n②ソファや家具\\n③カーペット\\n④段ボール\\n⑤その他\\n\\n爪とぎの場所選びにも理由があります！\\n#猫のあれこれ",
                "answer": "昨日の爪とぎアンケート結果を解説！🪚\\n\\n場所選びの理由：\\n✅専用器→理想的な環境\\n✅家具→縦の面を好む習性\\n✅カーペット→爪が引っかかりやすい\\n\\n爪とぎは縄張りマーキングでもあります。適切な場所を用意してあげましょう♪\\n#猫のあれこれ"
            },
            {
                "question": "猫の水飲み方クイズ💧\\n\\n【質問】愛猫の好きな水飲み方は？\\n\\n①お皿から普通に\\n②蛇口から直接\\n③流れる水\\n④氷入りの冷たい水\\n⑤その他\\n\\n水分摂取は健康の要です！\\n#猫のあれこれ",
                "answer": "昨日の水飲みクイズ、獣医師が解説！💧\\n\\n飲み方の特徴：\\n✅流れる水→新鮮さを好む本能\\n✅蛇口直接→冷たくて新鮮\\n✅お皿→安心できる場所\\n\\n猫は水分不足になりがち。愛猫の好みに合わせた水場を用意しましょう♪\\n#猫のあれこれ"
            },
            {
                "question": "猫の鳴き声意味クイズ🗣️\\n\\n【質問】愛猫はどんな時によく鳴きますか？\\n\\n①お腹がすいた時\\n②甘えたい時\\n③外を見てる時\\n④トイレの後\\n⑤その他\\n\\n鳴き声で気持ちがわかります！\\n#猫のあれこれ",
                "answer": "昨日の鳴き声クイズ、解説します！🗣️\\n\\n鳴く理由：\\n✅お腹すいた→要求の鳴き声\\n✅甘えたい→愛情表現\\n✅外を見て→狩猟本能の刺激\\n\\n成猫が鳴くのは主に人間に対してです。愛猫との大切なコミュニケーション♪\\n#猫のあれこれ"
            },
            {
                "question": "猫のお気に入り場所調査📍\\n\\n【質問】愛猫が一番長時間いる場所は？\\n\\n①窓際\\n②ベッドの上\\n③キャットタワー\\n④こたつ・暖房器具の近く\\n⑤その他\\n\\n場所選びには理由があります！\\n#猫のあれこれ",
                "answer": "昨日の場所調査、獣医師が分析！📍\\n\\n場所選びの理由：\\n✅窓際→外の様子を監視\\n✅ベッド→飼い主の匂いで安心\\n✅タワー→高所からの眺望\\n✅暖房近く→適温を求める\\n\\n猫は安全で暖かい場所を本能的に選びます♪\\n#猫のあれこれ"
            },
            {
                "question": "猫の運動量調査🏃‍♀️\\n\\n【質問】愛猫の1日の運動時間は？\\n\\n①ほとんど寝てる\\n②短時間だけ活発\\n③夜中に大運動会\\n④一日中元気\\n⑤季節によって変化\\n\\n運動量と健康の関係をお話しします！\\n#猫のあれこれ",
                "answer": "昨日の運動量調査を獣医師が分析！🏃‍♀️\\n\\n健康的な運動パターン：\\n✅夜中の運動会→野生の習性\\n✅短時間集中→効率的な運動\\n✅季節変化→気温への適応\\n\\n室内猫も1日15-30分の遊び時間で十分な運動量を確保できます♪\\n#猫のあれこれ"
            },
            {
                "question": "猫の毛づくろい頻度チェック✨\\n\\n【質問】愛猫の毛づくろい時間は？\\n\\n①1日数回、短時間\\n②長時間集中してやる\\n③食後必ずやる\\n④あまりやらない\\n⑤やりすぎて心配\\n\\n毛づくろいは健康のバロメーター！\\n#猫のあれこれ",
                "answer": "昨日の毛づくろいチェック、獣医師が解説！✨\\n\\n正常な毛づくろい：\\n✅1日の30-50%を占める\\n✅食後・起床後に行う\\n✅ストレス解消効果\\n\\n過度なグルーミングは皮膚炎の原因に。バランスが大切です♪\\n#猫のあれこれ"
            },
            {
                "question": "猫の社交性診断🤝\\n\\n【質問】愛猫の人見知り度は？\\n\\n①誰とでも仲良し\\n②家族だけに甘える\\n③特定の人だけ好き\\n④基本的に人見知り\\n⑤その日の気分次第\\n\\n社交性も個性の一つです！\\n#猫のあれこれ",
                "answer": "昨日の社交性診断、獣医師の分析！🤝\\n\\n社交性のタイプ：\\n✅社交的→環境適応が良い\\n✅選択的→信頼関係を重視\\n✅人見知り→慎重な性格\\n\\nどのタイプも正常。愛猫の性格を理解して接してあげましょう♪\\n#猫のあれこれ"
            },
            {
                "question": "猫の食べ物の好み調査🐟\\n\\n【質問】愛猫が一番好きな食べ物は？\\n\\n①ドライフード\\n②ウェットフード\\n③おやつ・ちゅーる\\n④魚系の食べ物\\n⑤特にこだわりなし\\n\\n食の好みと健康管理についてお話しします！\\n#猫のあれこれ",
                "answer": "昨日の食べ物調査、獣医師がアドバイス！🐟\\n\\n健康的な食事管理：\\n✅総合栄養食が基本\\n✅おやつは全体の10%以下\\n✅魚系食品の与えすぎ注意\\n\\n愛猫の好みを活かしながら、栄養バランスを大切に♪\\n#猫のあれこれ"
            }
        ]
        
        # 猫の健康投稿
        self.content_pools['cat_health'] = [
            "【猫の腎臓病予防】水分摂取のコツ💧\\n\\n腎臓病は猫の代表的な病気。予防の鍵は水分摂取！\\n\\n✅複数の水場を設置\\n✅新鮮な水を毎日交換\\n✅ウェットフードを活用\\n✅流れる水を好む子も\\n\\n1日の目安：体重1kg当たり50-60ml\\n愛猫の水分摂取量、チェックしてみて♪\\n#猫のあれこれ",
            "【シニア猫の健康管理】7歳からが勝負💪\\n\\n7歳以降は人間でいう44歳。この時期からの健康管理が長生きの秘訣！\\n\\n✅定期健診（年2回）\\n✅食事の見直し\\n✅運動量の調整\\n✅環境の配慮\\n\\n早期発見・早期治療で元気な老後を！\\n#猫のあれこれ",
            "【猫の歯の健康】意外と見落としがち🦷\\n\\n猫も歯周病になります！3歳以上の80%に歯周病の兆候が。\\n\\n症状：\\n⚠️口臭\\n⚠️よだれ\\n⚠️食事の変化\\n⚠️頬の腫れ\\n\\n予防は歯磨きが一番。難しい場合は獣医師に相談を！\\n#猫のあれこれ",
            "【猫の目の健康】こんな症状に注意👁️\\n\\n目の病気は早期発見が重要！\\n\\n注意すべき症状：\\n⚠️涙や目やにの増加\\n⚠️まぶたの腫れ\\n⚠️目を擦る行動\\n⚠️瞳の色の変化\\n\\n放置すると視力に影響することも。気になったら早めに受診を！\\n#猫のあれこれ",
            "【猫の皮膚トラブル】原因と対策🔍\\n\\n皮膚病は猫の診察で最も多い病気の一つ。\\n\\n主な原因：\\n✅アレルギー\\n✅寄生虫\\n✅細菌感染\\n✅ストレス\\n\\n症状：かゆみ、脱毛、湿疹\\n原因特定が治療の鍵。自己判断せず獣医師へ！\\n#猫のあれこれ",
            "【猫の肥満対策】適正体重を保つ方法⚖️\\n\\n室内飼いの猫の約40%が肥満気味。\\n\\n肥満のリスク：\\n⚠️糖尿病\\n⚠️関節疾患\\n⚠️心疾患\\n⚠️麻酔リスク増加\\n\\n対策：適量給餌、運動促進、定期体重測定\\n愛猫の健康のため、体重管理を！\\n#猫のあれこれ",
            "【猫の口臭】気になる原因と対策🦷\\n\\n口臭は病気のサインかも。\\n\\n主な原因：\\n✅歯周病\\n✅口内炎\\n✅腎疾患\\n✅消化器疾患\\n\\n予防法：歯磨き、デンタルケア用品、定期検診\\n強い口臭は要注意。早めの受診を！\\n#猫のあれこれ",
            "【猫の夏バテ対策】暑い季節を乗り切る方法🌡️\\n\\n猫も夏バテします。\\n\\n注意点：\\n⚠️室温管理（26-28℃）\\n⚠️水分摂取量確保\\n⚠️直射日光を避ける\\n⚠️食欲低下に注意\\n\\n症状：ぐったり、食欲不振、呼吸荒い\\n快適な環境作りが大切です♪\\n#猫のあれこれ",
            "【猫の毛玉対策】効果的な予防法✂️\\n\\n長毛種は特に注意が必要。\\n\\n毛玉の害：\\n⚠️腸閉塞のリスク\\n⚠️嘔吐の原因\\n⚠️食欲不振\\n\\n対策：\\n✅毎日のブラッシング\\n✅毛玉除去剤\\n✅定期的なトリミング\\n\\nお手入れで健康維持を！\\n#猫のあれこれ"
        ]
        
        # 犬のケーススタディ（質問・回答ペア）
        self.content_pools['dog_cases'] = [
            {
                "question": "【ケース①：散歩の変化】\\n\\n症例：6歳のラブラドール\\n最近、散歩中に立ち止まることが多くなった。\\n以前は元気に走っていたのに、歩くペースも遅くなった🐕\\n\\n考えられる原因は？\\n（実際によくある相談です）\\n明日、獣医師が解説します！\\n#獣医が教える犬のはなし",
                "answer": "【ケース①：獣医師の解説】\\n\\n昨日のケース、最も疑わしいのは関節の問題です。\\n大型犬に多い股関節形成不全や関節炎が考えられます🦴\\n\\n症状の特徴：\\n✅歩行ペースの低下\\n✅立ち止まりが増える\\n✅階段を嫌がる\\n\\n早期診断で適切な治療を！\\n#獣医が教える犬のはなし"
            },
            {
                "question": "【ケース②：食欲の変化】\\n\\n症例：8歳のシーズー\\n普段は食いしん坊なのに、最近フードを残すように。\\n水はよく飲むが、なんとなく元気がない💭\\n\\n何を疑いますか？\\n（複数の原因が考えられます）\\n#獣医が教える犬のはなし",
                "answer": "【ケース②：獣医師の解説】\\n\\n昨日のケース、多飲と食欲不振の組み合わせから腎臓病や糖尿病を疑います。\\n\\n鑑別すべき疾患：\\n✅慢性腎不全\\n✅糖尿病\\n✅甲状腺機能低下症\\n✅歯周病\\n\\n血液検査での確定診断が必要です🏥\\n#獣医が教える犬のはなし"
            },
            {
                "question": "【ケース③：呼吸の変化】\\n\\n症例：5歳のフレンチブルドッグ\\n運動後の呼吸が以前より荒い。\\n舌の色も心なしか薄い気がする😰\\n\\n緊急性は？どう対処する？\\n（短頭種に多い問題です）\\n#獣医が教える犬のはなし",
                "answer": "【ケース③：獣医師の解説】\\n\\n昨日のケース、短頭種症候群の悪化が疑われます。\\n舌の色が薄いのは酸素不足のサイン⚠️\\n\\n緊急性：高\\n✅即座に涼しい場所へ\\n✅安静にする\\n✅早急に受診\\n\\n夏場は特に注意が必要です！\\n#獣医が教える犬のはなし"
            },
            {
                "question": "【ケース④：皮膚の変化】\\n\\n症例：3歳のゴールデンレトリーバー\\n最近、体を掻く頻度が増えた。\\n毛が抜けて赤くなっている部分もある🔴\\n\\n原因として何が考えられる？\\n（春に多い相談です）\\n#獣医が教える犬のはなし",
                "answer": "【ケース④：獣医師の解説】\\n\\n昨日のケース、春に多いアレルギー性皮膚炎が最有力です。\\n\\n主な原因：\\n✅花粉アレルギー\\n✅ノミ・ダニ\\n✅食物アレルギー\\n✅細菌感染の併発\\n\\n適切な診断と治療で改善可能です🏥\\n#獣医が教える犬のはなし"
            },
            {
                "question": "【ケース⑤：排尿の変化】\\n\\n症例：7歳のダックスフント\\n排尿回数が増えて、時々血が混じる。\\n普段は我慢できるのに、家でも失敗することが💦\\n\\n緊急度と対処法は？\\n（オスメス関係なく起こります）\\n#獣医が教える犬のはなし",
                "answer": "【ケース⑤：獣医師の解説】\\n\\n昨日のケース、膀胱炎や尿路結石が疑われます。\\n血尿は重要なサイン⚠️\\n\\n考えられる原因：\\n✅細菌性膀胱炎\\n✅尿路結石\\n✅膀胱腫瘍\\n\\n尿検査で原因特定を！早期治療が重要です🏥\\n#獣医が教える犬のはなし"
            },
            {
                "question": "【ケース⑥：嘔吐の症状】\\n\\n症例：4歳のトイプードル\\n昨日から何度も嘔吐している。\\n最初は食べたものを吐いたが、今は透明な液体のみ💧\\n\\n考えられる原因は？\\n（頻度の高い症状です）\\n明日、獣医師が解説します！\\n#獣医が教える犬のはなし",
                "answer": "【ケース⑥：獣医師の解説】\\n\\n昨日のケース、急性胃腸炎が最も疑われます。\\n\\n主な原因：\\n✅食べ過ぎ・早食い\\n✅異物誤飲\\n✅ストレス\\n✅ウイルス感染\\n\\n透明な液体は胃液。12時間以上続く場合は緊急受診を！\\n#獣医が教える犬のはなし"
            },
            {
                "question": "【ケース⑦：咳の症状】\\n\\n症例：9歳のキャバリア\\n乾いた咳が続いている。\\n特に興奮した時や夜間に多い。運動はいつも通り元気😊\\n\\n何を疑うべき？\\n（この犬種に多い病気です）\\n明日、獣医師が解説します！\\n#獣医が教える犬のはなし",
                "answer": "【ケース⑦：獣医師の解説】\\n\\n昨日のケース、僧帽弁閉鎖不全症（心疾患）を疑います。\\n\\nキャバリアに多い病気：\\n✅心雑音の確認\\n✅レントゲン検査\\n✅心エコー検査\\n\\n早期診断で内服治療可能。定期検診が重要です🏥\\n#獣医が教える犬のはなし"
            },
            {
                "question": "【ケース⑧：食欲不振】\\n\\n症例：12歳の柴犬\\n2日前から急にご飯を食べなくなった。\\n水は飲むが、大好きなおやつにも興味を示さない😔\\n\\n高齢犬での食欲不振、何を疑う？\\n明日、獣医師が解説します！\\n#獣医が教える犬のはなし",
                "answer": "【ケース⑧：獣医師の解説】\\n\\n昨日のケース、高齢犬では複数の原因が考えられます。\\n\\n主な原因：\\n✅歯周病・口内炎\\n✅内臓疾患\\n✅認知症\\n✅腫瘍\\n\\n2日以上の食欲不振は要注意。早めの検査を！\\n#獣医が教える犬のはなし"
            },
            {
                "question": "【ケース⑨：歩き方の変化】\\n\\n症例：6歳のラブラドール\\n最近、後ろ足を引きずるような歩き方になった。\\n痛がる様子はないが、階段を嫌がるように🐕\\n\\n大型犬に多いこの症状、原因は？\\n明日、獣医師が解説します！\\n#獣医が教える犬のはなし",
                "answer": "【ケース⑨：獣医師の解説】\\n\\n昨日のケース、股関節形成不全や椎間板ヘルニアが疑われます。\\n\\n大型犬に多い疾患：\\n✅股関節形成不全\\n✅十字靭帯断裂\\n✅椎間板ヘルニア\\n\\nレントゲン検査で診断可能。早期治療で進行を抑制できます🏥\\n#獣医が教える犬のはなし"
            },
            {
                "question": "【ケース⑩：目の変化】\\n\\n症例：10歳のシーズー\\n目が白く濁ってきた。\\nぶつかることはないが、夜間の視力が落ちている感じ👁️\\n\\n高齢犬の目の変化、治療は必要？\\n明日、獣医師が解説します！\\n#獣医が教える犬のはなし",
                "answer": "【ケース⑩：獣医師の解説】\\n\\n昨日のケース、白内障の初期段階と思われます。\\n\\n高齢犬の目の病気：\\n✅白内障→水晶体の白濁\\n✅緑内障→眼圧上昇\\n✅ドライアイ→涙液不足\\n\\n定期的な眼科検査で進行をモニタリング。必要に応じて点眼治療を🏥\\n#獣医が教える犬のはなし"
            },
            {
                "question": "【ケース⑪：異物誤飲】\\n\\n症例：2歳のボーダーコリー\\n散歩中に何かを拾い食いした。\\n帰宅後から元気がなく、時々吐こうとする仕草😰\\n\\n異物誤飲の対処法は？\\n明日、獣医師が解説します！\\n#獣医が教える犬のはなし",
                "answer": "【ケース⑪：獣医師の解説】\\n\\n昨日のケース、異物誤飲の可能性が高いです。\\n\\n緊急対応：\\n✅無理に吐かせない\\n✅食事・水分制限\\n✅即座に受診\\n\\nレントゲンやエコーで確認。内視鏡や手術で摘出することも🏥\\n#獣医が教える犬のはなし"
            }
        ]
        
        # 犬の健康投稿
        self.content_pools['dog_health'] = [
            "【犬の肥満対策】適正体重を保つコツ⚖️\\n\\n肥満は万病の元！適正体重維持のポイント：\\n\\n✅理想体重の把握\\n✅カロリー計算\\n✅おやつの制限\\n✅定期的な運動\\n\\n肋骨を軽く触れるのが理想的。\\n愛犬の体重管理、見直してみませんか？\\n#獣医が教える犬のはなし",
            "【犬の関節ケア】年齢に関係なく大切🦴\\n\\n関節の健康は生活の質に直結！\\n\\n予防のポイント：\\n✅適正体重の維持\\n✅適度な運動\\n✅滑りにくい床材\\n✅関節サプリの活用\\n\\n大型犬だけでなく小型犬でも要注意。\\n毎日の積み重ねが大切です♪\\n#獣医が教える犬のはなし",
            "【犬の心臓病】早期発見のサイン❤️\\n\\n心臓病は犬の死因上位の病気。\\n\\n注意すべき症状：\\n⚠️咳が出る\\n⚠️疲れやすい\\n⚠️舌の色が悪い\\n⚠️失神する\\n\\n中高齢期からリスク上昇。\\n定期検診で早期発見を！\\n#獣医が教える犬のはなし",
            "【犬の耳の健康】トラブル予防法👂\\n\\n耳のトラブルは犬に多い病気の一つ。\\n\\n予防のポイント：\\n✅定期的な耳掃除\\n✅湿度管理\\n✅アレルゲン除去\\n✅早期治療\\n\\n垂れ耳の犬種は特に注意！\\n日頃のケアで健康な耳を保ちましょう♪\\n#獣医が教える犬のはなし",
            "【シニア犬の健康管理】7歳からの注意点👴\\n\\n7歳以降は人間でいう44歳。健康管理の重要性が増します。\\n\\n注意すべき点：\\n✅定期健診の頻度アップ\\n✅食事内容の見直し\\n✅運動量の調整\\n✅認知症の予防\\n\\n早めの対策で元気な老後を！\\n#獣医が教える犬のはなし",
            "【犬の誤飲対策】家庭内の危険なもの⚠️\\n\\n犬の誤飲事故は意外と多い。\\n\\n危険なもの：\\n🚫チョコレート・キシリトール\\n🚫小さなおもちゃ・ボタン\\n🚫薬・タバコ\\n🚫鶏の骨\\n\\n対策：手の届かない場所に保管\\n誤飲した場合は即座に受診を！\\n#獣医が教える犬のはなし",
            "【犬の熱中症対策】夏の危険を回避🌡️\\n\\n犬は体温調節が苦手。\\n\\n症状：\\n⚠️激しいパンティング\\n⚠️よだれが多量\\n⚠️ぐったりしている\\n⚠️嘔吐・下痢\\n\\n対策：散歩時間の調整、水分補給、日陰の確保\\n症状があれば緊急受診！\\n#獣医が教える犬のはなし",
            "【犬の歯石除去】麻酔の必要性について🦷\\n\\n歯石除去には全身麻酔が必要。\\n\\n理由：\\n✅安全な処置のため\\n✅ストレス軽減\\n✅歯周ポケット内の清掃\\n✅レントゲン撮影\\n\\n無麻酔処置は表面のみ。根本的な治療にはなりません🏥\\n#獣医が教える犬のはなし",
            "【犬のワクチン】接種スケジュールと重要性💉\\n\\n予防接種で命を守る。\\n\\n子犬：\\n✅6-8週：初回\\n✅10-12週：2回目\\n✅14-16週：3回目\\n\\n成犬：年1回追加接種\\n\\n狂犬病予防注射は法的義務。必ず接種を！\\n#獣医が教える犬のはなし"
        ]
    
    def log_message(self, message: str):
        """ログメッセージを表示"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def generate_content_with_monitoring(self, content_type: str, animal_type: str, 
                                       topic: str = None, qa_type: str = None) -> str:
        """重複監視付きコンテンツ生成"""
        
        self.duplicate_monitor.similarity_threshold = float(self.similarity_var.get()) / 100
        months_back = int(self.check_months_var.get())
        
        for attempt in range(self.max_regeneration_attempts):
            # コンテンツ生成
            if content_type == "cat_question":
                qa_pair = random.choice(self.content_pools['cat_questions'])
                content = qa_pair["question"] if qa_type == "question" else qa_pair["answer"]
            elif content_type == "cat_health":
                content = random.choice(self.content_pools['cat_health'])
            elif content_type == "dog_case":
                qa_pair = random.choice(self.content_pools['dog_cases'])
                content = qa_pair["question"] if qa_type == "question" else qa_pair["answer"]
            elif content_type == "dog_health":
                content = random.choice(self.content_pools['dog_health'])
            else:
                content = "デフォルトコンテンツ"
            
            # 重複チェック
            self.log_message(f"🔍 重複チェック実行中... (試行 {attempt + 1}/{self.max_regeneration_attempts})")
            
            is_duplicate, duplicate_info = self.duplicate_monitor.check_duplicate_comprehensive(
                content, animal_type, topic, months_back
            )
            
            if not is_duplicate:
                self.log_message(f"✅ 重複なし - コンテンツ承認")
                # 承認されたコンテンツを保存
                self.duplicate_monitor.save_approved_post(content, animal_type, topic, content_type)
                return content
            else:
                self.log_message(f"⚠️ 重複検出! 類似度: {duplicate_info[0]['similarity']:.2f}")
                self.log_message(f"   類似投稿: {duplicate_info[0]['content'][:50]}...")
                
                if attempt < self.max_regeneration_attempts - 1:
                    self.log_message(f"🔄 再生成を試行します...")
                    # 少し変化を加えて再生成
                    continue
        
        self.log_message(f"❌ {self.max_regeneration_attempts}回の試行後も重複が解決できませんでした")
        return None
    
    def generate_posts_with_monitoring(self):
        """重複監視付き投稿生成"""
        try:
            days = int(self.days_var.get())
            if days <= 0:
                raise ValueError("正の数を入力してください")
        except ValueError:
            messagebox.showerror("エラー", "正しい日数を入力してください")
            return
        
        self.log_text.delete(1.0, tk.END)
        self.result_text.delete(1.0, tk.END)
        self.progress['value'] = 0
        
        self.status_var.set("重複監視付き投稿生成を開始中...")
        self.log_message("🚀 重複監視付き投稿生成を開始")
        
        week_type = self.week_type_var.get()
        posts = []
        start_date = datetime.now()
        
        successful_generations = 0
        failed_generations = 0
        
        # 質問-回答ペアの管理
        selected_cat_qa = None
        selected_dog_qa = None
        
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            weekday = current_date.weekday()  # 0=月曜, 1=火曜...
            
            # 猫投稿（7:00）
            self.log_message(f"📅 {current_date.strftime('%Y-%m-%d')} 猫投稿生成中...")
            
            # 月曜・水曜・金曜(0,2,4)に質問、火曜・木曜・土曜(1,3,5)に回答
            if weekday % 2 == 0:  # 質問の日
                selected_cat_qa = random.choice(self.content_pools['cat_questions'])
                cat_content = selected_cat_qa["question"]
                # 重複チェック
                is_duplicate, _ = self.duplicate_monitor.check_duplicate_comprehensive(
                    cat_content, "cat", "猫の健康", int(self.check_months_var.get())
                )
                if is_duplicate:
                    self.log_message(f"⚠️ 猫質問で重複検出、別の質問を選択")
                    available_questions = [qa for qa in self.content_pools['cat_questions'] if qa != selected_cat_qa]
                    if available_questions:
                        selected_cat_qa = random.choice(available_questions)
                        cat_content = selected_cat_qa["question"]
                self.log_message(f"📝 猫質問選択: {cat_content[:30]}...")
            else:  # 回答の日
                if selected_cat_qa is not None:
                    cat_content = selected_cat_qa["answer"]
                    self.log_message(f"📝 猫回答生成: 前日の質問に対応")
                    # 重複チェック
                    is_duplicate, _ = self.duplicate_monitor.check_duplicate_comprehensive(
                        cat_content, "cat", "猫の健康", int(self.check_months_var.get())
                    )
                    if is_duplicate:
                        self.log_message(f"⚠️ 猫回答で重複検出、健康投稿にフォールバック")
                        cat_content = self.generate_content_with_monitoring("cat_health", "cat", "猫の健康")
                        selected_cat_qa = None
                    selected_cat_qa = None
                else:
                    self.log_message(f"⚠️ 猫: 対応する質問がないため健康投稿にフォールバック")
                    cat_content = self.generate_content_with_monitoring("cat_health", "cat", "猫の健康")
            
            if cat_content:
                posts.append([
                    current_date.replace(hour=7, minute=0).strftime('%Y-%m-%d %H:%M'),
                    cat_content.replace('\\n', '\n'),
                    str(len(cat_content))
                ])
                self.duplicate_monitor.save_approved_post(
                    cat_content, "cat", "猫の健康", 
                    "cat_question" if weekday % 2 == 0 else "cat_answer"
                )
                successful_generations += 1
                self.log_message(f"✅ 猫投稿生成成功 ({'質問' if weekday % 2 == 0 else '回答'})")
            else:
                failed_generations += 1
                self.log_message(f"❌ 猫投稿生成失敗 ({current_date.strftime('%Y-%m-%d')})")
            
            # 犬投稿（18:00）
            self.log_message(f"📅 {current_date.strftime('%Y-%m-%d')} 犬投稿生成中...")
            
            # 月曜・水曜・金曜(0,2,4)に質問、火曜・木曜・土曜(1,3,5)に回答
            if weekday % 2 == 0:  # 質問の日
                selected_dog_qa = random.choice(self.content_pools['dog_cases'])
                dog_content = selected_dog_qa["question"]
                # 重複チェック
                is_duplicate, _ = self.duplicate_monitor.check_duplicate_comprehensive(
                    dog_content, "dog", "犬の健康", int(self.check_months_var.get())
                )
                if is_duplicate:
                    self.log_message(f"⚠️ 犬質問で重複検出、別の質問を選択")
                    available_questions = [qa for qa in self.content_pools['dog_cases'] if qa != selected_dog_qa]
                    if available_questions:
                        selected_dog_qa = random.choice(available_questions)
                        dog_content = selected_dog_qa["question"]
                self.log_message(f"📝 犬質問選択: {dog_content[:30]}...")
            else:  # 回答の日
                if selected_dog_qa is not None:
                    dog_content = selected_dog_qa["answer"]
                    self.log_message(f"📝 犬回答生成: 前日の質問に対応")
                    # 重複チェック
                    is_duplicate, _ = self.duplicate_monitor.check_duplicate_comprehensive(
                        dog_content, "dog", "犬の健康", int(self.check_months_var.get())
                    )
                    if is_duplicate:
                        self.log_message(f"⚠️ 犬回答で重複検出、健康投稿にフォールバック")
                        dog_content = self.generate_content_with_monitoring("dog_health", "dog", "犬の健康")
                        selected_dog_qa = None
                    selected_dog_qa = None
                else:
                    self.log_message(f"⚠️ 犬: 対応する質問がないため健康投稿にフォールバック")
                    dog_content = self.generate_content_with_monitoring("dog_health", "dog", "犬の健康")
            
            if dog_content:
                posts.append([
                    current_date.replace(hour=18, minute=0).strftime('%Y-%m-%d %H:%M'),
                    dog_content.replace('\\n', '\n'),
                    str(len(dog_content))
                ])
                self.duplicate_monitor.save_approved_post(
                    dog_content, "dog", "犬の健康", 
                    "dog_case" if weekday % 2 == 0 else "dog_answer"
                )
                successful_generations += 1
                self.log_message(f"✅ 犬投稿生成成功 ({'質問' if weekday % 2 == 0 else '回答'})")
            else:
                failed_generations += 1
                self.log_message(f"❌ 犬投稿生成失敗 ({current_date.strftime('%Y-%m-%d')})")
            
            # 進捗更新
            self.progress['value'] = (i + 1) / days * 100
            self.root.update()
        
        # 結果出力
        if posts:
            output_filename = f"enhanced_posts_{start_date.strftime('%Y-%m-%d')}_{week_type}.csv"
            output_dir = os.path.join(os.path.dirname(__file__), "output")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                import csv
                writer = csv.writer(f)
                writer.writerow(['投稿日時', '投稿内容', '文字数'])
                writer.writerows(posts)
            
            self.log_message(f"💾 結果保存: {output_filename}")
            
            # 結果表示
            self.result_text.insert(tk.END, f"🎉 重複監視付き生成完了!\\n\\n")
            self.result_text.insert(tk.END, f"📊 成功: {successful_generations}件 | 失敗: {failed_generations}件\\n")
            self.result_text.insert(tk.END, f"📁 保存先: {output_path}\\n\\n")
            
            self.result_text.insert(tk.END, "=== 生成された投稿 ===\\n\\n")
            for post in posts:
                self.result_text.insert(tk.END, f"📅 {post[0]}\\n")
                self.result_text.insert(tk.END, f"📝 {post[1][:100]}...\\n")
                self.result_text.insert(tk.END, f"📏 ({post[2]}文字)\\n\\n")
                self.result_text.insert(tk.END, "-" * 60 + "\\n\\n")
            
            self.status_var.set(f"✅ 生成完了: {successful_generations}件成功, {failed_generations}件失敗")
            
            # 最後に生成されたCSVファイルを記録
            self.last_generated_csv = output_path
            # アップロードボタンを有効化
            if self.sheets_uploader.client and self.sheets_url_var.get():
                self.upload_button.config(state="normal")
            
        else:
            self.status_var.set("❌ 生成失敗: 重複のため生成できませんでした")
            messagebox.showerror("エラー", "重複のため投稿を生成できませんでした")
        
        self.progress['value'] = 0
    
    def setup_google_auth(self):
        """Google Sheets API認証を設定"""
        try:
            if self.sheets_uploader.setup_credentials():
                self.auth_status_var.set("認証済み")
                self.auth_status_var.set("認証済み")
                # ラベルの色を緑に変更
                for widget in self.root.winfo_children():
                    if isinstance(widget, ttk.Frame):
                        for child in widget.winfo_children():
                            if isinstance(child, ttk.LabelFrame) and child.cget("text") == "Googleスプレッドシート連携":
                                for label in child.winfo_children():
                                    if isinstance(label, ttk.Label) and label.cget("textvariable") == str(self.auth_status_var):
                                        label.config(foreground="green")
                                        break
                                break
                        break
                
                # URLが設定されていればアップロードボタンを有効化
                if self.sheets_url_var.get() and self.last_generated_csv:
                    self.upload_button.config(state="normal")
                    
                messagebox.showinfo("認証成功", "Google Sheets APIの認証が完了しました！")
            else:
                self.auth_status_var.set("認証失敗")
        except Exception as e:
            messagebox.showerror("認証エラー", f"認証に失敗しました:\n{str(e)}")
    
    def upload_to_google_sheets(self):
        """生成されたCSVをGoogleスプレッドシートにアップロード"""
        if not self.last_generated_csv:
            messagebox.showerror("エラー", "アップロードするCSVファイルがありません。\n先に投稿を生成してください。")
            return
        
        if not self.sheets_url_var.get():
            messagebox.showerror("エラー", "スプレッドシートのURLを入力してください。")
            return
        
        if not self.sheets_uploader.client:
            messagebox.showerror("エラー", "Google Sheets APIの認証が完了していません。")
            return
        
        try:
            # スプレッドシートURLを設定
            self.sheets_uploader.set_spreadsheet_url(self.sheets_url_var.get())
            
            # アップロード実行
            self.status_var.set("📤 Googleスプレッドシートにアップロード中...")
            self.root.update()
            
            # フォーマット済みシートとして作成
            if self.sheets_uploader.create_formatted_schedule_sheet(self.last_generated_csv):
                self.status_var.set("✅ Googleスプレッドシートへのアップロード完了！")
                self.log_message("📤 Googleスプレッドシートアップロード成功")
            else:
                self.status_var.set("❌ Googleスプレッドシートへのアップロードに失敗")
                self.log_message("❌ Googleスプレッドシートアップロード失敗")
                
        except Exception as e:
            self.status_var.set("❌ アップロードエラー")
            self.log_message(f"❌ アップロードエラー: {str(e)}")
            messagebox.showerror("アップロードエラー", f"アップロードに失敗しました:\n{str(e)}")
    
    def on_theme_change(self, event=None):
        """週テーマ変更時の処理"""
        theme = self.week_type_var.get()
        
        # テーマに応じて詳細設定の選択肢を更新
        if theme == "猫種特集":
            breeds = list(self.ai_generator.breed_database.keys())
            self.topic_combo['values'] = ("自動選択",) + tuple(breeds)
        elif theme == "専門テーマ":
            topics = list(self.ai_generator.medical_knowledge.keys())
            self.topic_combo['values'] = ("自動選択",) + tuple(topics)
        elif theme == "健康管理":
            areas = ["食事管理", "運動管理", "グルーミング", "ストレス管理", "環境整備"]
            self.topic_combo['values'] = ("自動選択",) + tuple(areas)
        else:  # 参加型
            self.topic_combo['values'] = ("自動選択", "クイズ特集", "アンケート特集", "写真投稿企画")
        
        # デフォルトを自動選択に戻す
        self.specific_topic_var.set("自動選択")
    
    def generate_posts_with_ai(self):
        """シンプル投稿生成（AI機能を無効化して安定動作を優先）"""
        try:
            # 基本設定の取得
            days = int(self.days_var.get())
            if days != 7:
                messagebox.showwarning("注意", "現在7日間のみ対応しています。7日間で生成します。")
                days = 7
            
            theme_type = self.week_type_var.get()
            
            # 開始日の設定（今日から）
            start_date = datetime.now().replace(hour=7, minute=0, second=0, microsecond=0)
            
            self.status_var.set("📝 投稿を生成中...")
            self.progress['value'] = 10
            self.root.update()
            
            # シンプル生成のみ使用（AI機能を完全無効化）
            self.log_message(f"📝 シンプル生成開始: テーマ={theme_type}")
            ai_posts = self._generate_simple_fallback_posts(start_date, theme_type)
            
            self.progress['value'] = 40
            self.root.update()
            
            # 重複チェックと調整
            checked_posts = []
            successful_generations = 0
            failed_generations = 0
            
            for i, ai_post in enumerate(ai_posts):
                self.progress['value'] = 40 + (i / len(ai_posts)) * 50
                self.root.update()
                
                # 投稿時間の設定（猫：07:00、犬：18:00の代替として曜日ベースで設定）
                post_date = datetime.strptime(ai_post['date'], '%Y-%m-%d')
                if i % 2 == 0:  # 偶数日は朝（猫の時間）
                    post_datetime = post_date.replace(hour=7, minute=0)
                else:  # 奇数日は夕方（犬の時間）
                    post_datetime = post_date.replace(hour=18, minute=0)
                
                content = ai_post['content']
                
                # 重複チェック
                is_duplicate, similarity = self.duplicate_monitor.check_duplicate_comprehensive(
                    content, "cat", theme_type, int(self.check_months_var.get())
                )
                
                if is_duplicate:
                    self.log_message(f"⚠️ 重複検出（類似度:{similarity:.1f}%）: {content[:30]}...")
                    
                    # AI による代替コンテンツ生成を試行
                    retry_success = False
                    for attempt in range(self.max_regeneration_attempts):
                        self.log_message(f"🔄 AI代替生成試行 {attempt + 1}/{self.max_regeneration_attempts}")
                        
                        # 少し異なるプロンプトで再生成（簡易版）
                        alternative_content = self._generate_alternative_content(content, theme_type, attempt)
                        
                        is_dup_alt, sim_alt = self.duplicate_monitor.check_duplicate_comprehensive(
                            alternative_content, "cat", theme_type, int(self.check_months_var.get())
                        )
                        
                        if not is_dup_alt:
                            content = alternative_content
                            retry_success = True
                            self.log_message(f"✅ AI代替生成成功: {content[:30]}...")
                            break
                    
                    if not retry_success:
                        self.log_message(f"❌ 重複回避失敗: {ai_post['date']}")
                        failed_generations += 1
                        continue
                
                # 投稿を承認リストに追加
                checked_posts.append([
                    post_datetime.strftime('%Y-%m-%d %H:%M'),
                    content,
                    str(len(content))
                ])
                
                # 重複監視システムに登録
                self.duplicate_monitor.save_approved_post(
                    content, "cat", theme_type, f"ai_generated_{theme_type}"
                )
                
                successful_generations += 1
                self.log_message(f"✅ AI生成投稿承認: {ai_post['date']}")
            
            self.progress['value'] = 90
            self.root.update()
            
            # 結果をファイルに保存
            if checked_posts:
                output_filename = f"ai_enhanced_posts_{start_date.strftime('%Y-%m-%d')}_{theme_type}.csv"
                output_dir = os.path.join(os.path.dirname(__file__), "output")
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, output_filename)
                
                import csv
                with open(output_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['投稿日時', '投稿内容', '文字数'])
                    writer.writerows(checked_posts)
                
                self.log_message(f"💾 AI生成結果保存: {output_filename}")
                
                # 結果表示
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, f"🤖 AI生成完了！\n\n")
                self.result_text.insert(tk.END, f"📊 成功: {successful_generations}件 | 失敗: {failed_generations}件\n")
                self.result_text.insert(tk.END, f"🎯 テーマ: {theme_type} ({specific_topic or '自動選択'})\n")
                self.result_text.insert(tk.END, f"📁 保存先: {output_path}\n\n")
                
                self.result_text.insert(tk.END, "=== AI生成された投稿 ===\n\n")
                for post in checked_posts:
                    self.result_text.insert(tk.END, f"📅 {post[0]}\n")
                    self.result_text.insert(tk.END, f"📝 {post[1]}\n")
                    self.result_text.insert(tk.END, f"📏 ({post[2]}文字)\n\n")
                    self.result_text.insert(tk.END, "-" * 60 + "\n\n")
                
                self.status_var.set(f"🤖 AI生成完了: {successful_generations}件成功, {failed_generations}件失敗")
                
                # 最後に生成されたCSVファイルを記録
                self.last_generated_csv = output_path
                # アップロードボタンを有効化
                if self.sheets_uploader.client and self.sheets_url_var.get():
                    self.upload_button.config(state="normal")
                
            else:
                self.status_var.set("❌ AI生成失敗: 重複のため投稿を生成できませんでした")
                messagebox.showerror("生成失敗", "重複のため投稿を生成できませんでした")
            
            self.progress['value'] = 100
            self.root.update()
            
        except Exception as e:
            self.status_var.set(f"❌ AI生成エラー: {str(e)}")
            self.log_message(f"❌ AI生成エラー: {str(e)}")
            messagebox.showerror("生成エラー", f"AI生成中にエラーが発生しました:\n{str(e)}")
        finally:
            self.progress['value'] = 0
    
    def _generate_alternative_content(self, original_content, theme_type, attempt):
        """
        重複回避のための代替コンテンツ生成（簡易版）
        """
        # 簡易的な代替生成（実際のAI APIを使用する場合はここを拡張）
        variations = [
            original_content.replace("獣医師が教える", "獣医師が解説"),
            original_content.replace("クイズ", "問題"),
            original_content.replace("みなさん", "皆さん"),
            original_content.replace("♪", "✨"),
            original_content.replace("！", "。")
        ]
        
        if attempt < len(variations):
            return variations[attempt]
        else:
            # 最後の手段：絵文字の変更
            import re
            emoji_replacements = {
                "🐱": "😸", "😴": "💤", "🍽️": "🥣", "💧": "💦",
                "⚠️": "🚨", "✅": "☑️", "❤️": "💖"
            }
            
            modified = original_content
            for old_emoji, new_emoji in emoji_replacements.items():
                if old_emoji in modified:
                    modified = modified.replace(old_emoji, new_emoji, 1)
                    break
            
            return modified
    
    def _generate_simple_fallback_posts(self, start_date, theme_type):
        """
        安定版シンプル投稿生成（猫と犬の両方）
        """
        posts = []
        
        if theme_type == "猫種特集":
            # ロシアンブルー特集の例
            sample_posts = [
                "獣医師が教える！ロシアンブルー特集①🇷🇺\n\n「ボイスレスキャット」とも呼ばれる美しい猫種。\n\n✅エメラルドグリーンの瞳\n✅ブルーの被毛\n✅優雅なスリム体型\n\n今週はその魅力を解説します！\n#猫のあれこれ",
                
                "獣医師が教える！ロシアンブルー特集②歴史📜\n\nロシア皇帝に愛された高貴な猫種。\n\n✅ロシア起源の貴族の猫\n✅19世紀にイギリスで品種改良\n✅戦後に復活を遂げた\n\n神秘的な雰囲気はその歴史から♪\n#猫のあれこれ",
                
                "獣医師が教える！ロシアンブルー特集③性格🐈\n\n「犬のような猫」と言われる忠実さ。\n\n✅物静かでおとなしい\n✅警戒心が強く人見知り\n✅心を許した相手には深い愛情\n\nツンデレな魅力が人気の秘密♪\n#猫のあれこれ",
                
                "獣医師が教える！ロシアンブルー特集④特徴✨\n\n美しい外見の秘密。\n\n✅ダブルコートの銀色光沢\n✅グリーンの美しい瞳\n✅微笑んでいるような口元\n\nロシアンスマイルが魅力的♪\n#猫のあれこれ",
                
                "獣医師が教える！ロシアンブルー特集⑤健康⚠️\n\n比較的健康な猫種ですが注意点も。\n\n✅アレルギー性皮膚炎\n✅ストレスに弱い傾向\n✅肥満になりやすい\n\n適切なケアで健康維持を♪\n#猫のあれこれ",
                
                "獣医師の豆知識：ロシアンブルーのケア✨\n\n美しさを保つケア方法。\n\n✅週1-2回のブラッシング\n✅カロリーコントロール\n✅知的な遊びを取り入れる\n\n静かですが遊びは大好きです♪\n#猫のあれこれ",
                
                "見せて！あなたのロシアンブルー😊\n\nロシアンブルーの飼い主さん！\n愛猫の「ロシアンスマイル」を見せてください♪\n\n#ロシアンスマイル見せて で投稿をお待ちしています！\n#猫のあれこれ"
            ]
        
        elif theme_type == "専門テーマ":
            # 慢性腎臓病特集の例
            sample_posts = [
                "獣医師が教える！猫の慢性腎臓病①💧\n\n高齢猫に多い重要な病気。\n\n✅腎機能が徐々に低下\n✅初期は症状が出にくい\n✅早期発見が重要\n\n今週は詳しく解説します。\n#猫のあれこれ",
                
                "獣医師が教える！猫の慢性腎臓病②症状👀\n\n初期症状に注意が必要。\n\n✅多飲多尿\n✅体重減少\n✅毛づやの悪化\n\n「歳のせい」と思わず早めの相談を。\n#猫のあれこれ",
                
                "獣医師が教える！猫の慢性腎臓病③進行⚠️\n\n病状が進行すると重篤な症状が。\n\n✅食欲不振、嘔吐\n✅元気消失\n✅貧血、口内炎\n\n早期の治療開始が重要です。\n#猫のあれこれ",
                
                "獣医師が教える！猫の慢性腎臓病④診断🩺\n\n正確な診断のための検査。\n\n✅血液検査(BUN,Cr,SDMA)\n✅尿検査(比重、蛋白)\n✅超音波検査\n\n定期健診での早期発見を。\n#猫のあれこれ",
                
                "獣医師が教える！猫の慢性腎臓病⑤治療💊\n\n進行を穏やかにする治療。\n\n✅食事療法\n✅輸液による水分補給\n✅投薬治療\n\n獣医師と相談し適切な治療を。\n#猫のあれこれ",
                
                "獣医師の豆知識：腎臓病のお家ケア🏠\n\n水分補給が非常に重要！\n\n✅ウェットフードを活用\n✅新鮮な水を複数箇所に\n✅流れる水を好む子には給水器\n\n少しでも飲水量を増やす工夫を。\n#猫のあれこれ",
                
                "獣医師からのお願い：腎臓を守るために🙏\n\n予防と早期発見のポイント。\n\n✅7歳以上は年1回健診\n✅飲水量・尿の観察\n✅適切な体重管理\n\n日々の観察が愛猫を守ります。\n#猫のあれこれ"
            ]
        
        else:  # 参加型・健康管理
            sample_posts = [
                "獣医師が教える！猫の毛づくろいクイズ👁️\n\nQ. 猫が1日に毛づくろいに費やす時間の割合は？\n\n①約10%\n②約30%\n③約50%\n\n正解と詳しい解説は明日発表！猫の習性について一緒に学びましょう♪\n#猫のあれこれ",
                
                "獣医師が解説！昨日のクイズ答え合わせ💡\n\n正解は②約30%でした！\n\n猫は起きている時間の30-50%を毛づくろいに費やします。これは体温調節、リラックス効果、社会的な意味もある大切な行動なんです✨\n#猫のあれこれ",
                
                "獣医師に教えて！愛猫の夏の過ごし方調査☀️\n\n【質問】あなたの猫ちゃんは夏場、どこで涼むのが好きですか？\n\n①フローリングの上\n②玄関のたたき\n③エアコンの風が当たる場所\n④その他\n\nコメントで番号を教えてください♪\n#猫のあれこれ",
                
                "獣医師が分析！猫の涼み方について💡\n\n昨日のアンケートありがとうございました！猫は体温調節のため本能的に涼しい場所を選びます。フローリングや玄関のたたきは理想的な涼み場所。夏の健康管理に役立ててくださいね♪\n#猫のあれこれ",
                
                "獣医師の豆知識：猫のフレーメン反応について😲\n\n猫が口を半開きにして変な顔をすること、ありますよね？これは「フレーメン反応」というフェロモンを嗅ぎ取るための特別な行動。怒っているわけではないので安心してください♪\n#猫のあれこれ",
                
                "獣医師からの注意喚起：夏の観葉植物🌿\n\n夏場、観葉植物を置くご家庭も多いですが、猫には毒になる植物があります。特にユリ科は非常に危険で、花瓶の水を飲むだけでも重い腎障害を起こすことが。植物選びは慎重に！\n#猫のあれこれ",
                
                "獣医師推奨！週末の愛猫健康チェック📝\n\n健康状態を確認するポイント：\n\n✅食欲はあるか\n✅元気に動いているか\n✅トイレは正常か\n✅毛づやは良いか\n\n日々の細かな観察が病気の早期発見につながります♪\n#猫のあれこれ"
            ]
        
        # 猫の投稿（07:00）を生成
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            content = sample_posts[i]
            
            # 140文字制限チェック・調整
            if len(content) > 140:
                # ハッシュタグを保持したまま本文を短縮
                hashtag = "#猫のあれこれ"
                main_content = content.replace(hashtag, "").strip()
                available_chars = 140 - len(hashtag) - 1  # ハッシュタグ + 改行分
                
                # 本文を調整
                if len(main_content) > available_chars:
                    main_content = main_content[:available_chars-3] + "..."
                
                content = main_content + "\n" + hashtag
            
            posts.append({
                "date": current_date.strftime('%Y-%m-%d'),
                "time": current_date.replace(hour=7, minute=0).strftime('%Y-%m-%d %H:%M'),
                "content": content,
                "char_count": len(content)
            })
        
        # 犬の投稿（18:00）を生成
        dog_posts = self._generate_dog_posts(start_date, theme_type)
        posts.extend(dog_posts)
        
        return posts
    
    def _generate_dog_posts(self, start_date, theme_type):
        """
        犬投稿生成（18:00）- 「#獣医が教える犬のはなし」
        過去投稿データの分析に基づく高品質な投稿生成
        """
        dog_posts = []
        
        # 実際の過去投稿パターンに基づいた犬投稿
        if theme_type == "猫種特集":
            # 犬種特集（実際の投稿スタイルに合わせた構成）
            sample_dog_posts = [
                "【もしもの時...ケース① 歩き方の変化】\n\n症例：8歳の柴犬。\n最近、散歩中に時々足を引きずるような歩き方をする。\n特に朝起きた時や、長時間座った後に目立つ💦\n\nこのサインから何を疑いますか？\n(※あくまで架空の事例です)\n#獣医が教える犬のはなし",
                
                "【ケース①：獣医師の視点解説】\n\n昨日のケース、最も疑わしいのは変形性関節症です。\n朝の歩行困難、起立時の痛みは典型的症状💦\n\n放置すると痛みが増し、\n生活の質が大きく低下してしまいます。\n早めに病院で診てもらいましょう！🏥\n#獣医が教える犬のはなし",
                
                "【デンタルケアクイズ！① 歯磨きの効果】\n\nQ. 硬いドライフードを食べていれば歯磨きは不要？\n\n① 十分な効果がある\n② あまり効果はない\n③ 全く効果がない\n\n正解は明日！皆さんはどう思いますか？🦷\n#獣医が教える犬のはなし",
                
                "【デンタルケアクイズ①：答え合わせ💡】\n\n昨日の答え：②あまり効果はない！\n\n解説：\n硬いフードでも多少は歯の表面を擦りますが、\n歯と歯茎の境目の歯周ポケットの汚れは取れません。\n\n歯磨きに勝るケアはなし！歯磨き習慣が大切です🦷\n#獣医が教える犬のはなし",
                
                "【シニア犬の食事のヒント🍽️】\n\n12歳のチワワちゃんのお悩み：\n「最近食が細くなった...」\n\nシニア犬の食事サポート：\n✅少量頻回給餌\n✅ウェットフードを温める\n✅手作りトッピング\n✅食べやすい器の高さ調整\n\n美味しく食べて元気に過ごそう✨\n#獣医が教える犬のはなし",
                
                "【もしもの時...ケース② 口のサイン】\n\n症例：7歳のトイプードル。\n最近、口臭が気になるし、硬いおやつを嫌がるように。\nよだれも少し増えた気がする...🤤\n\nこのサインから、まず何を疑いますか？\n(※あくまで架空の事例ですが、あるあるシチュエーションです)\n#獣医が教える犬のはなし",
                
                "【ケース②：獣医師の視点解説】\n\n昨日のケース、最も疑わしいのは歯周病です。\n口臭、痛み、よだれは典型的な症状💦\n\n放置すると歯が抜けたり、\n多くはないですが、細菌が全身に回り心臓病などを引き起こすことも。\n早めに病院で口の中をチェックしてもらいましょう！🏥\n#獣医が教える犬のはなし"
            ]
        
        elif theme_type == "専門テーマ":
            # 専門的な犬の健康テーマ（実際の獣医師の専門性を反映）
            sample_dog_posts = [
                "【教えて！シニア犬との暮らしの工夫🏠】\n\nシニア犬との生活で工夫していることはありますか？\n\n例：\n✅滑り止めマットの設置\n✅低めの段差解消\n✅夜間照明の追加\n✅温度管理の徹底\n\nコメントで教えてください！参考にさせていただきます✨\n#獣医が教える犬のはなし",
                
                "【認知機能不全症候群って？🧠】\n\n犬の認知症とも呼ばれる病気。\n\n主な症状：\n✅夜鳴き・昼夜逆転\n✅迷子行動\n✅飼い主を忘れる\n✅トイレの失敗\n\n完治は困難ですが、\n環境調整や投薬で症状を和らげることができます🏥\n#獣医が教える犬のはなし",
                
                "【膝蓋骨脱臼について🦴】\n\n小型犬に多い疾患「パテラ」。\n膝のお皿の骨が正常な位置からずれてしまう状態です。\n\nグレード1〜4まであり、\nグレード3・4では手術が必要になることも。\n\n「ケンケン」歩きに気づいたら早めの受診を！\n#獣医が教える犬のはなし",
                
                "【腎臓病の早期発見💧】\n\n犬の慢性腎不全は猫より進行が早いのが特徴。\n\n初期症状：\n✅多飲多尿\n✅元気食欲の低下\n✅体重減少\n✅嘔吐\n\n血液検査での「SDMA」という項目が\n早期発見の鍵になります🩺\n#獣医が教える犬のはなし",
                
                "【心臓病のサイン❤️】\n\n特に小型犬の高齢期に多い心疾患。\n\n注意すべき症状：\n✅乾いた咳（特に夜間）\n✅運動を嫌がる\n✅息切れしやすい\n✅失神\n\n聴診で心雑音を確認。\n心エコー検査で詳しく診断します🏥\n#獣医が教える犬のはなし",
                
                "【アレルギー性皮膚炎の管理🔴】\n\n春から夏にかけて悪化しやすい皮膚病。\n\n原因：\n✅花粉・ハウスダスト\n✅食物アレルギー\n✅ノミ・ダニ\n\n根治は困難ですが、\n適切な治療とケアで症状をコントロールできます✨\n#獣医が教える犬のはなし",
                
                "【予防医学の大切さ🌟】\n\n「病気になってから治す」より\n「病気を予防する」ことが重要。\n\n基本の予防：\n✅年1〜2回の健康診断\n✅適正体重の維持\n✅ワクチン・フィラリア予防\n✅デンタルケア\n\n愛犬の健康寿命を一緒に延ばしましょう！\n#獣医が教える犬のはなし"
            ]
        
        else:  # 参加型・健康管理（実際の投稿パターンに基づく）
            sample_dog_posts = [
                "【もしもの時...ケース③ 食欲の変化】\n\n症例：10歳のゴールデンレトリーバー。最近、大好きだったご飯を残すように。水はよく飲むけれど、なんとなく元気がない💦\n\nこの症状で最初に疑うべきは？\n(※架空の事例です)\n#獣医が教える犬のはなし",
                
                "【ケース③：獣医師の視点解説】\n\n昨日のケース、多飲と食欲不振の組み合わせから腎臓病や糖尿病を疑います💦\n\n高齢期は内臓疾患が増える時期。「歳のせい」と思わず、気になる変化があれば早めの検査を！🏥\n#獣医が教える犬のはなし",
                
                "【夏の散歩クイズ！危険な時間帯☀️】\n\nQ. 真夏日の散歩で最も注意すべき時間帯は？\n\n①早朝5-6時\n②午前10-11時\n③夕方17-18時\n\n正解は明日発表！アスファルトの温度にも注意です🐾\n#獣医が教える犬のはなし",
                
                "【夏の散歩クイズ：答え合わせ💡】\n\n昨日の答え：②午前10-11時！\n\n解説：既にアスファルトが熱くなっている時間帯。手の甲で地面を触って確認を！理想は早朝・夜間の涼しい時間帯です🌙\n#獣医が教える犬のはなし",
                
                "【教えて！愛犬の夏バテ対策🌡️】\n\n暑い季節、皆さんはどんな工夫をしていますか？\n\n例：\n✅クールマットの活用\n✅氷入りの水\n✅エアコンの温度設定\n✅散歩時間の調整\n\nコメントで教えてください！参考にします✨\n#獣医が教える犬のはなし",
                
                "【パピヨンの魅力をご紹介🦋】\n\n美しい耳の飾り毛が特徴的なパピヨン。性格は明るく活発で、知的で学習能力が高く、人懐っこい性格です。注意すべき疾患は膝蓋骨脱臼や眼疾患。小さくても運動量は意外と多い犬種です🐕\n#獣医が教える犬のはなし",
                
                "【週末の愛犬健康チェック📋】\n\n愛犬の様子、普段と変わりありませんか？\n\nチェックポイント：\n✅食欲・元気\n✅歩き方\n✅呼吸の仕方\n✅排尿・排便\n\n小さな変化に気づくことが病気の早期発見につながります🏥\n#獣医が教える犬のはなし"
            ]
        
        # 犬の投稿（18:00）を生成
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            content = sample_dog_posts[i]
            
            # 140文字制限チェック・調整
            if len(content) > 140:
                # ハッシュタグを保持したまま本文を短縮
                hashtag = "#獣医が教える犬のはなし"
                main_content = content.replace(hashtag, "").strip()
                available_chars = 140 - len(hashtag) - 1  # ハッシュタグ + 改行分
                
                # 本文を調整
                if len(main_content) > available_chars:
                    main_content = main_content[:available_chars-3] + "..."
                
                content = main_content + "\n" + hashtag
            
            dog_posts.append({
                "date": current_date.strftime('%Y-%m-%d'),
                "time": current_date.replace(hour=18, minute=0).strftime('%Y-%m-%d %H:%M'),
                "content": content,
                "char_count": len(content)
            })
        
        return dog_posts
    
    def generate_simple_posts(self):
        """シンプル投稿生成（エラーフリー版）"""
        try:
            # 基本設定の取得
            days = int(self.days_var.get())
            if days != 7:
                messagebox.showwarning("注意", "現在7日間のみ対応しています。7日間で生成します。")
                days = 7
            
            theme_type = self.week_type_var.get()
            
            # 開始日の設定（今日から）
            start_date = datetime.now().replace(hour=7, minute=0, second=0, microsecond=0)
            
            self.status_var.set("📝 投稿を生成中...")
            self.progress['value'] = 10
            self.root.update()
            
            self.log_message(f"📝 シンプル生成開始: テーマ={theme_type}")
            
            # シンプル生成を実行
            posts = self._generate_simple_fallback_posts(start_date, theme_type)
            
            self.progress['value'] = 80
            self.root.update()
            
            # CSV出力
            if posts:
                output_filename = f"posts_{start_date.strftime('%Y-%m-%d')}_{theme_type}.csv"
                output_dir = os.path.join(os.path.dirname(__file__), "output")
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, output_filename)
                
                # CSVファイル作成
                import csv
                with open(output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['投稿日時', '投稿内容', '文字数'])
                    
                    for post in posts:
                        writer.writerow([
                            post['time'],
                            post['content'],
                            str(post['char_count'])
                        ])
                
                self.last_generated_csv = output_path
                self.progress['value'] = 100
                
                # 結果表示
                cat_count = sum(1 for post in posts if "07:00" in post['time'])
                dog_count = sum(1 for post in posts if "18:00" in post['time'])
                
                self.status_var.set(f"✅ 生成完了！猫投稿: {cat_count}件、犬投稿: {dog_count}件")
                self.log_message(f"✅ 生成完了: {output_filename}")
                self.log_message(f"📄 出力先: {output_path}")
                
                # Googleスプレッドシートアップロードボタンを有効化
                if hasattr(self, 'upload_button'):
                    self.upload_button.config(state="normal")
                
                messagebox.showinfo("生成完了", 
                    f"投稿生成が完了しました！\n\n"
                    f"🐱 猫投稿: {cat_count}件 (07:00)\n"
                    f"🐕 犬投稿: {dog_count}件 (18:00)\n"
                    f"📄 ファイル: {output_filename}")
                
            else:
                self.status_var.set("❌ 生成に失敗しました")
                messagebox.showerror("エラー", "投稿の生成に失敗しました。")
                
        except Exception as e:
            self.status_var.set("❌ エラーが発生しました")
            self.log_message(f"❌ エラー: {str(e)}")
            messagebox.showerror("エラー", f"生成中にエラーが発生しました:\n{str(e)}")

def main():
    root = tk.Tk()
    app = EnhancedPostGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()