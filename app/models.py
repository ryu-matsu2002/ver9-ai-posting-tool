from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# SQLAlchemyインスタンスを作成
db = SQLAlchemy()

# ✅ プロンプトテンプレートのモデル
class PromptTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(100), nullable=False, unique=True)  # ジャンル名
    title_prompt = db.Column(db.Text, nullable=False)              # タイトル用プロンプト
    body_prompt = db.Column(db.Text, nullable=False)               # 本文用プロンプト

# ✅ 投稿ログのための記事保存モデル
class ScheduledPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(255), nullable=False)
    title = db.Column(db.Text, nullable=True)
    body = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(50), default='pending')  # pending / completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
