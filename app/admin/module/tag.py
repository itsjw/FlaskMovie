# encoding: utf-8
from flask import render_template, redirect, url_for, flash
from flask_wtf import csrf

from .. import admin
from ..forms import TagForm
from app import db
from app.models import Tag
from app.utils import login_required_wraps


@admin.route("/tag-add/", methods=["GET", "POST"])
@login_required_wraps("admin", "admin.login")
def tag_add():
    form = TagForm()
    if form.validate_on_submit():
        count = Tag.query.filter_by(name=form.name.data).count()
        if count:
            flash("此标签已存在", "fail")
        else:
            tag = Tag(name=form.name.data)
            db.session.add(tag)
            db.session.commit()
            flash("添加标签成功", "succeed")
            return redirect(url_for("admin.tag_add"))
    return render_template("admin/tag_add.html", title="添加标签", btn="添加", form=form)


@admin.route("/tag-delete/<int:tag_id>/", methods=["POST"])
@login_required_wraps("admin", "admin.login")
def tag_delete(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    flash("删除标签", "succeed")
    return redirect(url_for("admin.tag_list"))


@admin.route("/tag-edit/<int:tag_id>/", methods=["GET", "POST"])
@login_required_wraps("admin", "admin.login")
def tag_edit(tag_id):
    form = TagForm()
    tag = Tag.query.get_or_404(tag_id)
    if form.validate_on_submit():
        obj = Tag.query.filter_by(name=form.name.data).first()
        if obj and obj is not tag:
            flash("此标签已存在", "fail")
        else:
            tag.name = form.name.data
            db.session.add(tag)
            db.session.commit()
            flash("修改标签", "succeed")
            return redirect(url_for("admin.tag_list"))

    form.name.data = tag.name
    return render_template("admin/tag_add.html", title="修改标签", btn="修改", form=form)


@admin.route("/tag-list/")
@admin.route("/tag-list/<int:page>/")
@login_required_wraps("admin", "admin.login")
def tag_list(page=1):
    pagination = Tag.query.order_by(Tag.add_time.desc()).paginate(page=page, per_page=1)
    csrf_token = csrf.generate_csrf()
    return render_template("admin/tag_list.html", pagination=pagination, csrf_token=csrf_token)
