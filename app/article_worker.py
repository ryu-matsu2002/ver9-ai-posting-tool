import os
import time
import threading
import requests
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor

from .models import db, ScheduledPost
from flask import current_app
from datetime import datetime

def generate_article(post_id, title_prompt, body_prompt, openai_api_key, pixabay_key):
    with current_app.app_context():
        post = ScheduledPost.query.get(post_id)
        if not post or post.status != 'pending':
            return

        client = OpenAI(api_key=openai_api_key)

        # タイトル生成
        title_response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": f"キーワード: {post.keyword}\n\n{title_prompt}"
            }],
            max_tokens=150,
            temperature=0.8
        )
        title_raw = title_response.choices[0].message.content.strip()
        title = title_raw.split("1.")[1].strip().split("\n")[0] if "1." in title_raw else title_raw.strip().split("\n")[0]

        # 本文生成
        content_response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": f"記事タイトル: {title}\n\n{body_prompt}"
            }],
            max_tokens=3200,
            temperature=0.8
        )
        body = content_response.choices[0].message.content.strip()

        # 画像検索
        image_url = None
        try:
            res = requests.get(
                f"https://pixabay.com/api/?key={pixabay_key}&q={post.keyword}&image_type=photo&per_page=3"
            )
            data = res.json()
            if data['hits']:
                image_url = data['hits'][0]['webformatURL']
        except:
            pass

        # DB更新
        post.title = title
        post.body = body
        post.image_url = image_url
        post.status = 'completed'
        db.session.commit()

def run_article_worker(app):
    def worker_loop():
        with app.app_context():
            print("🟢 記事生成ワーカー起動中...")
            while True:
                pending_posts = ScheduledPost.query.filter_by(status='pending').limit(3).all()
                if not pending_posts:
                    time.sleep(10)
                    continue

                print(f"🟡 処理対象: {len(pending_posts)} 件")

                # 並列処理で記事生成
                with ThreadPoolExecutor(max_workers=3) as executor:
                    for post in pending_posts:
                        executor.submit(
                            generate_article,
                            post.id,
                            "以下のキーワードを使って魅力的な記事タイトルを考えてください。",
                            "この記事タイトルに対して読者が納得できる解説記事を書いてください。",
                            os.getenv("OPENAI_API_KEY"),
                            os.getenv("PIXABAY_API_KEY")
                        )

                time.sleep(5)  # 次のチェックまで少し待つ

    thread = threading.Thread(target=worker_loop, daemon=True)
    thread.start()
