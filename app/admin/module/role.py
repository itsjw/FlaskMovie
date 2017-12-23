# encoding: utf-8
from flask import render_template, redirect, url_for, flash

from .. import admin
from ..forms import RoleForm
from app import db
from app.models import Role
from app.utils import login_required_wraps


@admin.route("/role-add/", methods=["GET", "POST"])
@login_required_wraps("admin", "admin.login")
def role_add():
    form = RoleForm()
    if form.validate_on_submit():
        count = Role.query.filter_by(name=form.name.data).count()
        if count:
            flash("此角色已存在", "fail")
        else:
            role = Role(name=form.name.data, auths=str(form.auths.data))
            db.session.add(role)
            db.session.commit()
            flash("添加角色", "succeed")
            return redirect(url_for("admin.role_add"))
    return render_template("admin/role_add.html", title="添加角色", btn="添加", form=form)


@admin.route("/role-delete/<int:role_id>/", methods=["POST"])
@login_required_wraps("admin", "admin.login")
def role_delete(role_id):
    role = Role.query.get_or_404(role_id)
    db.session.delete(role)
    db.session.commit()
    flash("删除角色", "succeed")
    return redirect(url_for("admin.role_list"))


@admin.route("/role-edit/<int:role_id>/", methods=["GET", "POST"])
@login_required_wraps("admin", "admin.login")
def role_edit(role_id):
    form = RoleForm()
    role = Role.query.get_or_404(role_id)
    if form.validate_on_submit():
        obj = Role.query.filter_by(name=form.name.data).first()
        if obj and obj is not role:
            flash("此角色名已存在", "fail")
        else:
            role.name = form.name.data
            role.auths = str(form.auths.data)
            db.session.add(role)
            db.session.commit()
            flash("修改角色", "succeed")
            return redirect(url_for("admin.role_list"))
    import json
    form.name.data = role.name
    form.auths.data = json.loads(role.auths)
    return render_template("admin/role_add.html", title="编辑角色", btn="编辑", form=form)


@admin.route("/role-list/")
@admin.route("/role-list/<int:page>/")
@login_required_wraps("admin", "admin.login")
def role_list(page=1):
    pagination = Role.query.order_by(Role.add_time.desc()).paginate(page=page, per_page=1)
    return render_template("admin/role_list.html", pagination=pagination)
