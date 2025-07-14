#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
140文字制限テスト
"""

# 猫投稿のテスト
cat_posts = [
    "獣医師クイズ！猫の毛づくろい時間は？👁️\n\n①約10%\n②約30%\n③約50%\n\n正解は明日！\n#猫のあれこれ",
    "昨日の答え：②約30%！\n\n猫は起きている時間の30-50%を毛づくろいに費やします。体温調節とリラックス効果があります✨\n#猫のあれこれ",
    "愛猫の夏の涼み方は？☀️\n\n①フローリング\n②玄関\n③エアコンの風\n④その他\n\nコメントで教えて♪\n#猫のあれこれ",
    "猫の涼み方考察💡\n\n体温調節のため涼しい場所を本能的に選びます。フローリングや玄関は理想的ですね♪\n#猫のあれこれ",
    "猫のフレーメン反応😲\n\n口を半開きにする変な顔、見たことありますか？これはフェロモンを嗅ぎ取る行動。怒ってません♪\n#猫のあれこれ",
    "夏の観葉植物注意🌿\n\nユリ科は猫に危険！花瓶の水でも腎障害の恐れが。植物選びは慎重に。\n#猫のあれこれ",
    "週末健康チェック📝\n\n✅食欲\n✅元気\n✅トイレ\n✅毛づや\n\n日々の観察が早期発見の鍵です♪\n#猫のあれこれ"
]

# 犬投稿のテスト
dog_posts = [
    "【ケース：食欲の変化】10歳ゴールデン。\nご飯を残し、水をよく飲む💦\n\n最初に疑うべきは？\n(※架空事例)\n#獣医が教える犬のはなし",
    "【解説】昨日のケース💦\n\n多飲+食欲不振→腎臓病・糖尿病を疑います。\n高齢期は要注意。早めの検査を！🏥\n#獣医が教える犬のはなし",
    "【夏散歩クイズ☀️】\n\n危険な時間帯は？\n①早朝5-6時\n②午前10-11時\n③夕方17-18時\n\n答えは明日🐾\n#獣医が教える犬のはなし",
    "【答え】②午前10-11時！\n\nアスファルトが熱い時間。手で確認を。\n理想は早朝・夜間🌙\n#獣医が教える犬のはなし",
    "【夏バテ対策🌡️】\n\n✅クールマット\n✅氷入り水\n✅エアコン調整\n✅散歩時間変更\n\n皆さんの工夫は？\n#獣医が教える犬のはなし",
    "【パピヨン紹介🦋】\n\n✅明るく活発\n✅知的で学習能力高\n✅人懐っこい\n\n注意：膝蓋骨脱臼、眼疾患\n運動量多め🐕\n#獣医が教える犬のはなし",
    "【週末健康チェック📋】\n\n✅食欲・元気\n✅歩き方\n✅呼吸\n✅排泄\n\n小さな変化が早期発見の鍵🏥\n#獣医が教える犬のはなし"
]

print("=== 140文字制限チェック ===")
print()

print("🐱 猫投稿の文字数チェック:")
for i, post in enumerate(cat_posts):
    char_count = len(post)
    status = "✅" if char_count <= 140 else "❌"
    print(f"{i+1}日目: {char_count}文字 {status}")
    if char_count > 140:
        print(f"   超過: {char_count - 140}文字")

print()
print("🐕 犬投稿の文字数チェック:")
for i, post in enumerate(dog_posts):
    char_count = len(post)
    status = "✅" if char_count <= 140 else "❌"
    print(f"{i+1}日目: {char_count}文字 {status}")
    if char_count > 140:
        print(f"   超過: {char_count - 140}文字")

# 統計情報
cat_avg = sum(len(post) for post in cat_posts) / len(cat_posts)
dog_avg = sum(len(post) for post in dog_posts) / len(dog_posts)
cat_max = max(len(post) for post in cat_posts)
dog_max = max(len(post) for post in dog_posts)

print()
print("📊 統計情報:")
print(f"🐱 猫投稿 - 平均: {cat_avg:.1f}文字, 最大: {cat_max}文字")
print(f"🐕 犬投稿 - 平均: {dog_avg:.1f}文字, 最大: {dog_max}文字")

# 140文字制限遵守状況
cat_compliant = all(len(post) <= 140 for post in cat_posts)
dog_compliant = all(len(post) <= 140 for post in dog_posts)

print()
print("✅ 140文字制限遵守状況:")
print(f"🐱 猫投稿: {'全て遵守' if cat_compliant else '制限超過あり'}")
print(f"🐕 犬投稿: {'全て遵守' if dog_compliant else '制限超過あり'}")

if cat_compliant and dog_compliant:
    print("\n🎉 全ての投稿が140文字制限を遵守しています！")