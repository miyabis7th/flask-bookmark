import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# アプリケーションバージョン
APP_VERSION = "1.0.2"

# Cloud SQLとの接続設定
INSTANCE_CONNECTION_NAME = os.environ.get("INSTANCE_CONNECTION_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME")

# データベース設定
try:
    if INSTANCE_CONNECTION_NAME and DB_USER and DB_PASS and DB_NAME:
        # Cloud SQL使用
        from google.cloud.sql.connector import Connector, IPTypes
        
        connector = Connector()

        def getconn():
            conn = connector.connect(
                INSTANCE_CONNECTION_NAME,
                "pg8000",
                user=DB_USER,
                password=DB_PASS,
                db=DB_NAME,
                ip_type=IPTypes.PUBLIC
            )
            return conn

        app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+pg8000://"
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            "creator": getconn
        }
        print("Using Cloud SQL PostgreSQL database")
    else:
        raise Exception("Cloud SQL credentials not found")
        
except Exception as e:
    # ローカル開発用SQLite
    print(f"Cloud SQL connection failed ({e}), falling back to SQLite")
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Bookmarkモデルの定義
class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f'<Bookmark {self.title}>'

# データベースの初期化
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return redirect(url_for('bookmarks'))

@app.route('/bookmarks')
def bookmarks():
    bookmarks = Bookmark.query.order_by(Bookmark.created_at.desc()).all()
    return render_template('bookmarks.html', bookmarks=bookmarks, app_version=APP_VERSION)

@app.route('/add', methods=['GET', 'POST'])
def add_bookmark():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        url = request.form.get('url', '').strip()
        description = request.form.get('description', '').strip()

        if not title or not url:
            flash('Title and URL are required!', 'error')
            return render_template('add_bookmark.html', app_version=APP_VERSION)

        try:
            new_bookmark = Bookmark(title=title, url=url, description=description or None)
            db.session.add(new_bookmark)
            db.session.commit()
            flash('Bookmark added successfully!', 'success')
            return redirect(url_for('bookmarks'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding bookmark. Please try again.', 'error')
            return render_template('add_bookmark.html', app_version=APP_VERSION)
    
    return render_template('add_bookmark.html', app_version=APP_VERSION)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
