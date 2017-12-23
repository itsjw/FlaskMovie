# encoding: utf-8
import os

from flask import render_template, redirect, url_for, flash, current_app
from flask_wtf import csrf
from werkzeug.utils import secure_filename

from .. import admin
from ..forms import PreviewForm
from app import db
from app.models import Preview
from app.utils import login_required_wraps, handle_filename


@admin.route("/preview-add/", methods=["GET", "POST"])
@login_required_wraps("admin", "admin.login")
def preview_add():
    form = PreviewForm()
    if form.validate_on_submit():
        count = Preview.query.filter_by(title=form.title.data).count()
        if count:
            flash("此预告标题已经存在", "fail")
        else:
            filename = handle_filename(secure_filename(form.logo.data.filename))
            preview = Preview(title=form.title.data, logo=filename)
            form.logo.data.save(os.path.join(current_app.config["UPLOAD_DIR"], filename))
            db.session.add(preview)
            db.session.commit()
            flash("添加预告", "succeed")
            return redirect(url_for("admin.preview_add"))
    return render_template("admin/preview_add.html", title="添加预告", btn="添加", form=form)


@admin.route("/preview-delete/<int:preview_id>", methods=["POST"])
@login_required_wraps("admin", "admin.login")
def preview_delete(preview_id):
    preview = Preview.query.get_or_404(preview_id)
    db.session.delete(preview)
    db.session.commit()
    flash("删除预告", "succeed")
    return redirect(url_for("admin.preview_list"))


@admin.route("/preview-edit/<int:preview_id>/", methods=["GET", "POST"])
@login_required_wraps("admin", "admin.login")
def preview_edit(preview_id):
    form = PreviewForm()
    preview = Preview.query.get_or_404(preview_id)

    form.logo.validators = []
    if form.validate_on_submit():
        obj = Preview.query.filter_by(title=form.title.data).first()
        if obj and obj is not preview:
            flash("预告已存在", "fail")
        else:
            if secure_filename(form.logo.data.filename):
                filename = handle_filename(secure_filename(form.logo.data.filename))
                preview.logo = filename
                form.logo.data.save(os.path.join(current_app.config["UPLOAD_DIR"], filename))
            preview.title = form.title.data

            db.session.add(preview)
            db.session.commit()
            flash("修改成功", "succeed")
            return redirect(url_for("admin.preview_list"))

    form.title.data = preview.title
    return render_template("admin/preview_add.html", title="编辑预告", btn="编辑", form=form, preview=preview)


@admin.route("/preview-list/")
@admin.route("/preview-list/<int:page>/")
@login_required_wraps("admin", "admin.login")
def preview_list(page=1):
    pagination = Preview.query.order_by(Preview.add_time.desc()).paginate(page=page, per_page=1)
    csrf_token = csrf.generate_csrf()
    return render_template("admin/preview_list.html", pagination=pagination, csrf_token=csrf_token)
