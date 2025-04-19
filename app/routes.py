from flask import Blueprint, render_template, request
import os
import openai
import requests
import random
from openai import OpenAI

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    results = []

    if request.method == 'POST':
        # フォームから取得
        raw_keywords = request.form['keywords']
        title_prompt = request.form['title_prompt']
        body_prompt = request.form['body_prompt']

        # 改行で分割、空白除去して最大40件まで取得
        keywords = [k.strip() for k in raw_keywords.strip().splitlines() if k.strip()][:40]

        # OpenAIクライアント初期化
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        pixabay_key = os.getenv("PIXABAY_API_KEY")

        for keyword in keywords:
            num_articles = random.randint(2, 3)  # 各キーワードで2～3記事生成

            for _ in range(num_articles):
                # タイトル生成
                title_response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{
                        "role": "user",
                        "content": f"キーワード: {keyword}\n\n{title_prompt}"
                    }],
                    max_tokens=150,
                    temperature=0.8
                )
                title_raw = title_response.choices[0].message.content.strip()

                # タイトル抽出（最初の1本だけ）
                if "1." in title_raw:
                    title = title_raw.split("1.")[1].strip().split("\n")[0]
                else:
                    title = title_raw.strip().split("\n")[0]

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
                content = content_response.choices[0].message.content.strip()

                # Pixabay画像取得
                image_url = None
                try:
                    res = requests.get(
                        f"https://pixabay.com/api/?key={pixabay_key}&q={keyword}&image_type=photo&per_page=3"
                    )
                    data = res.json()
                    if data['hits']:
                        image_url = data['hits'][0]['webformatURL']
                except:
                    pass  # Pixabayエラー時は画像なし

                # 結果リストに追加
                results.append({
                    "title": title,
                    "content": content,
                    "image_url": image_url
                })

    return render_template('index.html', results=results)
