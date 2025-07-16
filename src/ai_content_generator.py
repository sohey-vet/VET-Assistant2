#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI駆動型コンテンツ生成システム
高品質な獣医師向けSNS投稿を動的に生成
"""

import random
from datetime import datetime, timedelta
import json

class AIContentGenerator:
    def __init__(self):
        # 週テーマの定義
        self.week_themes = {
            "参加型": {
                "description": "クイズ、アンケート、参加型コンテンツ中心",
                "patterns": ["quiz", "survey", "interactive", "show_and_tell"]
            },
            "猫種特集": {
                "description": "特定の猫種について深掘り",
                "breeds": ["ロシアンブルー", "メインクーン", "ペルシャ", "スコティッシュフォールド", "アメリカンショートヘア", "ラグドール", "ベンガル", "ノルウェージャンフォレストキャット"]
            },
            "専門テーマ": {
                "description": "獣医学的専門知識を7日間で詳解",
                "topics": ["慢性腎臓病", "歯周病", "アレルギー性皮膚炎", "肥満管理", "ワクチン", "寄生虫予防", "高齢猫ケア"]
            },
            "健康管理": {
                "description": "日常的な健康管理とケア方法",
                "areas": ["食事管理", "運動管理", "グルーミング", "ストレス管理", "環境整備"]
            }
        }
        
        # 専門的な医学知識データベース
        self.medical_knowledge = {
            "慢性腎臓病": {
                "定義": "腎機能が3ヶ月以上にわたって低下している状態",
                "統計": "高齢猫の30-40%が罹患",
                "症状": ["多飲多尿", "体重減少", "食欲不振", "嘔吐", "毛づやの悪化"],
                "診断": ["血液検査(BUN,Cr,SDMA)", "尿検査", "超音波検査"],
                "治療": ["食事療法", "輸液療法", "投薬治療", "血圧管理"],
                "予防": ["定期健診", "適切な水分摂取", "腎臓病用フード"]
            },
            "歯周病": {
                "定義": "歯石の蓄積による歯肉の炎症と歯周組織の破壊",
                "統計": "3歳以上の猫の80%に歯周病の兆候",
                "症状": ["口臭", "歯石", "歯肉炎", "よだれ", "食事の変化"],
                "診断": ["口腔内検査", "歯科レントゲン"],
                "治療": ["歯石除去", "抗生剤", "抜歯"],
                "予防": ["歯磨き", "デンタルケア用品", "定期検診"]
            }
        }
        
        # 猫種の詳細データベース
        self.breed_database = {
            "ロシアンブルー": {
                "原産国": "ロシア",
                "特徴": ["エメラルドグリーンの瞳", "ブルーの被毛", "ロシアンスマイル", "ダブルコート"],
                "性格": ["物静か", "忠実", "人見知り", "賢明"],
                "歴史": "ロシア皇帝に愛された貴族の猫",
                "健康": ["アレルギー性皮膚炎", "ストレス性疾患"],
                "ケア": ["週1-2回ブラッシング", "カロリーコントロール", "知的な遊び"]
            },
            "メインクーン": {
                "原産国": "アメリカ",
                "特徴": ["大型", "長毛", "ふさふさの尻尾", "耳の房毛"],
                "性格": ["穏やか", "社交的", "犬のような性格", "知的"],
                "歴史": "アメリカ最古の自然発生猫種",
                "健康": ["肥大性心筋症", "股関節形成不全", "多発性嚢胞腎"],
                "ケア": ["毎日のブラッシング", "大きなトイレ", "十分な運動スペース"]
            }
        }
        
        # 文章生成テンプレート
        self.templates = {
            "quiz_start": [
                "獣医師が教える！{topic}クイズ{emoji}\n\nQ. {question}\n\n{choices}\n\n正解と解説は明日！{call_to_action}\n#猫のあれこれ",
                "これって知ってる？{topic}に関するクイズ{emoji}\n\n【問題】{question}\n\n{choices}\n\n{hint}明日、詳しく解説します！\n#猫のあれこれ"
            ],
            "quiz_answer": [
                "獣医師が解説！昨日のクイズ答え合わせ{emoji}\n\n正解は…{answer}！\n\n解説：{explanation}\n\n{additional_info}\n#猫のあれこれ",
                "昨日のクイズ、いかがでしたか？{emoji}\n\n正解：{answer}\n\n{detailed_explanation}\n\n{practical_advice}\n#猫のあれこれ"
            ],
            "survey": [
                "獣医師に教えて！{topic}{emoji}\n\n【質問】{question}\n※コメントで番号を教えてね！\n\n{choices}\n\n{call_to_action}\n#猫のあれこれ",
                "みんなで情報交換！{topic}について{emoji}\n\n{question}\n\n{choices}\n\nみなさんの愛猫はいかがですか？{follow_up}\n#猫のあれこれ"
            ]
        }

    def generate_week_content(self, start_date, theme_type, specific_topic=None):
        """
        1週間分のコンテンツを生成
        """
        if theme_type == "猫種特集":
            return self._generate_breed_week(start_date, specific_topic)
        elif theme_type == "専門テーマ":
            return self._generate_medical_week(start_date, specific_topic)
        elif theme_type == "参加型":
            return self._generate_interactive_week(start_date)
        else:
            return self._generate_health_week(start_date)

    def _generate_breed_week(self, start_date, breed_name):
        """猫種特集週の生成"""
        if breed_name not in self.breed_database:
            breed_name = random.choice(list(self.breed_database.keys()))
        
        breed_info = self.breed_database[breed_name]
        posts = []
        
        # 7日間の投稿を生成
        for day in range(7):
            current_date = start_date + timedelta(days=day)
            
            if day == 0:  # 月曜日：導入
                content = f"獣医師が教える！{breed_name}特集①🐱\n\n{self._get_breed_intro(breed_info)}\n\n今週はその魅力と特徴を詳しく解説します！\n\n皆さんの{breed_name}ちゃんとの生活も教えてくださいね。\n#猫のあれこれ"
            
            elif day == 1:  # 火曜日：歴史
                content = f"獣医師が教える！{breed_name}特集②歴史📜\n\n{self._get_breed_history(breed_info)}\n\n{self._add_historical_detail(breed_info)}\n#猫のあれこれ"
            
            elif day == 2:  # 水曜日：性格
                content = f"獣医師が教える！{breed_name}特集③性格🐈\n\n{self._get_personality_description(breed_info)}\n\n{self._add_personality_tips(breed_info)}\n#猫のあれこれ"
            
            elif day == 3:  # 木曜日：身体的特徴
                content = f"獣医師が教える！{breed_name}特集④特徴✨\n\n{self._get_physical_features(breed_info)}\n\n{self._add_feature_details(breed_info)}\n#猫のあれこれ"
            
            elif day == 4:  # 金曜日：健康管理
                content = f"獣医師が教える！{breed_name}特集⑤健康⚠️\n\n{self._get_health_info(breed_info)}\n\n{self._add_health_advice(breed_info)}\n#猫のあれこれ"
            
            elif day == 5:  # 土曜日：ケア方法
                content = f"獣医師の豆知識：{breed_name}のケア✨\n\n{self._get_care_instructions(breed_info)}\n\n{self._add_care_tips(breed_info)}\n#猫のあれこれ"
            
            else:  # 日曜日：参加型コンテンツ
                content = f"見せて！あなたの{breed_name}の魅力😊\n\n{breed_name}の飼い主さん！\n愛猫の{self._get_breed_unique_feature(breed_info)}が撮れた奇跡の一枚を見せてくれませんか？\n\n#{breed_name}見せて のハッシュタグでお待ちしています！\n#猫のあれこれ"
            
            posts.append({
                "date": current_date.strftime('%Y-%m-%d'),
                "content": content,
                "char_count": len(content)
            })
        
        return posts

    def _generate_medical_week(self, start_date, topic):
        """専門テーマ週の生成"""
        if topic not in self.medical_knowledge:
            topic = random.choice(list(self.medical_knowledge.keys()))
        
        medical_info = self.medical_knowledge[topic]
        posts = []
        
        for day in range(7):
            current_date = start_date + timedelta(days=day)
            
            if day == 0:  # 導入・定義
                content = f"獣医師が教える！猫の{topic}①：どんな病気？💧\n\n{medical_info['定義']}\n\n✅{medical_info['統計']}\n✅初期は症状が出にくい\n✅早期発見が重要\n\n今週は詳しく解説していきます。\n#猫のあれこれ"
            
            elif day == 1:  # 初期症状
                symptoms = medical_info['症状'][:3]
                symptom_list = [f"✅{symptom}" for symptom in symptoms]
                symptoms_text = "\n".join(symptom_list)
                content = f"獣医師が教える！猫の{topic}②：初期症状に注意👀\n\n以下の症状に注意が必要です：\n\n{symptoms_text}\n\n「歳のせいかな？」と思わず、変化に気づいたら早めに相談を。\n#猫のあれこれ"
            
            elif day == 2:  # 進行時の症状
                content = f"獣医師が教える！猫の{topic}③：進行時の症状⚠️\n\n病状が進行すると、より重篤な症状が現れます。\n\n{self._format_advanced_symptoms(medical_info)}\n\nこれらの症状が見られたら、緊急性が高い可能性があります。\n#猫のあれこれ"
            
            elif day == 3:  # 診断方法
                diagnostics = medical_info['診断']
                diagnostic_list = [f"✅{diag}" for diag in diagnostics]
                diagnostics_text = "\n".join(diagnostic_list)
                content = f"獣医師が教える！猫の{topic}④：診断方法🩺\n\n正確な診断のため、以下の検査を行います：\n\n{diagnostics_text}\n\n定期健診での早期発見が重要です。\n#猫のあれこれ"
            
            elif day == 4:  # 治療法
                treatments = medical_info['治療']
                treatment_list = [f"✅{treatment}" for treatment in treatments]
                treatments_text = "\n".join(treatment_list)
                content = f"獣医師が教える！猫の{topic}⑤：治療と管理💊\n\n{self._get_treatment_intro(topic)}\n\n{treatments_text}\n\n獣医師とよく相談し、その子に合った治療を。\n#猫のあれこれ"
            
            elif day == 5:  # 家庭でのケア
                content = f"獣医師の豆知識：{topic}のお家でのケア🏠\n\n{self._get_home_care_intro(topic)}\n\n{self._format_home_care_tips(medical_info)}\n\n日々のケアが症状の改善につながります。\n#猫のあれこれ"
            
            else:  # 予防とまとめ
                prevention = medical_info['予防']
                prevention_list = [f"✅{prev}" for prev in prevention]
                prevention_text = "\n".join(prevention_list)
                content = f"獣医師からのお願い：愛猫の{topic}を防ぐために🙏\n\n予防と早期発見のポイント：\n\n{prevention_text}\n\n日々の観察が愛猫の健康寿命を延ばします。\n#猫のあれこれ"
            
            posts.append({
                "date": current_date.strftime('%Y-%m-%d'),
                "content": content,
                "char_count": len(content)
            })
        
        return posts

    def _generate_interactive_week(self, start_date):
        """参加型コンテンツ週の生成"""
        posts = []
        
        quiz_topics = [
            {
                "topic": "猫の能力",
                "question": "猫が1日に毛づくろいに費やす時間の割合は？",
                "choices": ["①約10%", "②約30%", "③約50%"],
                "correct": "②約30%",
                "explanation": "猫は起きている時間の30-50%を毛づくろいに費やします。これは体温調節、リラックス効果、社会的なコミュニケーションの意味があります。"
            }
        ]
        
        # クイズ形式で7日間構成
        for day in range(7):
            current_date = start_date + timedelta(days=day)
            
            if day == 0:  # クイズ出題
                quiz = quiz_topics[0]
                choices_text = "\n".join(quiz['choices'])
                content = f"獣医師が教える！{quiz['topic']}クイズ👁️\n\nQ. {quiz['question']}\n\n{choices_text}\n\n正解と解説は明日！猫の習性、ご存知ですか？\n#猫のあれこれ"
            
            elif day == 1:  # クイズ解答
                quiz = quiz_topics[0]
                content = f"獣医師が解説！昨日のクイズ答え合わせ💡\n\n正解は…{quiz['correct']}！\n\n解説：{quiz['explanation']}\n\n猫の行動には必ず理由があるんです。\n#猫のあれこれ"
            
            # 残りの日は動的に生成
            else:
                content = self._generate_daily_interactive_content(day, current_date)
            
            posts.append({
                "date": current_date.strftime('%Y-%m-%d'),
                "content": content,
                "char_count": len(content)
            })
        
        return posts

    # ヘルパーメソッド群
    def _get_breed_intro(self, breed_info):
        features = breed_info['特徴'][:3]
        feature_list = [f"✅{feature}" for feature in features]
        return "\n".join(feature_list)

    def _get_breed_history(self, breed_info):
        return f"原産国：{breed_info['原産国']}\n\n{breed_info['歴史']}"

    def _get_personality_description(self, breed_info):
        personality = breed_info['性格']
        personality_list = [f"✅{trait}" for trait in personality]
        personality_text = "\n".join(personality_list)
        return f"「{personality[0]}で{personality[1]}」な性格です。\n\n{personality_text}"

    def _get_physical_features(self, breed_info):
        features = breed_info['特徴']
        features_list = [f"✅{feature}" for feature in features]
        features_text = "\n".join(features_list)
        return f"際立った身体的特徴：\n\n{features_text}"

    def _get_health_info(self, breed_info):
        health_issues = breed_info['健康']
        health_list = [f"✅{issue}" for issue in health_issues]
        health_text = "\n".join(health_list)
        return f"注意すべき健康問題：\n\n{health_text}"

    def _get_care_instructions(self, breed_info):
        care_points = breed_info['ケア']
        care_list = [f"✅{care}" for care in care_points]
        care_text = "\n".join(care_list)
        return f"適切なケア方法：\n\n{care_text}"

    def _format_advanced_symptoms(self, medical_info):
        symptoms = medical_info['症状'][3:] if len(medical_info['症状']) > 3 else medical_info['症状']
        symptom_list = [f"✅{symptom}" for symptom in symptoms]
        return "\n".join(symptom_list)

    def _get_treatment_intro(self, topic):
        intros = {
            "慢性腎臓病": "根治は困難ですが、進行を穏やかにし、生活の質(QOL)を維持することが治療目標です。",
            "歯周病": "適切な治療により症状の改善と進行の阻止が可能です。",
        }
        return intros.get(topic, "早期治療により症状の改善が期待できます。")

    def _format_home_care_tips(self, medical_info):
        # 治療法をベースに家庭でのケアに変換
        care_tips = []
        for treatment in medical_info['治療']:
            if "食事" in treatment:
                care_tips.append("✅獣医師推奨の療法食を与える")
            elif "水分" in treatment or "輸液" in treatment:
                care_tips.append("✅十分な水分摂取を促す")
            elif "薬" in treatment:
                care_tips.append("✅処方薬を指示通り投与する")
        
        if care_tips:
            return "\n".join(care_tips)
        else:
            return "✅定期的な観察と記録\n✅環境の清潔維持\n✅ストレス軽減"

    def _get_home_care_intro(self, topic):
        intros = {
            "慢性腎臓病": "腎臓病の猫にとって家庭でのケアは非常に重要！",
            "歯周病": "お家でできる歯周病ケアで進行を防ぎましょう！",
        }
        return intros.get(topic, "家庭でできるケアで症状の改善を目指しましょう。")

    def _get_breed_unique_feature(self, breed_info):
        unique_features = {
            "ロシアンブルー": "ロシアンスマイル",
            "メインクーン": "立派な尻尾",
            "ペルシャ": "ふわふわの長毛"
        }
        # 品種名を特定してユニークな特徴を返す
        for breed, feature in unique_features.items():
            if any(breed in str(breed_info.values())):
                return feature
        return "美しい瞳"

    def _generate_daily_interactive_content(self, day, current_date):
        """日々の参加型コンテンツを動的生成"""
        interactive_patterns = [
            "獣医師に教えて！愛猫の夏の過ごし方☀️\n\n【質問】あなたの猫ちゃんは、夏はどこで涼むのが好きですか？\n\n①フローリングの上\n②玄関のたたき\n③エアコンの風が当たる場所\n④その他\n\nコメントで教えてくださいね！\n#猫のあれこれ",
            
            "獣医師の豆知識：猫の「フレーメン反応」って？😲\n\n猫が口を半開きにして変な顔をすることがありますよね。これはフェロモンを嗅ぎ取るための特別な行動「フレーメン反応」。怒ったりしているわけではないんですよ。\n#猫のあれこれ",
            
            "救急獣医師のつぶやき⑥🌿\n\n夏場、観葉植物を置くご家庭も多いですが、猫には毒になる植物も。特にユリ科は非常に危険です。花瓶の水を飲むだけでも重い腎障害を起こすことがあります。植物を置く前に安全か確認を。\n#猫のあれこれ"
        ]
        
        return interactive_patterns[min(day-2, len(interactive_patterns)-1)]

# テスト用関数
def test_ai_generator():
    generator = AIContentGenerator()
    
    # 猫種特集週をテスト
    start_date = datetime(2025, 7, 14)
    posts = generator.generate_week_content(start_date, "猫種特集", "ロシアンブルー")
    
    print("=== ロシアンブルー特集週 ===")
    for post in posts:
        print(f"\n{post['date']} ({post['char_count']}文字)")
        print(post['content'])
        print("-" * 50)

if __name__ == "__main__":
    test_ai_generator()