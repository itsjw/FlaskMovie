# encoding: utf-8
from flask import render_template, redirect, url_for, flash

from .. import admin
from ..forms import AuthForm
from app import db
from app.models import Auth
from app.utils import login_required_wraps


@admin.route("/auth-add/", methods=["GET", "POST"])
@login_required_wraps("admin", "admin.login")
def auth_add():
    form = AuthForm()
    if form.validate_on_submit():
        from sqlalchemy import or_
        count = Auth.query.filter(or_(Auth.name == form.name.data, Auth.url == form.url.data)).count()
        if count:
            flash("此权限名或此链接已经存在", "fail")
        else:
            auth = Auth(name=form.name.data, url=form.url.data)
            db.session.add(auth)
            db.session.commit()
            flash("添加权限", "succeed")
            return redirect(url_for("admin.auth_add"))
    return render_template("admin/auth_add.html", title="添加权限", btn="添加", form=form)


@admin.route("/auth-delete/<int:auth_id>/", methods=["POST"])
@login_required_wraps("admin", "admin.login")
def auth_delete(auth_id):
    auth = Auth.query.get(auth_id)
    db.session.delete(auth)
    db.session.commit()
    flash("删除权限", "succeed")
    return redirect(url_for("admin.auth_list"))


@admin.route("/auth-edit/<int:auth_id>/", methods=["GET", "POST"])
@login_required_wraps("admin", "admin.login")
def auth_edit(auth_id):
    form = AuthForm()
    auth = Auth.query.get_or_404(auth_id)
    if form.validate_on_submit():
        from sqlalchemy import or_
        obj = Auth.query.filter(or_(Auth.name == form.name.data, Auth.url == form.url.data)).first()
        if obj and obj is not auth:
            flash("此权限名或此链接已经存在", "fail")
        else:
            auth.name = form.name.data
            auth.url = form.url.data
            db.session.add(auth)
            db.session.commit()
            flash("编辑权限", "succeed")
            return redirect(url_for("admin.auth_list"))
    form.name.data = auth.name
    form.url.data = auth.url
    return render_template("admin/auth_add.html", title="编辑权限", btn="编辑", form=form)


@admin.route("/auth-list/")
@admin.route("/auth-list/<int:page>/")
@login_required_wraps("admin", "admin.login")
def auth_list(page=1):
    pagination = Auth.query.order_by(Auth.add_time.desc()).paginate(page=page, per_page=2)
    return render_template("admin/auth_list.html", pagination=pagination)
