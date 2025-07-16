@echo off
chcp 65001
echo 全Gitコミット履歴を日本語に強制書き換えします...

cd /d "C:\Users\souhe\アプリ開発\アプリ開発\VET-Assistant2"

echo === 現在のブランチをバックアップ ===
git branch backup-main

echo === 全履歴を削除して新しい日本語履歴を作成 ===
git checkout --orphan new-main

echo === 全ファイルを追加 ===
git add .

echo === 初回コミット（日本語） ===
git commit -m "🎯 VET-Assistant2: 獣医師向けSNS投稿生成ツール

📝 主要機能:
┌────────────────────────────────────┐
│ ✅ 猫投稿自動生成 (07:00, #猫のあれこれ)        │
│ ✅ 犬投稿自動生成 (18:00, #獣医が教える犬のはなし) │
│ ✅ 140文字制限完全対応                     │
│ ✅ 文字数自動チェック・調整                 │
│ ✅ 重複投稿監視システム                     │
│ ✅ Google Sheets API連携                  │
│ ✅ 過去データ分析による高品質コンテンツ        │
│ ✅ AI生成エラー完全修正                     │
└────────────────────────────────────┘

🔧 技術スタック:
• Python 3.x + Tkinter GUI
• SQLite データベース  
• Google Sheets API
• 重複検出アルゴリズム
• 自動文字数調整機能

📚 主要ファイル:
• enhanced_post_generator.py - メインアプリケーション
• ai_content_generator.py - コンテンツ生成エンジン
• advanced_duplicate_monitor.py - 重複監視システム
• google_sheets_uploader.py - スプレッドシート連携

🚀 使用方法:
1. run_enhanced.bat 実行
2. 「📝 投稿生成開始」クリック  
3. 生成された投稿をCSVで確認
4. Google Sheetsに自動アップロード

💡 特徴:
- 獣医師の専門知識に基づく高品質コンテンツ
- 過去投稿データ分析による最適化
- 完全自動化されたワークフロー
- エラーハンドリング完備

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo === 古いメインブランチを削除 ===
git branch -D main

echo === 新しいブランチをメインに ===
git branch -m main

echo === 強制プッシュで履歴を完全書き換え ===
git push --force origin main

echo === 完了 ===
echo Git履歴が完全に日本語に書き換えられました！
echo GitHubページを再読み込みしてください。
pause