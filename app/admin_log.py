from flask import Blueprint, render_template
from .models import ScheduledPost
from sqlalchemy import desc

log_bp = Blueprint('log', __name__)

@log_bp.route('/log')
def show_log():
    posts = ScheduledPost.query.order_by(desc(ScheduledPost.created_at)).all()
    return render_template('admin_log.html', posts=posts)
