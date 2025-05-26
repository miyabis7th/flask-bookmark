#!/bin/bash

# Cloud SQL データベースとユーザー作成スクリプト

PROJECT_ID="bookmark-app-1748244130"
INSTANCE_NAME="bookmark-db"
DB_NAME="bookmarkdb"
DB_USER="dbuser"
DB_PASS="BookmarkApp123!"

echo "🗄️ Cloud SQL データベース設定開始"
echo "=================================="

# インスタンスの状態確認
echo "📊 Cloud SQLインスタンスの状態確認..."
STATUS=$(gcloud sql instances describe $INSTANCE_NAME --format="value(state)" 2>/dev/null || echo "NOT_FOUND")
echo "現在の状態: $STATUS"

if [ "$STATUS" != "RUNNABLE" ]; then
    echo "⏳ Cloud SQLインスタンスの作成完了を待っています..."
    echo "   作成には通常5-10分かかります。"
    echo "   状態を確認するには: gcloud sql instances list"
    exit 1
fi

echo "✅ Cloud SQLインスタンスが利用可能です！"

# データベース作成
echo "📝 データベース '$DB_NAME' を作成中..."
gcloud sql databases create $DB_NAME --instance=$INSTANCE_NAME 2>/dev/null || echo "データベースは既に存在します"

# ユーザー作成
echo "👤 ユーザー '$DB_USER' を作成中..."
gcloud sql users create $DB_USER --instance=$INSTANCE_NAME --password=$DB_PASS 2>/dev/null || echo "ユーザーは既に存在します"

echo ""
echo "🎉 Cloud SQL設定完了！"
echo "=================================="
echo "インスタンス: $INSTANCE_NAME"
echo "データベース: $DB_NAME"
echo "ユーザー: $DB_USER"
echo "パスワード: $DB_PASS"
echo ""
echo "🚀 次のステップ: mainブランチにプッシュしてデプロイを開始"