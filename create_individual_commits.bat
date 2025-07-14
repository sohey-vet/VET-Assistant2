@echo off
chcp 65001
echo 各ファイルに個別の日本語コミットメッセージを設定します...

cd /d "C:\Users\souhe\アプリ開発\アプリ開発\VET-Assistant2"

echo === 新しいブランチで個別コミット開始 ===
git checkout --orphan individual-commits

echo === 1. メインアプリケーション ===
git add enhanced_post_generator.py
git commit -m "feat: メインアプリケーション - 投稿生成GUIツール

enhanced_post_generator.py
📱 Tkinter GUIアプリケーション
🎯 猫・犬投稿の自動生成機能
📏 140文字制限対応
🔄 重複チェック機能
📊 Google Sheets連携"

echo === 2. AI生成エンジン ===
git add ai_content_generator.py
git commit -m "feat: AI生成エンジン - 高品質コンテンツ生成システム

ai_content_generator.py  
🤖 AI駆動コンテンツ生成
📚 獣医学知識データベース
🐱 猫種特集生成機能
💊 専門テーマ解説機能
❓ 参加型クイズ生成"

echo === 3. 重複監視システム ===
git add advanced_duplicate_monitor.py
git commit -m "feat: 重複監視システム - 投稿重複検出・防止機能

advanced_duplicate_monitor.py
🔍 高度な重複検出アルゴリズム
📊 類似度計算機能
📅 期間指定チェック
💾 SQLiteデータベース連携
📈 統計情報出力"

echo === 残りのファイル追加 ===
git add .
git commit -m "feat: プロジェクト完成 - 全機能統合"

echo === 古いブランチ削除・置き換え ===
git branch -D main
git branch -m main

echo === 強制プッシュ ===
git push --force origin main

echo === 完了 ===
echo 各ファイルに個別コミットが設定されました！
pause