from flask import Blueprint, render_template, request, redirect, url_for
from .models import ScheduledPost
from sqlalchemy import desc

log_bp = Blueprint('log', __name__)

@log_bp.route('/log')
def show_log():
    # 投稿ログの表示（新しい投稿順）
    posts = ScheduledPost.query.order_by(desc(ScheduledPost.created_at)).all()
    return render_template('admin_log.html', posts=posts)

@log_bp.route('/preview_post/<int:post_id>')
def preview_post(post_id):
    # 投稿IDを基に記事を取得
    post = ScheduledPost.query.get_or_404(post_id)
    
    # 記事のプレビュー表示
    if post.status == 'completed':
        return render_template('preview_post.html', post=post)
    else:
        return "記事がまだ生成されていません。", 400  # 生成されていない場合のエラーハンドリング
