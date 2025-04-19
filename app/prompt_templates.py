from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import db, PromptTemplate

prompt_bp = Blueprint('prompt', __name__)

@prompt_bp.route('/prompts', methods=['GET', 'POST'])
def manage_prompts():
    if request.method == 'POST':
        genre = request.form['genre'].strip()
        title_prompt = request.form['title_prompt'].strip()
        body_prompt = request.form['body_prompt'].strip()

        # ジャンル名が重複していないかチェック
        if PromptTemplate.query.filter_by(genre=genre).first():
            flash("このジャンルはすでに登録されています。", "warning")
        else:
            new_prompt = PromptTemplate(
                genre=genre,
                title_prompt=title_prompt,
                body_prompt=body_prompt
            )
            db.session.add(new_prompt)
            db.session.commit()
            flash("プロンプトを登録しました。", "success")
        return redirect(url_for('prompt.manage_prompts'))

    prompts = PromptTemplate.query.order_by(PromptTemplate.genre).all()
    return render_template('prompt_templates.html', prompts=prompts)

@prompt_bp.route('/prompts/delete/<int:prompt_id>', methods=['POST'])
def delete_prompt(prompt_id):
    prompt = PromptTemplate.query.get(prompt_id)
    if prompt:
        db.session.delete(prompt)
        db.session.commit()
        flash("プロンプトを削除しました。", "info")
    else:
        flash("プロンプトが見つかりませんでした。", "danger")
    return redirect(url_for('prompt.manage_prompts'))
