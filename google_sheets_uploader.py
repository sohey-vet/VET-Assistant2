#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Sheets アップロード機能
VET-Assistant2で生成されたCSVをGoogleスプレッドシートに自動アップロード
"""

import gspread
import pandas as pd
import os
from google.oauth2.service_account import Credentials
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, filedialog

class GoogleSheetsUploader:
    def __init__(self):
        self.credentials_path = None
        self.client = None
        self.spreadsheet_url = None
        
    def setup_credentials(self, credentials_path=None):
        """
        Google Sheets APIの認証設定
        """
        if credentials_path is None:
            credentials_path = filedialog.askopenfilename(
                title="Google Cloud認証JSONファイルを選択",
                filetypes=[("JSON files", "*.json")]
            )
        
        if not credentials_path or not os.path.exists(credentials_path):
            return False
            
        try:
            # Google Sheets APIのスコープ
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            
            # 認証情報の読み込み
            credentials = Credentials.from_service_account_file(
                credentials_path, scopes=scope
            )
            
            # gspreadクライアントの初期化
            self.client = gspread.authorize(credentials)
            self.credentials_path = credentials_path
            
            return True
            
        except Exception as e:
            messagebox.showerror("認証エラー", f"Google Sheets API認証に失敗しました:\n{str(e)}")
            return False
    
    def set_spreadsheet_url(self, url):
        """
        アップロード先のスプレッドシートURLを設定
        """
        self.spreadsheet_url = url
    
    def upload_csv_to_sheet(self, csv_file_path, sheet_name=None, clear_existing=True):
        """
        CSVファイルをGoogleスプレッドシートにアップロード
        
        Args:
            csv_file_path: アップロードするCSVファイルのパス
            sheet_name: シート名（Noneの場合は自動生成）
            clear_existing: 既存データをクリアするかどうか
        """
        if not self.client:
            messagebox.showerror("エラー", "Google Sheets APIの認証が完了していません")
            return False
            
        if not self.spreadsheet_url:
            messagebox.showerror("エラー", "アップロード先のスプレッドシートURLが設定されていません")
            return False
            
        try:
            # スプレッドシートを開く
            spreadsheet = self.client.open_by_url(self.spreadsheet_url)
            
            # CSVファイルを読み込み
            df = pd.read_csv(csv_file_path)
            
            # シート名を決定
            if sheet_name is None:
                now = datetime.now()
                sheet_name = f"投稿スケジュール_{now.strftime('%Y%m%d_%H%M')}"
            
            # シートが存在するかチェック
            try:
                worksheet = spreadsheet.worksheet(sheet_name)
                if clear_existing:
                    worksheet.clear()
            except gspread.WorksheetNotFound:
                # シートが存在しない場合は新規作成
                worksheet = spreadsheet.add_worksheet(
                    title=sheet_name, 
                    rows=len(df) + 10, 
                    cols=len(df.columns) + 2
                )
            
            # データをアップロード
            # ヘッダーをアップロード
            header_range = f"A1:{chr(ord('A') + len(df.columns) - 1)}1"
            worksheet.update(header_range, [df.columns.tolist()])
            
            # データをアップロード
            if len(df) > 0:
                data_range = f"A2:{chr(ord('A') + len(df.columns) - 1)}{len(df) + 1}"
                worksheet.update(data_range, df.values.tolist())
            
            # 成功メッセージ
            messagebox.showinfo(
                "アップロード完了", 
                f"Googleスプレッドシートへのアップロードが完了しました!\n"
                f"シート名: {sheet_name}\n"
                f"行数: {len(df)}件"
            )
            
            return True
            
        except Exception as e:
            messagebox.showerror("アップロードエラー", f"アップロードに失敗しました:\n{str(e)}")
            return False
    
    def create_formatted_schedule_sheet(self, csv_file_path):
        """
        フォーマット済みの投稿スケジュールシートを作成
        """
        if not self.client or not self.spreadsheet_url:
            return False
            
        try:
            spreadsheet = self.client.open_by_url(self.spreadsheet_url)
            df = pd.read_csv(csv_file_path)
            
            # 新しいシート名
            now = datetime.now()
            sheet_name = f"投稿スケジュール_{now.strftime('%Y年%m月%d日')}"
            
            # 既存シートの削除（同名があれば）
            try:
                old_sheet = spreadsheet.worksheet(sheet_name)
                spreadsheet.del_worksheet(old_sheet)
            except gspread.WorksheetNotFound:
                pass
            
            # 新しいシートを作成
            worksheet = spreadsheet.add_worksheet(
                title=sheet_name,
                rows=len(df) + 10,
                cols=6
            )
            
            # ヘッダーの設定
            headers = ["投稿日時", "投稿内容", "文字数", "投稿済み", "備考", "ハッシュタグ"]
            worksheet.update("A1:F1", [headers])
            
            # データの挿入
            for i, row in df.iterrows():
                worksheet.update(f"A{i+2}", row['投稿日時'])
                worksheet.update(f"B{i+2}", row['投稿内容'])
                worksheet.update(f"C{i+2}", row['文字数'])
                worksheet.update(f"D{i+2}", "未投稿")  # デフォルト値
                
                # ハッシュタグの抽出
                content = row['投稿内容']
                hashtags = []
                if '#猫のあれこれ' in content:
                    hashtags.append('#猫のあれこれ')
                if '#獣医が教える犬のはなし' in content:
                    hashtags.append('#獣医が教える犬のはなし')
                
                worksheet.update(f"F{i+2}", ', '.join(hashtags))
            
            # セルの書式設定
            # ヘッダー行を太字に
            worksheet.format("A1:F1", {
                "textFormat": {"bold": True},
                "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9}
            })
            
            # 投稿済み列にデータ検証を追加
            worksheet.batch_update([{
                'setDataValidation': {
                    'range': {
                        'sheetId': worksheet.id,
                        'startRowIndex': 1,
                        'endRowIndex': len(df) + 1,
                        'startColumnIndex': 3,
                        'endColumnIndex': 4
                    },
                    'rule': {
                        'condition': {
                            'type': 'ONE_OF_LIST',
                            'values': [
                                {'userEnteredValue': '未投稿'},
                                {'userEnteredValue': '投稿済み'},
                                {'userEnteredValue': '下書き'}
                            ]
                        },
                        'showCustomUi': True
                    }
                }
            }])
            
            messagebox.showinfo(
                "フォーマット済みシート作成完了",
                f"投稿管理用のシートを作成しました!\n"
                f"シート名: {sheet_name}\n"
                f"投稿予定: {len(df)}件"
            )
            
            return True
            
        except Exception as e:
            messagebox.showerror("シート作成エラー", f"フォーマット済みシートの作成に失敗しました:\n{str(e)}")
            return False

# 使用例とテスト用の関数
def test_upload():
    """
    テスト用のアップロード関数
    """
    uploader = GoogleSheetsUploader()
    
    # 認証設定
    if uploader.setup_credentials():
        print("認証成功")
        
        # スプレッドシートURL設定（テスト用）
        test_url = input("テスト用スプレッドシートのURLを入力してください: ")
        uploader.set_spreadsheet_url(test_url)
        
        # CSVファイル選択
        csv_file = filedialog.askopenfilename(
            title="アップロードするCSVファイルを選択",
            filetypes=[("CSV files", "*.csv")]
        )
        
        if csv_file:
            # フォーマット済みシートとして作成
            uploader.create_formatted_schedule_sheet(csv_file)
    else:
        print("認証失敗")

if __name__ == "__main__":
    # テスト実行
    root = tk.Tk()
    root.withdraw()  # メインウィンドウを非表示
    test_upload()