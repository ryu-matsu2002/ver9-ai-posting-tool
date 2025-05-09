from flask import Flask
from dotenv import load_dotenv
import os

from .models import db
from flask_migrate import Migrate

from .routes import main_bp
from .prompt_templates import prompt_bp  # ✅ 追加：ジャンル別プロンプト機能用
from .admin_log import log_bp

def create_app():
    # .envファイルの読み込み
    load_dotenv()

    # Flaskアプリケーションの作成
    app = Flask(__name__)

    # .envからSECRET_KEYの取得（デフォルトは"dev_key"）
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "dev_key")

    # .envからDATABASE_URLを取得し、データベース接続設定
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///data.db")

    # SQLAlchemyのトラッキング機能無効化
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # DB初期化・マイグレーション設定
    db.init_app(app)
    Migrate(app, db)

    # Blueprint登録
    app.register_blueprint(main_bp)
    app.register_blueprint(prompt_bp)  # ✅ プロンプト機能をルーティングに追加
    app.register_blueprint(log_bp)

    return app
