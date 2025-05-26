# Bookmark Management App

FlaskとSQLAlchemyを使用したシンプルなブックマーク管理アプリケーションです。Google Cloud RunとCloud SQLで動作します。

## 機能

- ブックマークの登録（タイトル、URL、説明）
- ブックマーク一覧表示
- Bootstrapを使用したレスポンシブUI

## 技術スタック

- **Backend**: Flask, SQLAlchemy, Flask-SQLAlchemy
- **Database**: Cloud SQL (PostgreSQL) / SQLite (開発環境)
- **Deployment**: Google Cloud Run
- **CI/CD**: GitHub Actions

## ローカル開発

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env` ファイルを作成し、以下の変数を設定してください：

```env
# Cloud SQL設定（本番環境用）
DB_USER=your_db_user
DB_PASS=your_db_password
DB_NAME=your_db_name
INSTANCE_CONNECTION_NAME=your_project:your_region:your_instance

# Flask設定
SECRET_KEY=your_secret_key

# ローカル開発用（Cloud SQL設定がない場合は自動的にSQLiteを使用）
# DATABASE_URL=sqlite:///app.db
```

### 3. アプリケーションの実行

```bash
flask run
```

アプリケーションは `http://127.0.0.1:5000` で利用できます。

## デプロイ

### 前提条件

1. **GCPプロジェクトの準備**
   - Google Cloud Projectを作成
   - 以下のAPIを有効化：
     - Cloud SQL Admin API
     - Cloud Build API
     - Cloud Run API
     - Container Registry API

2. **Cloud SQLインスタンスの作成**
   ```bash
   gcloud sql instances create bookmark-db \
     --database-version=POSTGRES_13 \
     --tier=db-f1-micro \
     --region=asia-northeast1
   
   gcloud sql databases create bookmarkdb --instance=bookmark-db
   
   gcloud sql users create dbuser \
     --instance=bookmark-db \
     --password=your_secure_password
   ```

3. **サービスアカウントの作成**
   ```bash
   gcloud iam service-accounts create github-actions \
     --display-name="GitHub Actions"
   
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/cloudsql.client"
   
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/cloudbuild.builds.editor"
   
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/run.admin"
   
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/storage.admin"
   
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/iam.serviceAccountUser"
   ```

4. **サービスアカウントキーの作成**
   ```bash
   gcloud iam service-accounts keys create key.json \
     --iam-account=github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com
   ```

### GitHub Secrets設定

GitHub リポジトリの Settings > Secrets and variables > Actions に以下を設定：

**必須のSecrets:**
- `GCP_SA_KEY`: 上記で作成したサービスアカウントキー（key.jsonの内容全体）
- `PROJECT_ID`: GCPプロジェクトID
- `SERVICE_NAME`: Cloud Runサービス名（例: `bookmark-app`）
- `REGION`: Cloud Runリージョン（例: `asia-northeast1`）
- `INSTANCE_CONNECTION_NAME`: Cloud SQL接続名（例: `your-project:asia-northeast1:bookmark-db`）
- `DB_USER`: データベースユーザー名（例: `dbuser`）
- `DB_PASS`: データベースパスワード
- `DB_NAME`: データベース名（例: `bookmarkdb`）
- `SECRET_KEY`: Flask用秘密鍵（ランダムな文字列、例: `your-super-secret-key-here`）

**設定例:**
```
GCP_SA_KEY: {
  "type": "service_account",
  "project_id": "your-project-id",
  ...
}
PROJECT_ID: your-project-id
SERVICE_NAME: bookmark-app
REGION: asia-northeast1
INSTANCE_CONNECTION_NAME: your-project-id:asia-northeast1:bookmark-db
DB_USER: dbuser
DB_PASS: your_secure_password
DB_NAME: bookmarkdb
SECRET_KEY: your-super-secret-key-here
```

### 自動デプロイ

1. **リポジトリの準備**
   ```bash
   git add .
   git commit -m "Setup Cloud Run deployment"
   git push origin main
   ```

2. **デプロイの確認**
   - GitHub > Actions タブでワークフローの実行状況を確認
   - 成功すると、コンソールにサービスURLが表示されます
   - Cloud Run Console でサービスの状態を確認

3. **手動デプロイ（必要に応じて）**
   ```bash
   # ローカルからの手動デプロイ
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/bookmark-app
   gcloud run deploy bookmark-app \
     --image gcr.io/YOUR_PROJECT_ID/bookmark-app \
     --platform managed \
     --region asia-northeast1 \
     --allow-unauthenticated
   ```

### トラブルシューティング

1. **Cloud SQL接続エラー**
   - INSTANCE_CONNECTION_NAME の形式を確認（project:region:instance）
   - サービスアカウントにCloud SQL Clientロールが付与されているか確認

2. **Permission denied エラー**
   - サービスアカウントの権限を確認
   - GitHub Secretsの値が正しく設定されているか確認

3. **Build エラー**
   - requirements.txtの依存関係を確認
   - Dockerfileの構文を確認

### 必要なGCP権限

サービスアカウントに以下のロールが必要です：

- `roles/cloudsql.client` - Cloud SQL Client
- `roles/cloudbuild.builds.editor` - Cloud Build Editor
- `roles/run.admin` - Cloud Run Admin
- `roles/storage.admin` - Storage Admin (Container Registry用)
- `roles/iam.serviceAccountUser` - Service Account User

## API有効化

以下のAPIを有効化してください：

- Cloud SQL Admin API
- Cloud Build API
- Cloud Run API

## プルリクのテスト