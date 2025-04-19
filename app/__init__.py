from flask import Flask
from dotenv import load_dotenv
import os

# .env読み込み
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "dev_key")  # 安全のため .env で管理推奨

    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app
