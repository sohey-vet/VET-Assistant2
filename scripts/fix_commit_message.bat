@echo off
chcp 65001
echo 正しい日本語コミットメッセージでプッシュし直します...

cd /d "C:\Users\souhe\アプリ開発\アプリ開発\VET-Assistant2"

echo === Creating proper Japanese commit ===
git add .
git commit -m "feat: 犬投稿生成機能の完全実装と140文字制限対応

主な変更点:
- 犬投稿生成メソッド実装 (18:00, #獣医が教える犬のはなし)
- 猫投稿も同時生成 (07:00, #猫のあれこれ)  
- 140文字制限チェック機能追加
- 過去投稿データ分析に基づく高品質コンテンツ
- AI生成エラー修正とシンプル生成への変更
- 文字数自動調整機能実装
- UIボタン名変更とエラーハンドリング強化
- 不要なテストファイル削除

これで猫と犬の両方の投稿が適切な文字数で生成されます。

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo === Pushing to GitHub ===
git push origin main

echo === 完了 ===
echo 日本語コミットメッセージでのプッシュが完了しました！
pause