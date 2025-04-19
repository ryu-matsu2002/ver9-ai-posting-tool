from flask_sqlalchemy import SQLAlchemy

# SQLAlchemyインスタンスを作成
db = SQLAlchemy()

# プロンプトテンプレートのモデル
class PromptTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(100), nullable=False, unique=True)  # ジャンル名
    title_prompt = db.Column(db.Text, nullable=False)              # タイトル用プロンプト
    body_prompt = db.Column(db.Text, nullable=False)               # 本文用プロンプト
