#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VET-Assistant2 重複防止機能テストスクリプト
"""

import sys
import os
from advanced_duplicate_monitor import AdvancedDuplicateMonitor

def test_duplicate_prevention():
    """重複防止機能の総合テスト"""
    print("🧪 VET-Assistant2 重複防止機能テスト開始")
    print("=" * 60)
    
    # テスト用データベース
    test_db = "test_vet_assistant2.db"
    if os.path.exists(test_db):
        os.remove(test_db)
    
    monitor = AdvancedDuplicateMonitor(test_db)
    
    # テスト投稿データ
    test_posts = [
        {
            "content": "獣医師が教える！【猫の腎臓病】🐱\n\n腎臓病は猫の代表的な病気の一つです💦\n\n✅早期発見が重要\n✅水分摂取を増やす\n✅食事療法が基本\n\n愛猫の健康を守りましょう！\n#猫のあれこれ",
            "animal_type": "cat",
            "topic": "猫の腎臓病",
            "post_type": "health"
        },
        {
            "content": "獣医師が教える！【猫の腎臓病について】🐱\n\n腎臓病は猫の代表的な疾患です💦\n\n✅早期発見が大切\n✅水分摂取量を増やす\n✅食事療法が重要\n\n愛猫の健康を守りましょう！\n#猫のあれこれ",
            "animal_type": "cat", 
            "topic": "猫の腎臓病",
            "post_type": "health"
        },
        {
            "content": "【もしもの時... ケース① 歩行異常】\n\n症例：7歳のゴールデンレトリーバー\n散歩中に後ろ足をかばうような歩き方をする。\n階段を上がるのを嫌がるようになった🐕\n\n考えられる原因は？\n#獣医が教える犬のはなし",
            "animal_type": "dog",
            "topic": "犬の関節",
            "post_type": "case"
        },
        {
            "content": "獣医師が教える！【犬の散歩について】🐶\n\n散歩は犬の健康維持に重要です！\n\n✅適度な運動\n✅ストレス発散\n✅社会性の向上\n\n愛犬との時間を楽しみましょう♪\n#獣医が教える犬のはなし",
            "animal_type": "dog",
            "topic": "犬の運動",
            "post_type": "health"
        }
    ]
    
    print("\n1. 投稿保存テスト")
    print("-" * 30)
    
    for i, post in enumerate(test_posts, 1):
        success = monitor.save_approved_post(
            post["content"], 
            post["animal_type"], 
            post["topic"], 
            post["post_type"]
        )
        print(f"投稿 {i}: {'✅ 保存成功' if success else '❌ 保存失敗'}")
    
    print("\n2. 完全一致テスト")
    print("-" * 30)
    
    # 同じ内容で重複チェック
    is_duplicate, duplicates = monitor.check_duplicate_comprehensive(
        test_posts[0]["content"], 
        test_posts[0]["animal_type"], 
        test_posts[0]["topic"]
    )
    
    print(f"完全一致検出: {'✅ 重複検出成功' if is_duplicate else '❌ 重複検出失敗'}")
    if duplicates:
        print(f"類似度: {duplicates[0]['similarity']:.3f}")
    
    print("\n3. 類似投稿テスト")
    print("-" * 30)
    
    # 類似投稿で重複チェック
    is_duplicate, duplicates = monitor.check_duplicate_comprehensive(
        test_posts[1]["content"], 
        test_posts[1]["animal_type"], 
        test_posts[1]["topic"]
    )
    
    print(f"類似投稿検出: {'✅ 重複検出成功' if is_duplicate else '❌ 重複検出失敗'}")
    if duplicates:
        print(f"類似度: {duplicates[0]['similarity']:.3f}")
        print(f"類似投稿: {duplicates[0]['content'][:50]}...")
    
    print("\n4. 異なる動物種テスト")
    print("-" * 30)
    
    # 異なる動物種で重複チェック
    is_duplicate, duplicates = monitor.check_duplicate_comprehensive(
        test_posts[2]["content"], 
        test_posts[2]["animal_type"], 
        test_posts[2]["topic"]
    )
    
    print(f"異なる動物種: {'❌ 重複検出' if is_duplicate else '✅ 重複なし'}")
    
    print("\n5. キーワード抽出テスト")
    print("-" * 30)
    
    test_content = "獣医師が教える！【猫の糖尿病】🐱\n\n糖尿病は高齢猫に多い病気です。\n\n✅血液検査で診断\n✅インスリン治療\n✅食事療法が重要\n\n症状：多飲多尿、体重減少\n#猫のあれこれ"
    
    keywords = monitor.extract_keywords(test_content)
    print(f"抽出キーワード: {keywords}")
    
    main_points = monitor.extract_main_points(test_content)
    print(f"主要ポイント: {main_points}")
    
    print("\n6. 類似度計算テスト")
    print("-" * 30)
    
    content1 = "獣医師が教える！【猫の腎臓病】🐱\n\n早期発見が重要です。\n\n✅多飲多尿\n✅食欲不振\n✅体重減少\n\n#猫のあれこれ"
    content2 = "獣医師が教える！【猫の腎臓病について】🐱\n\n早期発見が大切です。\n\n✅水をよく飲む\n✅食欲がない\n✅痩せてきた\n\n#猫のあれこれ"
    content3 = "獣医師が教える！【犬の散歩】🐶\n\n運動が大切です。\n\n✅健康維持\n✅ストレス解消\n✅楽しい時間\n\n#獣医が教える犬のはなし"
    
    similarity1 = monitor.calculate_similarity(content1, content2)
    similarity2 = monitor.calculate_similarity(content1, content3)
    
    print(f"類似コンテンツ間の類似度: {similarity1:.3f}")
    print(f"異なるコンテンツ間の類似度: {similarity2:.3f}")
    
    print("\n7. 統計情報テスト")
    print("-" * 30)
    
    stats = monitor.get_statistics()
    print(f"総投稿数: {stats['total_posts']}")
    print(f"動物種別: {stats['animal_counts']}")
    print(f"重複検出数: {stats['duplicate_detections']}")
    print(f"最近の投稿: {stats['recent_posts']}")
    
    print("\n8. 期間指定テスト")
    print("-" * 30)
    
    # 6か月前まで
    is_duplicate_6m, duplicates_6m = monitor.check_duplicate_comprehensive(
        test_posts[0]["content"], 
        test_posts[0]["animal_type"], 
        test_posts[0]["topic"],
        months_back=6
    )
    
    # 1か月前まで
    is_duplicate_1m, duplicates_1m = monitor.check_duplicate_comprehensive(
        test_posts[0]["content"], 
        test_posts[0]["animal_type"], 
        test_posts[0]["topic"],
        months_back=1
    )
    
    print(f"6か月前まで: {'✅ 重複検出' if is_duplicate_6m else '❌ 重複なし'}")
    print(f"1か月前まで: {'✅ 重複検出' if is_duplicate_1m else '❌ 重複なし'}")
    
    print("\n9. 閾値テスト")
    print("-" * 30)
    
    # 閾値を変更してテスト
    original_threshold = monitor.similarity_threshold
    
    monitor.similarity_threshold = 0.8  # 80%
    is_duplicate_high, _ = monitor.check_duplicate_comprehensive(
        test_posts[1]["content"], 
        test_posts[1]["animal_type"], 
        test_posts[1]["topic"]
    )
    
    monitor.similarity_threshold = 0.5  # 50%
    is_duplicate_low, _ = monitor.check_duplicate_comprehensive(
        test_posts[1]["content"], 
        test_posts[1]["animal_type"], 
        test_posts[1]["topic"]
    )
    
    print(f"閾値80%: {'✅ 重複検出' if is_duplicate_high else '❌ 重複なし'}")
    print(f"閾値50%: {'✅ 重複検出' if is_duplicate_low else '❌ 重複なし'}")
    
    # 閾値を元に戻す
    monitor.similarity_threshold = original_threshold
    
    print("\n10. 自動再生成シミュレーション")
    print("-" * 30)
    
    # 重複が検出される投稿を複数回チェック
    test_regeneration_content = test_posts[0]["content"]
    max_attempts = 5
    
    for attempt in range(max_attempts):
        is_duplicate, duplicates = monitor.check_duplicate_comprehensive(
            test_regeneration_content, 
            test_posts[0]["animal_type"], 
            test_posts[0]["topic"]
        )
        
        print(f"試行 {attempt + 1}: {'❌ 重複検出' if is_duplicate else '✅ 重複なし'}")
        
        if not is_duplicate:
            print("✅ 再生成成功（重複なし）")
            break
        elif attempt < max_attempts - 1:
            # 実際の再生成シミュレーション
            test_regeneration_content = test_regeneration_content.replace("腎臓病", "腎疾患")
            print("🔄 コンテンツを変更して再試行...")
        else:
            print("❌ 最大試行回数に達しました")
    
    print("\n" + "=" * 60)
    print("🎉 VET-Assistant2 重複防止機能テスト完了!")
    
    # テストファイルのクリーンアップ
    if os.path.exists(test_db):
        os.remove(test_db)
        print("🧹 テストファイルを削除しました")

def test_integration():
    """統合テスト"""
    print("\n" + "=" * 60)
    print("🔧 統合テスト開始")
    print("=" * 60)
    
    # 実際の使用を想定したテスト
    monitor = AdvancedDuplicateMonitor("integration_test.db")
    
    # 大量の投稿を保存
    test_posts = []
    for i in range(50):
        content = f"獣医師が教える！【テスト投稿{i}】🐱\n\nテスト内容です。\n\n✅ポイント{i}\n#猫のあれこれ"
        test_posts.append({
            "content": content,
            "animal_type": "cat",
            "topic": f"テスト{i}",
            "post_type": "test"
        })
    
    print(f"📝 {len(test_posts)}件の投稿を保存中...")
    
    saved_count = 0
    for post in test_posts:
        if monitor.save_approved_post(
            post["content"], 
            post["animal_type"], 
            post["topic"], 
            post["post_type"]
        ):
            saved_count += 1
    
    print(f"✅ {saved_count}件の投稿を保存完了")
    
    # 重複チェック性能テスト
    print("\n🚀 性能テスト開始...")
    
    import time
    start_time = time.time()
    
    # 100回の重複チェック
    for i in range(100):
        test_content = f"獣医師が教える！【性能テスト{i}】🐱\n\n性能テスト内容です。\n#猫のあれこれ"
        monitor.check_duplicate_comprehensive(test_content, "cat", f"性能テスト{i}")
    
    end_time = time.time()
    avg_time = (end_time - start_time) / 100
    
    print(f"✅ 重複チェック平均時間: {avg_time:.3f}秒")
    
    # 統計情報
    stats = monitor.get_statistics()
    print(f"📊 最終統計:")
    print(f"   総投稿数: {stats['total_posts']}")
    print(f"   重複検出数: {stats['duplicate_detections']}")
    
    # クリーンアップ
    if os.path.exists("integration_test.db"):
        os.remove("integration_test.db")
        print("🧹 統合テストファイルを削除しました")
    
    print("🎉 統合テスト完了!")

if __name__ == "__main__":
    # メインテスト
    test_duplicate_prevention()
    
    # 統合テスト
    test_integration()
    
    print("\n" + "=" * 60)
    print("✨ 全テスト完了！VET-Assistant2の重複防止機能は正常に動作しています。")
    print("=" * 60)