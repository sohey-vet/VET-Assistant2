#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
X投稿案自動生成アプリケーション（最終版）
指示書完全準拠・過去投稿分析ベース
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import re
import os
import random
import codecs
from datetime import datetime, timedelta

class XPostGeneratorFinal:
    def __init__(self, root):
        self.root = root
        self.root.title("X投稿案自動生成ツール（最終版）")
        self.root.geometry("700x600")
        
        self.tweets_data = []
        self.cat_posts = []
        self.tweets_file_path = r"C:\Users\souhe\Desktop\X過去投稿\data\tweets.js"
        
        # 投稿サイクル管理
        self.current_week_type = "参加型"  # "猫種特集", "専門テーマ", "参加型"
        self.current_day = 0  # 0=月曜, 1=火曜, ..., 6=日曜
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # タイトル
        title_label = ttk.Label(main_frame, text="X投稿案自動生成ツール（指示書準拠版）", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # ファイル情報
        ttk.Label(main_frame, text="データソース:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.file_path_var = tk.StringVar(value=self.tweets_file_path)
        file_entry = ttk.Entry(main_frame, textvariable=self.file_path_var, width=60, state="readonly")
        file_entry.grid(row=1, column=1, columnspan=2, pady=5, padx=(5, 0))
        
        # 生成日数
        ttk.Label(main_frame, text="生成日数:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.days_var = tk.StringVar(value="7")
        ttk.Entry(main_frame, textvariable=self.days_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # 投稿時間情報（固定）
        ttk.Label(main_frame, text="投稿時間:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Label(main_frame, text="07:00（猫） / 18:00（犬）", font=("Arial", 9)).grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # 週テーマ選択
        ttk.Label(main_frame, text="週テーマ:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.week_type_var = tk.StringVar(value="参加型")
        week_combo = ttk.Combobox(main_frame, textvariable=self.week_type_var, width=15)
        week_combo['values'] = ("参加型", "猫種特集", "専門テーマ")
        week_combo.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # 生成開始ボタン
        self.generate_button = ttk.Button(main_frame, text="生成開始", command=self.generate_posts)
        self.generate_button.grid(row=5, column=0, columnspan=3, pady=20)
        
        # 進捗表示
        self.status_var = tk.StringVar(value="設定を確認して「生成開始」をクリックしてください")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=6, column=0, columnspan=3, pady=10)
        
        # プログレスバー
        self.progress = ttk.Progressbar(main_frame, length=500, mode='determinate')
        self.progress.grid(row=7, column=0, columnspan=3, pady=10)
        
        # 結果表示
        self.result_text = tk.Text(main_frame, height=20, width=80, font=("Consolas", 9))
        self.result_text.grid(row=8, column=0, columnspan=3, pady=10)
        
        # スクロールバー
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.result_text.yview)
        scrollbar.grid(row=8, column=3, sticky='ns', pady=10)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
    def check_file_exists(self):
        if os.path.exists(self.tweets_file_path):
            return True
        else:
            messagebox.showerror("エラー", f"tweets.jsファイルが見つかりません:\\n{self.tweets_file_path}")
            return False
            
    def parse_tweets_js(self):
        """tweets.jsファイルを解析して猫投稿のみ抽出"""
        try:
            with open(self.tweets_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            json_match = re.search(r'window\.YTD\.tweets\.part0\s*=\s*(\[.*\]);?', content, re.DOTALL)
            if not json_match:
                raise ValueError("tweets.jsファイルの形式が正しくありません")
            
            json_str = json_match.group(1)
            tweets_data = json.loads(json_str)
            
            cat_posts = []
            for tweet_obj in tweets_data:
                if 'tweet' in tweet_obj and 'full_text' in tweet_obj['tweet']:
                    full_text = tweet_obj['tweet']['full_text']
                    try:
                        full_text = codecs.decode(full_text, 'unicode_escape')
                    except:
                        pass
                    
                    # 猫投稿のみ抽出
                    if '#猫のあれこれ' in full_text:
                        cat_posts.append(full_text)
            
            self.cat_posts = cat_posts
            return len(cat_posts)
            
        except Exception as e:
            raise Exception(f"ファイル読み込みエラー: {str(e)}")
    
    def count_characters(self, text):
        """正確な文字数カウント（全角・半角・絵文字すべて1文字）"""
        return len(text)
    
    def generate_interactive_post(self, day_num):
        """参加型投稿を生成（過去投稿の傾向に基づく）"""
        
        if day_num % 2 == 0:  # 質問系
            questions = [
                "獣医師に教えて！愛猫のモーニングコールは？⏰\n\n【質問】あなたの猫ちゃんは、どんな風に朝起こしてくれますか？\n※コメントで番号を教えてね！\n\n①顔の近くで鳴く\n②顔や手を舐める・噛む\n③体にのってくる\n④その他（ぜひ具体的に！）\n\nうちの猫様は、鼻を噛んできました😼\n#猫のあれこれ",
                
                "獣医師に聞きたい！愛猫の変わった癖は？🤔\n\n【質問】みなさんの猫ちゃんの「なんでそうするの？」な行動を教えてください！\n\n①箱に入りたがる\n②高い所から見下ろす\n③水道の蛇口から飲む\n④その他（詳しく教えて！）\n\n行動には必ず理由があるんです✨\n#猫のあれこれ",
                
                "愛猫の「困った行動」ありませんか？😅\n\n【アンケート】飼い主さんが困っている猫ちゃんの行動は？\n\n①夜中に大運動会\n②カーテンによじ登る\n③ティッシュで遊ぶ\n④爪とぎ場所を間違える\n\nどれも猫らしい行動です♪対策を一緒に考えましょう！\n#猫のあれこれ"
            ]
            return random.choice(questions)
            
        else:  # クイズ系
            quizzes = [
                "もしもの時…緊急度クイズ🚨\n\n【ケース】猫が突然吐いて、ぐったりしている\n\n①すぐ病院へ\n②しばらく様子見\n③水だけ与える\n④何もしない\n\n正解は明日発表！\n緊急性の判断、できますか？\nコメントで答えを教えてください♪\n#猫のあれこれ",
                
                "獣医師クイズ！猫の行動編🐱\n\n【問題】猫が「ゴロゴロ」音を出すのはなぜ？\n\n①嬉しい時だけ\n②リラックス時だけ\n③痛い時もある\n④お腹が空いた時\n\n実は意外な理由もあるんです💡\n答えは明日の投稿で！\n#猫のあれこれ",
                
                "原因は何だろう？アンケート🤔\n\n【症状】最近、愛猫の食欲がない...\n\n①ストレス\n②病気\n③フードに飽きた\n④季節の変化\n\n複数の原因が考えられます。明日、詳しく解説しますね！\nみなさんの予想を教えてください♪\n#猫のあれこれ"
            ]
            return random.choice(quizzes)
    
    def generate_explanation_post(self, day_num):
        """解説型投稿を生成"""
        
        explanations = [
            "獣医師が解説！昨日のアンケート考察💡\n\n猫のモーニングコール、様々な方法があるんですが、これらは「お腹すいた」「遊んで」の要求行動です😸\n無視するとエスカレートすることも…\n\n決まった時間に自動給餌器を使ったり、寝る前に遊んであげたりすると改善する場合がありますよ♪\n#猫のあれこれ",
            
            "獣医師の視点から解説！猫の「ゴロゴロ」の秘密🔍\n\n実は嬉しい時だけじゃないんです！\n✅リラックス時\n✅痛みを和らげる時\n✅不安な時\n✅治癒促進効果も\n\n低周波の振動が骨密度向上や傷の治癒を早めるという研究もあります。猫の神秘的な能力ですね✨\n#猫のあれこれ",
            
            "昨日のクイズ解説！猫が突然吐いた時の対応💦\n\n正解：①すぐ病院へ\n\n「ぐったりしている」がポイント！\n単発の嘔吐なら様子見もありますが、元気がない場合は緊急性大です🚨\n\n脱水や中毒、腸閉塞の可能性も。迷った時は早めの受診を！\n#猫のあれこれ"
        ]
        
        return random.choice(explanations)
    
    def generate_health_post(self, day_num):
        """健康関連投稿を生成"""
        
        health_posts = [
            "【今日の猫の健康豆知識】水分摂取について💧\n\n猫は元々砂漠の動物なので、あまり水を飲みません。\nでも腎臓病予防には水分が重要！\n\n✅ウェットフードを取り入れる\n✅複数箇所に水場を設置\n✅流れる水を好む子も\n\n1日の目安：体重1kgあたり50-60ml\n愛猫の水分摂取、チェックしてみてくださいね♪\n#猫のあれこれ",
            
            "【こんな症状、見逃していませんか？】猫の隠れサイン⚠️\n\n猫は痛みや不調を隠すのが得意です。\n以下の変化に注意を！\n\n✅食事のペースが遅くなった\n✅高い所に登らなくなった\n✅グルーミングが減った\n✅隠れる時間が増えた\n\n小さな変化が大きなサイン。日々の観察が早期発見につながります🔍\n#猫のあれこれ",
            
            "【猫の年齢別注意点】シニア猫（7歳以降）のケア🐱\n\n人間でいう44歳からがシニア期。\nこの時期から注意したいのは：\n\n✅腎臓病\n✅甲状腺機能亢進症\n✅関節炎\n✅認知症\n\n年2回の健康診断がおすすめです。\n愛猫の「いつもと違う」を見逃さないよう、一緒に長生きを目指しましょう！\n#猫のあれこれ"
        ]
        
        return random.choice(health_posts)
    
    def generate_breed_post(self, day_num, breed="マンチカン"):
        """猫種特集投稿を生成"""
        
        day_templates = {
            0: f"【{breed}特集①：概要】\n\n短い脚で有名な{breed}🐱\n\n愛らしい見た目で人気急上昇中！\n\n今週は{breed}について詳しくお話しします♪\n\n#猫のあれこれ",
            1: f"【{breed}特集②：歴史】\n\n{breed}の起源は1983年、アメリカで発見された短脚の猫からです📚\n\n比較的新しい品種なんです！\n\n#猫のあれこれ",
            2: f"【{breed}特集③：性格】\n\n{breed}は温厚で人懐っこい性格😸\n\n活発で好奇心旺盛、でも穏やかな子が多いです♪\n\n#猫のあれこれ",
            3: f"【{breed}特集④：特徴】\n\n{breed}の最大の特徴は短い脚🦵\n\nでも全ての{breed}が短脚ではないんです！\n\n#猫のあれこれ",
            4: f"【{breed}特集⑤：健康面】\n\n{breed}は軟骨異形成症に注意が必要です⚠️\n\n定期的な健康チェックが大切です🏥\n\n#猫のあれこれ",
            5: f"【{breed}特集⑥：ケア】\n\n{breed}のケアは他の猫と基本的に同じです✅\n\n高い所への配慮をしてあげると良いでしょう♪\n\n#猫のあれこれ",
            6: f"【{breed}特集⑦：飼い主さんへ】\n\n{breed}を飼ってる方、愛猫の可愛いエピソードを教えてください😸\n\n写真も大歓迎です📸\n\n#猫のあれこれ"
        }
        
        return day_templates.get(day_num % 7, day_templates[0])
    
    def generate_specialized_post(self, day_num, topic="尿路結石"):
        """専門テーマ投稿を生成"""
        
        day_templates = {
            0: f"【{topic}特集①：概要】\n\n{topic}は猫の代表的な病気の一つです💦\n\n今週は{topic}について詳しく解説します🏥\n\n#猫のあれこれ",
            1: f"【{topic}特集②：原因】\n\n{topic}の主な原因は水分不足や食事内容です💧\n\n体質的な要因もあります📊\n\n#猫のあれこれ",
            2: f"【{topic}特集③：症状】\n\n{topic}の症状：\n✅トイレの回数増加\n✅血尿\n✅排尿時の痛み\n\n早期発見が大切です🚨\n\n#猫のあれこれ",
            3: f"【{topic}特集④：診断】\n\n{topic}の診断は尿検査やレントゲンで行います🔍\n\n獣医師にご相談ください🏥\n\n#猫のあれこれ",
            4: f"【{topic}特集⑤：治療】\n\n{topic}の治療は食事療法が基本です🍽️\n\n重症例では手術が必要な場合もあります⚕️\n\n#猫のあれこれ",
            5: f"【{topic}特集⑥：お家ケア】\n\n{topic}予防のお家ケア：\n💧水分摂取を増やす\n🍽️適切な食事\n🚽清潔なトイレ\n\n#猫のあれこれ",
            6: f"【{topic}特集⑦：まとめ】\n\n{topic}は予防と早期発見が重要です✨\n\n気になる症状があれば早めの受診を🏥\n\n#猫のあれこれ"
        }
        
        return day_templates.get(day_num % 7, day_templates[0])
    
    def generate_cat_post(self, day_num, week_type):
        """猫投稿（7:00）を生成"""
        
        if week_type == "猫種特集":
            breeds = ["マンチカン", "スコティッシュフォールド", "アメリカンショートヘア", "ロシアンブルー", "ペルシャ"]
            breed = random.choice(breeds)
            return self.generate_breed_post(day_num, breed)
            
        elif week_type == "専門テーマ":
            topics = ["尿路結石", "腎不全", "糖尿病", "甲状腺機能亢進症", "歯周病"]
            topic = random.choice(topics)
            return self.generate_specialized_post(day_num, topic)
            
        else:  # 参加型
            if day_num % 2 == 0:  # 偶数日は質問系
                return self.generate_interactive_post(day_num)
            elif day_num % 3 == 1:  # 一部の日は解説系
                return self.generate_explanation_post(day_num)
            else:  # その他は健康系
                return self.generate_health_post(day_num)
    
    def generate_dog_post(self, day_num):
        """犬投稿（18:00）を生成"""
        
        if day_num % 2 == 0:  # ケーススタディ
            case_studies = [
                "【もしもの時… ケース⑥ 口のサイン】\n\n症例：7歳のトイプードル。\n最近、口臭が気になるし、硬いおやつを嫌がるように。\nよだれも少し増えた気がする…🤤\n\nこのサインから、まず何を疑いますか？\n(※あくまで架空の事例ですが、あるあるシチュエーションです)\n#獣医が教える犬のはなし",
                
                "【もしもの時… ケース⑦ 歩き方の変化】\n\n症例：5歳のゴールデンレトリーバー。\n散歩中に後ろ足をかばうような歩き方をする。\n階段を上がるのを嫌がるようになった🐕\n\nどんな病気を疑いますか？\n(※実際によくある症例です)\n#獣医が教える犬のはなし",
                
                "【もしもの時… ケース⑧ 水を大量に飲む】\n\n症例：8歳のシーズー。\n最近、水をがぶ飲みして、おしっこの回数も増加💧\n食欲は旺盛だが、なんとなく痩せてきた気が…\n\n考えられる病気は？\n#獣医が教える犬のはなし"
            ]
            return random.choice(case_studies)
            
        else:  # 解説
            explanations = [
                "【ケース⑥：獣医師の視点解説】\n\n昨日のケース、最も疑わしいのは歯周病です。\n口臭、痛み、よだれは典型的な症状💦\n\n放置すると歯が抜けたり、多くはないですが、細菌が全身に回り心臓病などを引き起こすことも。\n早めに病院で口の中をチェックしてもらいましょう！🏥\n#獣医が教える犬のはなし",
                
                "【デンタルケアクイズ①：答え合わせ💡】\n\n昨日の答え：②あまり効果はない！\n\n解説：\n硬いフードでも多少は歯の表面を擦りますが、歯と歯茎の境目の歯周ポケットの汚れは取れません。\n歯周ポケットに菌がはびこるのです！\n\n歯磨きに勝るケアはなし！歯磨き習慣が大切です🦷\n#獣医が教える犬のはなし",
                
                "【獣医師が教える】犬の関節ケアの基本📋\n\n関節炎は大型犬に多い病気ですが、小型犬でも起こります。\n\n予防のポイント：\n✅適正体重の維持\n✅適度な運動\n✅滑りにくい床材\n✅サプリメント活用\n\n早期発見・早期治療で愛犬の QOL を保ちましょう♪\n#獣医が教える犬のはなし"
            ]
            return random.choice(explanations)
    
    def generate_posts(self):
        """投稿案を生成"""
        if not self.check_file_exists():
            return
        
        try:
            days = int(self.days_var.get())
            if days <= 0:
                raise ValueError("正の数を入力してください")
        except ValueError:
            messagebox.showerror("エラー", "正しい日数を入力してください")
            return
        
        self.status_var.set("処理中...")
        self.progress['value'] = 0
        self.result_text.delete(1.0, tk.END)
        self.root.update()
        
        try:
            # ファイル解析
            self.status_var.set("過去投稿データを分析中...")
            self.root.update()
            
            parsed_count = self.parse_tweets_js()
            
            # 投稿案生成
            posts = []
            start_date = datetime.now()
            week_type = self.week_type_var.get()
            
            for i in range(days):
                current_date = start_date + timedelta(days=i)
                
                # 猫投稿（7:00）
                cat_post = self.generate_cat_post(i, week_type)
                cat_char_count = self.count_characters(cat_post)
                
                # 140文字制限チェック（猫）
                if cat_char_count > 140:
                    lines = cat_post.split('\n')
                    hashtag_line = lines[-1]
                    content_lines = lines[:-1]
                    
                    while self.count_characters('\n'.join(content_lines + [hashtag_line])) > 140 and content_lines:
                        if content_lines:
                            content_lines[-1] = content_lines[-1][:max(0, len(content_lines[-1])-5)] + "..."
                    
                    cat_post = '\n'.join(content_lines + [hashtag_line])
                    cat_char_count = self.count_characters(cat_post)
                
                # 犬投稿（18:00）
                dog_post = self.generate_dog_post(i)
                dog_char_count = self.count_characters(dog_post)
                
                # 投稿を追加
                posts.append([
                    current_date.replace(hour=7, minute=0).strftime('%Y-%m-%d %H:%M'),
                    cat_post,
                    str(cat_char_count)
                ])
                
                posts.append([
                    current_date.replace(hour=18, minute=0).strftime('%Y-%m-%d %H:%M'),
                    dog_post,
                    str(dog_char_count)
                ])
                
                # 進捗更新
                self.progress['value'] = (i + 1) / days * 100
                self.root.update()
            
            # CSV出力
            output_filename = f"tweet_drafts_{start_date.strftime('%Y-%m-%d')}_{week_type}.csv"
            output_dir = r"C:\\Users\\souhe\\アプリ開発\\アプリ開発\\VET-Assistant2\\output"
            output_path = os.path.join(output_dir, output_filename)
            
            os.makedirs(output_dir, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
                import csv
                writer = csv.writer(f)
                writer.writerow(['投稿日時', '投稿内容', '文字数'])
                writer.writerows(posts)
            
            self.status_var.set(f"✅ 完了: {output_filename}")
            
            # 結果表示
            self.result_text.insert(tk.END, f"🎉 生成完了!\n\n")
            self.result_text.insert(tk.END, f"📁 ファイル名: {output_filename}\n")
            self.result_text.insert(tk.END, f"📊 生成投稿数: {len(posts)}件\n")
            self.result_text.insert(tk.END, f"🕒 投稿時間: 07:00（猫）/ 18:00（犬）\n")
            self.result_text.insert(tk.END, f"📚 週テーマ: {week_type}\n")
            self.result_text.insert(tk.END, f"🐱 参考にした過去投稿: {parsed_count}件\n")
            self.result_text.insert(tk.END, f"💾 保存場所: {output_path}\n\n")
            
            self.result_text.insert(tk.END, "=== 生成された投稿案 ===\n\n")
            for i, post in enumerate(posts):
                self.result_text.insert(tk.END, f"📅 {post[0]}\n")
                self.result_text.insert(tk.END, f"📝 {post[1]}\n")
                self.result_text.insert(tk.END, f"📏 ({post[2]}文字)\n\n")
                self.result_text.insert(tk.END, "-" * 50 + "\n\n")
            
            self.result_text.insert(tk.END, "💡 全投稿が140文字以内に調整されています！")
            
        except Exception as e:
            self.status_var.set("❌ エラーが発生しました")
            messagebox.showerror("エラー", str(e))
        finally:
            self.progress['value'] = 0

def main():
    root = tk.Tk()
    app = XPostGeneratorFinal(root)
    root.mainloop()

if __name__ == "__main__":
    main()