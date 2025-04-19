from flask import Blueprint, render_template, request, jsonify, redirect, url_for
import os
import openai
import requests
import random
from openai import OpenAI
from .models import PromptTemplate, ScheduledPost  # ✅ 追加

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    genres = PromptTemplate.query.order_by(PromptTemplate.genre).all()

    if request.method == 'POST':
        raw_keywords = request.form['keywords']
        title_prompt = request.form['title_prompt']
        body_prompt = request.form['body_prompt']

        keywords = [k.strip() for k in raw_keywords.strip().splitlines() if k.strip()][:40]

        # ✅ 各キーワードをDBに「pending」で保存
        for keyword in keywords:
            num_articles = random.randint(2, 3)
            for _ in range(num_articles):
                new_post = ScheduledPost(
                    keyword=keyword,
                    title=None,
                    body=None,
                    image_url=None,
                    status='pending'
                )
                # プロンプトも記録（必要ならモデル拡張）
                # new_post.title_prompt = title_prompt
                # new_post.body_prompt = body_prompt
                from .models import db
                db.session.add(new_post)
        db.session.commit()

        # ✅ 投稿ログページへリダイレクト
        return redirect(url_for('log.show_log'))

    return render_template('index.html', genres=genres)


# ✅ JavaScriptから選ばれたジャンルのプロンプトを取得するAPI
@main_bp.route('/get_prompt/<genre>')
def get_prompt(genre):
    prompt = PromptTemplate.query.filter_by(genre=genre).first()
    if prompt:
        return jsonify({
            "title_prompt": prompt.title_prompt,
            "body_prompt": prompt.body_prompt
        })
    return jsonify({"error": "プロンプトが見つかりません"}), 404
