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

class EnhancedPostGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("VET-Assistant2 強化版投稿生成ツール")
        self.root.geometry("800x700")
        
        # 重複監視システム
        self.duplicate_monitor = AdvancedDuplicateMonitor()
        
        # 基本設定
        self.tweets_file_path = r"C:\Users\souhe\Desktop\X過去投稿\data\tweets.js"
        self.max_regeneration_attempts = 5  # 最大再生成回数
        
        # コンテンツプール
        self.content_pools = {
            'cat_questions': [],
            'cat_health': [],
            'cat_behavior': [],
            'cat_breeds': [],
            'dog_cases': [],
            'dog_health': [],
            'dog_general': []
        }
        
        self.setup_ui()
        self.initialize_enhanced_content_pools()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # タイトル
        title_label = ttk.Label(main_frame, text="VET-Assistant2 強化版投稿生成ツール", 
                               font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # 重複監視状況
        stats_frame = ttk.LabelFrame(main_frame, text="重複監視システム状況", padding="10")
        stats_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 15))\n        
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
        
        # 重複チェック設定
        ttk.Label(settings_frame, text="重複チェック期間:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.check_months_var = tk.StringVar(value="6")
        months_combo = ttk.Combobox(settings_frame, textvariable=self.check_months_var, width=10)
        months_combo['values'] = ("3", "6", "12", "24")
        months_combo.grid(row=1, column=1, sticky=tk.W, pady=5)
        ttk.Label(settings_frame, text="か月前まで").grid(row=1, column=2, sticky=tk.W, pady=5)
        
        # 類似度閾値
        ttk.Label(settings_frame, text="類似度閾値:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.similarity_var = tk.StringVar(value="65")
        similarity_combo = ttk.Combobox(settings_frame, textvariable=self.similarity_var, width=10)
        similarity_combo['values'] = ("50", "60", "65", "70", "75", "80")
        similarity_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        ttk.Label(settings_frame, text="% 以上で重複判定").grid(row=2, column=2, sticky=tk.W, pady=5)
        
        # 生成ボタン
        self.generate_button = ttk.Button(main_frame, text="🚀 重複監視付き生成開始", 
                                        command=self.generate_posts_with_monitoring)
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
        
        # 結果表示
        result_frame = ttk.LabelFrame(main_frame, text="生成結果", padding="10")
        result_frame.grid(row=7, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        
        self.result_text = tk.Text(result_frame, height=12, width=90, font=("Consolas", 9))
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        result_scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
        result_scrollbar.grid(row=0, column=1, sticky='ns')
        self.result_text.configure(yscrollcommand=result_scrollbar.set)
        
        # グリッドの重み設定
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        main_frame.rowconfigure(7, weight=1)
        
    def initialize_enhanced_content_pools(self):
        """強化されたコンテンツプールを初期化"""
        
        # 猫の質問系（50パターン）
        self.content_pools['cat_questions'] = [
            "獣医師に教えて！愛猫の寝る場所は？😴\\n\\n【質問】あなたの猫ちゃんはどこで寝ることが多いですか？\\n\\n①飼い主のベッド\\n②専用ベッド\\n③段ボール箱\\n④高い場所\\n⑤その他（教えて！）\\n\\n場所選びにも理由があるんです♪\\n#猫のあれこれ",
            
            "猫の食事時間クイズ！🍽️\\n\\n【質問】愛猫の食事回数は？\\n\\n①1日1回\\n②1日2回\\n③1日3回以上\\n④決まっていない\\n\\n年齢によって理想的な回数は変わります。\\nみなさんの猫ちゃんはどうですか？\\n#猫のあれこれ",
            
            "愛猫の「変わった好み」ありませんか？🤔\\n\\n【質問】うちの子だけ？と思う愛猫の好みは？\\n\\n①特定の音に反応\\n②変わった食べ物好き\\n③特定の場所へのこだわり\\n④その他（詳しく！）\\n\\n猫の個性、面白いですよね✨\\n#猫のあれこれ",
            
            "猫の遊び方アンケート🎾\\n\\n【質問】愛猫が一番喜ぶ遊びは？\\n\\n①猫じゃらし\\n②ボール\\n③段ボール\\n④かくれんぼ\\n⑤その他（教えて！）\\n\\n年齢に合った遊びが大切です♪\\n#猫のあれこれ",
            
            "猫の健康チェック📊\\n\\n【質問】愛猫の健康診断頻度は？\\n\\n①年1回\\n②年2回\\n③調子悪い時のみ\\n④まだ受けていない\\n\\n獣医師としてのおすすめ頻度もお話しします！\\n#猫のあれこれ"
        ]
        
        # 猫の健康投稿（30パターン）
        self.content_pools['cat_health'] = [
            "【猫の腎臓病予防】水分摂取のコツ💧\\n\\n腎臓病は猫の代表的な病気。予防の鍵は水分摂取！\\n\\n✅複数の水場を設置\\n✅新鮮な水を毎日交換\\n✅ウェットフードを活用\\n✅流れる水を好む子も\\n\\n1日の目安：体重1kg当たり50-60ml\\n愛猫の水分摂取量、チェックしてみて♪\\n#猫のあれこれ",
            
            "【シニア猫の健康管理】7歳からが勝負💪\\n\\n7歳以降は人間でいう44歳。この時期からの健康管理が長生きの秘訣！\\n\\n✅定期健診（年2回）\\n✅食事の見直し\\n✅運動量の調整\\n✅環境の配慮\\n\\n早期発見・早期治療で元気な老後を！\\n#猫のあれこれ",
            
            "【猫の歯の健康】意外と見落としがち🦷\\n\\n猫も歯周病になります！3歳以上の80%に歯周病の兆候が。\\n\\n症状：\\n⚠️口臭\\n⚠️よだれ\\n⚠️食事の変化\\n⚠️頬の腫れ\\n\\n予防は歯磨きが一番。難しい場合は獣医師に相談を！\\n#猫のあれこれ",
            
            "【猫の目の健康】こんな症状に注意👁️\\n\\n目の病気は早期発見が重要！\\n\\n注意すべき症状：\\n⚠️涙や目やにの増加\\n⚠️まぶたの腫れ\\n⚠️目を擦る行動\\n⚠️瞳の色の変化\\n\\n放置すると視力に影響することも。気になったら早めに受診を！\\n#猫のあれこれ",
            
            "【猫の皮膚トラブル】原因と対策🔍\\n\\n皮膚病は猫の診察で最も多い病気の一つ。\\n\\n主な原因：\\n✅アレルギー\\n✅寄生虫\\n✅細菌感染\\n✅ストレス\\n\\n症状：かゆみ、脱毛、湿疹\\n原因特定が治療の鍵。自己判断せず獣医師へ！\\n#猫のあれこれ"
        ]
        
        # 犬のケーススタディ（25パターン）
        self.content_pools['dog_cases'] = [
            "【ケース①：散歩の変化】\\n\\n症例：6歳のラブラドール\\n最近、散歩中に立ち止まることが多くなった。\\n以前は元気に走っていたのに、歩くペースも遅くなった🐕\\n\\n考えられる原因は？\\n（実際によくある相談です）\\n#獣医が教える犬のはなし",
            
            "【ケース②：食欲の変化】\\n\\n症例：8歳のシーズー\\n普段は食いしん坊なのに、最近フードを残すように。\\n水はよく飲むが、なんとなく元気がない💭\\n\\n何を疑いますか？\\n（複数の原因が考えられます）\\n#獣医が教える犬のはなし",
            
            "【ケース③：呼吸の変化】\\n\\n症例：5歳のフレンチブルドッグ\\n運動後の呼吸が以前より荒い。\\n舌の色も心なしか薄い気がする😰\\n\\n緊急性は？どう対処する？\\n（短頭種に多い問題です）\\n#獣医が教える犬のはなし",
            
            "【ケース④：皮膚の変化】\\n\\n症例：3歳のゴールデンレトリーバー\\n最近、体を掻く頻度が増えた。\\n毛が抜けて赤くなっている部分もある🔴\\n\\n原因として何が考えられる？\\n（春に多い相談です）\\n#獣医が教える犬のはなし",
            
            "【ケース⑤：排尿の変化】\\n\\n症例：7歳のダックスフント\\n排尿回数が増えて、時々血が混じる。\\n普段は我慢できるのに、家でも失敗することが💦\\n\\n緊急度と対処法は？\\n（オスメス関係なく起こります）\\n#獣医が教える犬のはなし"
        ]
        
        # 犬の健康投稿（20パターン）
        self.content_pools['dog_health'] = [
            "【犬の肥満対策】適正体重を保つコツ⚖️\\n\\n肥満は万病の元！適正体重維持のポイント：\\n\\n✅理想体重の把握\\n✅カロリー計算\\n✅おやつの制限\\n✅定期的な運動\\n\\n肋骨を軽く触れるのが理想的。\\n愛犬の体重管理、見直してみませんか？\\n#獣医が教える犬のはなし",
            
            "【犬の関節ケア】年齢に関係なく大切🦴\\n\\n関節の健康は生活の質に直結！\\n\\n予防のポイント：\\n✅適正体重の維持\\n✅適度な運動\\n✅滑りにくい床材\\n✅関節サプリの活用\\n\\n大型犬だけでなく小型犬でも要注意。\\n毎日の積み重ねが大切です♪\\n#獣医が教える犬のはなし",
            
            "【犬の心臓病】早期発見のサイン❤️\\n\\n心臓病は犬の死因上位の病気。\\n\\n注意すべき症状：\\n⚠️咳が出る\\n⚠️疲れやすい\\n⚠️舌の色が悪い\\n⚠️失神する\\n\\n中高齢期からリスク上昇。\\n定期検診で早期発見を！\\n#獣医が教える犬のはなし",
            
            "【犬の耳の健康】トラブル予防法👂\\n\\n耳のトラブルは犬に多い病気の一つ。\\n\\n予防のポイント：\\n✅定期的な耳掃除\\n✅湿度管理\\n✅アレルゲン除去\\n✅早期治療\\n\\n垂れ耳の犬種は特に注意！\\n日頃のケアで健康な耳を保ちましょう♪\\n#獣医が教える犬のはなし",
            
            "【シニア犬の健康管理】7歳からの注意点👴\\n\\n7歳以降は人間でいう44歳。健康管理の重要性が増します。\\n\\n注意すべき点：\\n✅定期健診の頻度アップ\\n✅食事内容の見直し\\n✅運動量の調整\\n✅認知症の予防\\n\\n早めの対策で元気な老後を！\\n#獣医が教える犬のはなし"
        ]
    
    def log_message(self, message: str):
        """ログメッセージを表示"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def generate_content_with_monitoring(self, content_type: str, animal_type: str, 
                                       topic: str = None) -> str:
        """重複監視付きコンテンツ生成"""
        
        self.duplicate_monitor.similarity_threshold = float(self.similarity_var.get()) / 100
        months_back = int(self.check_months_var.get())
        
        for attempt in range(self.max_regeneration_attempts):
            # コンテンツ生成
            if content_type == "cat_question":
                content = random.choice(self.content_pools['cat_questions'])
            elif content_type == "cat_health":
                content = random.choice(self.content_pools['cat_health'])
            elif content_type == "dog_case":
                content = random.choice(self.content_pools['dog_cases'])
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
        
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            
            # 猫投稿（7:00）
            self.log_message(f"📅 {current_date.strftime('%Y-%m-%d')} 猫投稿生成中...")
            
            cat_content = self.generate_content_with_monitoring(
                "cat_question" if i % 2 == 0 else "cat_health", 
                "cat", 
                "猫の健康"
            )
            
            if cat_content:
                posts.append([
                    current_date.replace(hour=7, minute=0).strftime('%Y-%m-%d %H:%M'),
                    cat_content.replace('\\n', '\n'),
                    str(len(cat_content))
                ])
                successful_generations += 1
            else:
                failed_generations += 1
                self.log_message(f"❌ 猫投稿生成失敗 ({current_date.strftime('%Y-%m-%d')})")
            
            # 犬投稿（18:00）
            self.log_message(f"📅 {current_date.strftime('%Y-%m-%d')} 犬投稿生成中...")
            
            dog_content = self.generate_content_with_monitoring(
                "dog_case" if i % 2 == 0 else "dog_health",
                "dog",
                "犬の健康"
            )
            
            if dog_content:
                posts.append([
                    current_date.replace(hour=18, minute=0).strftime('%Y-%m-%d %H:%M'),
                    dog_content.replace('\\n', '\n'),
                    str(len(dog_content))
                ])
                successful_generations += 1
            else:
                failed_generations += 1
                self.log_message(f"❌ 犬投稿生成失敗 ({current_date.strftime('%Y-%m-%d')})")
            
            # 進捗更新
            self.progress['value'] = (i + 1) / days * 100
            self.root.update()
        
        # 結果出力
        if posts:
            output_filename = f"enhanced_posts_{start_date.strftime('%Y-%m-%d')}_{week_type}.csv"
            output_dir = "/home/souhei/VET-Assistant2/output"
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
            
        else:
            self.status_var.set("❌ 生成失敗: 重複のため生成できませんでした")
            messagebox.showerror("エラー", "重複のため投稿を生成できませんでした")
        
        self.progress['value'] = 0

def main():
    root = tk.Tk()
    app = EnhancedPostGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()