import os
import sys
import time
import threading
import requests
from openai import OpenAI
from .models import db, ScheduledPost
from flask import current_app

def generate_article(post_id, title_prompt, body_prompt, openai_api_key, pixabay_key):
    with current_app.app_context():
        try:
            print(f"\n📥 generate_article 呼び出し：post_id={post_id}")
            sys.stdout.flush()

            post = ScheduledPost.query.get(post_id)
            if not post or post.status != 'pending':
                print(f"⏩ スキップ：post_id={post_id} は処理不要")
                sys.stdout.flush()
                return

            print(f"📝 記事生成開始: ID={post_id}, キーワード={post.keyword}")
            sys.stdout.flush()

            client = OpenAI(api_key=openai_api_key)

            # 🔹 タイトル生成
            print("🔹 タイトル生成開始")
            sys.stdout.flush()
            title_response = client.chat.completions.create(
                model="gpt-4-turbo",  # gpt-4-turboを使用
                messages=[{
                    "role": "user",
                    "content": f"キーワード: {post.keyword}\n\n{title_prompt}"
                }],
                max_tokens=200,  # トークン数を増加
                temperature=0.9  # 多様性を増すために温度を上げる
            )
            print("🔸 タイトル生成完了")
            sys.stdout.flush()
            title_raw = title_response.choices[0].message.content.strip()
            title = title_raw.split("1.")[1].strip().split("\n")[0] if "1." in title_raw else title_raw.strip().split("\n")[0]

            # 🔹 本文生成
            print("🔹 本文生成開始")
            sys.stdout.flush()
            content_response = client.chat.completions.create(
                model="gpt-4-turbo",  # gpt-4-turboを使用
                messages=[{
                    "role": "user",
                    "content": f"記事タイトル: {title}\n\n{body_prompt}"
                }],
                max_tokens=4000,  # 長文を生成するためにトークン数を増加
                temperature=0.9  # 多様性を増すために温度を上げる
            )
            print("🔸 本文生成完了")
            sys.stdout.flush()
            body = content_response.choices[0].message.content.strip()

            # 🔹 画像検索
            print("🔹 画像取得開始")
            sys.stdout.flush()
            image_url = None
            try:
                res = requests.get(
                    f"https://pixabay.com/api/?key={pixabay_key}&q={post.keyword}関連画像&image_type=photo&per_page=3"
                )
                data = res.json()
                if data['hits']:
                    image_url = data['hits'][0]['webformatURL']
                print("🔸 画像取得完了")
                sys.stdout.flush()
            except Exception as img_err:
                print(f"[Pixabay画像取得エラー] {img_err}")
                sys.stdout.flush()

            # 🔹 DB更新
            post.title = title
            post.body = body
            post.image_url = image_url
            post.status = 'completed'
            db.session.commit()

            print(f"✅ 記事生成完了: ID={post_id} | タイトル: {title}")
            sys.stdout.flush()

        except Exception as e:
            print(f"❌ 生成失敗（post_id={post_id}）: {e}")
            sys.stdout.flush()
            # エラー時にDBのステータスを変更して再試行可能にする
            post.status = 'failed'
            db.session.commit()

def run_article_worker(app):
    def worker_loop():
        with app.app_context():
            print("🟢 記事生成ワーカーモード：シーケンシャル処理")
            while True:
                # 一度に処理する件数を1件に変更
                pending_posts = ScheduledPost.query.filter_by(status='pending').limit(1).all()
                if not pending_posts:
                    time.sleep(10)
                    continue

                print(f"🟡 処理対象: {len(pending_posts)} 件（シーケンシャル処理）")
                sys.stdout.flush()

                for post in pending_posts:
                    # 各記事を順番に処理
                    generate_article(
                        post.id,
                        post.title_prompt,  # ユーザーから渡されたタイトルプロンプトを使用
                        post.body_prompt,   # ユーザーから渡された本文プロンプトを使用
                        os.getenv("OPENAI_API_KEY"),
                        os.getenv("PIXABAY_API_KEY")
                    )

                time.sleep(5)  # 次のチェックまで少し待つ

    thread = threading.Thread(target=worker_loop, daemon=True)
    thread.start()
