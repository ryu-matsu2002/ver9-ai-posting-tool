from flask import Blueprint, render_template, request
import os
import openai
import requests

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    title = None
    content = None
    image_url = None

    if request.method == 'POST':
        keyword = request.form['keyword']
        prompt = request.form['prompt']

        # ChatGPTでタイトル生成
        openai.api_key = os.getenv("OPENAI_API_KEY")
        title_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": f"キーワード: {keyword}\n\n{prompt} に基づいて、魅力的な記事タイトルを1つだけ生成してください。"}],
            max_tokens=150,
            temperature=0.8
        )
        title = title_response.choices[0].message['content'].strip()

        # ChatGPTで本文生成
        content_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": f"記事タイトル: {title}\n\n{prompt} に基づいて、SEOに強い本文（2500文字以上、h2見出し付き）を生成してください。"}],
            max_tokens=3200,
            temperature=0.8
        )
        content = content_response.choices[0].message['content'].strip()

        # Pixabayで画像検索（英語キーワードに変換して使用してもOK）
        pixabay_key = os.getenv("PIXABAY_API_KEY")
        res = requests.get(f"https://pixabay.com/api/?key={pixabay_key}&q={keyword}&image_type=photo&per_page=3")
        data = res.json()
        if data['hits']:
            image_url = data['hits'][0]['webformatURL']

    return render_template('index.html', title=title, content=content, image_url=image_url)
