# encoding: utf-8
from flask import render_template, redirect, url_for, flash, request

from .. import admin
from app import db
from app.models import Comment
from app.utils import login_required_wraps


@admin.route("/comment-list/")
@admin.route("/comment-list/<int:page>/")
@login_required_wraps("admin", "admin.login")
def comment_list(page=1):
    pagination = Comment.query.order_by(Comment.add_time.desc()).paginate(page=page, per_page=5)
    return render_template("admin/comment_list.html", pagination=pagination)


@admin.route("/comment-delete/<int:comment_id>", methods=["POST"])
@login_required_wraps("admin", "admin.login")
def comment_delete(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash("删除评论", "succeed")
    page = request.args.get("page", 1)
    return redirect(url_for("admin.comment_list", page=page))
