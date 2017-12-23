# encoding: utf-8
from flask import render_template, redirect, url_for, flash, request

from .. import admin
from app import db
from app.models import User
from app.utils import login_required_wraps


@admin.route("/user-list/")
@admin.route("/user-list/<int:page>/")
@login_required_wraps("admin", "admin.login")
def user_list(page=1):
    pagination = User.query.order_by(User.id.desc()).paginate(page=page, per_page=5)
    return render_template("admin/user_list.html", pagination=pagination)


@admin.route("/user-view/<int:user_id>")
@login_required_wraps("admin", "admin.login")
def user_view(user_id):
    user = User.query.get_or_404(user_id)
    return render_template("admin/user_view.html", user=user)


@admin.route("/user-delete/<int:user_id>", methods=["POST"])
@login_required_wraps("admin", "admin.login")
def user_delete(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("删除会员", "succeed")
    page = request.args.get("page", 1)
    return redirect(url_for("admin.user_list", page=page))
