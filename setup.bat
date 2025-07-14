@echo off
echo VET-Assistant2 AI強化版セットアップ開始...
echo.

echo Python の確認中...
python --version
if errorlevel 1 (
    echo エラー: Python がインストールされていません。
    echo Python 3.7以上をインストールしてください。
    pause
    exit /b 1
)

echo.
echo 必要なライブラリをインストール中...
echo - 基本ライブラリ
pip install pandas python-dateutil

echo - Google Sheets連携ライブラリ
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib gspread

echo - 既存のrequirements.txtからもインストール
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo 警告: 一部のライブラリのインストールに失敗した可能性があります。
    echo インターネット接続とPythonの設定を確認してください。
)

echo.
echo =====================================
echo 🤖 VET-Assistant2 AI強化版 セットアップ完了！
echo =====================================
echo.
echo 新機能:
echo ✅ AI駆動の高品質投稿生成
echo ✅ Googleスプレッドシート自動連携
echo ✅ 週テーマ別コンテンツ生成
echo ✅ 改善された重複監視システム
echo.
echo run_enhanced.bat をダブルクリックしてアプリを起動してください。
echo.
pause