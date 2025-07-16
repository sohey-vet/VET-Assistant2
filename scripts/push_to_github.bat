@echo off
echo VET-Assistant2をGitHubにプッシュしています...

cd /d "C:\Users\souhe\アプリ開発\アプリ開発\VET-Assistant2"

echo === Git Status ===
git status

echo === Adding files ===
git add .

echo === Creating commit ===
git commit -m "feat: 完全な犬投稿生成機能を実装し140文字制限に対応

- 犬投稿生成メソッド(_generate_dog_posts)を実装
- 過去投稿データ分析に基づく高品質なコンテンツ
- 猫投稿(07:00)と犬投稿(18:00)の両方を生成
- 140文字制限チェック機能を追加
- 文字数カウント・自動調整機能
- AI生成エラーを修正しシンプル生成に変更
- ボタン名を「📝 投稿生成開始」に変更
- 不要なテストファイルを削除

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo === Pushing to GitHub ===
git push origin main

echo === 完了 ===
echo GitHubプッシュが完了しました！
pause