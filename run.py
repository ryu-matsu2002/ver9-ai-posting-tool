from app import create_app
from app.article_worker import run_article_worker  # ✅ 非同期ワーカーの読み込み
import os

app = create_app()

# ✅ Flask起動時に非同期記事生成ワーカーを起動
run_article_worker(app)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Render用ポート指定
    app.run(host='0.0.0.0', port=port, debug=True)
