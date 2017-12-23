# encoding: utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FileField, SelectField, SelectMultipleField
from wtforms.validators import ValidationError, DataRequired, EqualTo

from app.models import Admin, Tag, Auth, Role


class LoginForm(FlaskForm):
    password = PasswordField(
        label="密码：",
        validators=[DataRequired("请输入密码！")],
        description="密码",
        render_kw={"class": "form-control", "required": "required", "placeholder": "请输入密码！"}
    )
    account = StringField(
        label="账号：",
        validators=[DataRequired("请输入账号！")],
        description="账号",
        render_kw={"class": "form-control", "required": "required", "placeholder": "请输入账号！"}
    )
    submit = SubmitField(
        label="登录",
        render_kw={"class": "btn btn-primary btn-block btn-flat"}
    )

    def validate_password(self, field):
        self.password_field = field.data

    def validate_account(self, field):
        account = field.data
        admin = Admin.query.filter_by(name=account).first()
        if admin is None:
            raise ValidationError("账号或密码错误！")
        else:
            from werkzeug.security import check_password_hash
            if not check_password_hash(admin.password, self.password_field):
                raise ValidationError("账号或密码错误！")
            else:
                from flask import session
                session["admin"] = field.data
                session["admin_id"] = admin.id


class TagForm(FlaskForm):
    name = StringField(
        label="标签名称：",
        validators=[DataRequired("请输入标签名称！")],
        description="标签",
        render_kw={"class": "form-control", "required": "required", "placeholder": "请输入标签名称！"}
    )
    submit = SubmitField(
        label="添加",
        render_kw={"class": "btn btn-primary"}
    )


class MovieForm(FlaskForm):
    title = StringField(
        label="片名",
        validators=[DataRequired("请输入片名！")],
        description="片名",
        render_kw={"class": "form-control", "required": "required", "placeholder": "请输入片名！"}
    )
    url = FileField(
        label="文件：",
        validators=[DataRequired("请上传视频文件！")],
        description="文件"
    )
    info = TextAreaField(
        label="简介：",
        validators=[DataRequired("请输入简介！")],
        description="简介",
        render_kw={"class": "form-control", "rows": "10", "required": "required", "placeholder": "请输入简介！"}
    )
    logo = FileField(
        label="封面：",
        validators=[DataRequired("请上传封面！")],
        description="封面"
    )
    star_level = SelectField(
        label="星级：",
        validators=[DataRequired()],
        coerce=int,
        choices=[(1, "1星"), (2, "2星"), (3, "3星"), (4, "4星"), (5, "5星")],
        description="星级",
        render_kw={"class": "form-control"}
    )
    tag_id = SelectField(
        label="标签：",
        validators=[DataRequired()],
        coerce=int,
        choices=[(obj.id, obj.name) for obj in Tag.query.all()],
        description="标签",
        render_kw={"class": "form-control"}
    )
    area = StringField(
        label="地区：",
        validators=[DataRequired("请输入地区！")],
        description="地区",
        render_kw={"class": "form-control", "required": "required", "placeholder": "请输入地区！"}
    )
    length = StringField(
        label="片长：",
        validators=[DataRequired("请输入片长！")],
        description="片长",
        render_kw={"class": "form-control", "required": "required", "placeholder": "请输入片长！"}
    )
    release_time = StringField(
        label="上映时间：",
        validators=[DataRequired("请选择上映时间！")],
        description="上映时间",
        render_kw={"class": "form-control", "id": "input_release_time", "placeholder": "请选择上映时间！"}
    )
    submit = SubmitField(
        label="添加",
        render_kw={"class": "btn btn-primary"}
    )


class PreviewForm(FlaskForm):
    title = StringField(
        label="预告标题：",
        validators=[DataRequired("请输入标题！")],
        description="预告标题",
        render_kw={"class": "form-control", "required": "required", "placeholder": "请输入标题！"}
    )
    logo = FileField(
        label="预告封面：",
        validators=[DataRequired("请上传封面！")],
        description="预告封面",
    )
    submit = SubmitField(
        label="添加",
        render_kw={"class": "btn btn-primary"}
    )


class PasswordForm(FlaskForm):
    old_password = PasswordField(
        label="旧密码：",
        validators=[DataRequired("请输入旧密码！")],
        description="旧密码",
        render_kw={"class": "form-control", "required": "required", "placeholder": "请输入旧密码！"}
    )
    new_password = PasswordField(
        label="新密码：",
        validators=[DataRequired("请输入新密码！")],
        description="新密码",
        render_kw={"class": "form-control", "required": "required", "placeholder": "请输入新密码！"}
    )
    submit = SubmitField(
        label="修改",
        render_kw={"class": "btn btn-primary"}
    )

    def validate_old_password(self, field):
        from flask import session
        name = session.get("admin")
        if name:
            from werkzeug.security import check_password_hash
            admin = Admin.query.filter_by(name=name).first()
            if not check_password_hash(admin.password, field.data):
                raise ValidationError("旧密码错误！")


class AuthForm(FlaskForm):
    name = StringField(
        label="权限名称：",
        validators=[DataRequired("请输入权限名称！")],
        description="权限名称",
        render_kw={"class": "form-control", "required": "required", "placeholder": "请输入权限名称！"}
    )
    url = StringField(
        label="权限地址：",
        validators=[DataRequired("请输入权限地址！")],
        description="权限地址",
        render_kw={"class": "form-control", "required": "required", "placeholder": "请输入权限地址！"}
    )
    submit = SubmitField(
        label="添加",
        render_kw={"class": "btn btn-primary"}
    )


class RoleForm(FlaskForm):
    name = StringField(
        label="角色名称：",
        validators=[DataRequired("请输入角色名称！")],
        description="角色名称",
        render_kw={"class": "form-control", "required": "required", "placeholder": "请输入角色名称！"}
    )
    auths = SelectMultipleField(
        label="权限列表：",
        validators=[DataRequired("请选择权限！")],
        description="权限列表",
        coerce=int,
        choices=[(obj.id, obj.name) for obj in Auth.query.all()],
        render_kw={"class": "form-control", "required": "required"}
    )
    submit = SubmitField(
        label="添加",
        render_kw={"class": "btn btn-primary"}
    )


class AdminForm(FlaskForm):
    name = StringField(
        label="名称：",
        validators=[DataRequired("请输入名称！")],
        description="管理员名称",
        render_kw={"class": "form-control", "required": "required", "placeholder": "请输入名称！"}
    )
    password = PasswordField(
        label="密码：",
        validators=[DataRequired("请输入密码！")],
        description="密码",
        render_kw={"class": "form-control", "required": "required", "placeholder": "请输入密码！"}
    )
    repeat_password = PasswordField(
        label="确认密码：",
        validators=[DataRequired("请输入密码！"), EqualTo("password", message="两次密码不一致！")],
        description="确认密码",
        render_kw={"class": "form-control", "required": "required", "placeholder": "请确认密码！"}
    )
    role_id = SelectField(
        label="所属角色",
        validators=[DataRequired("请选择所属角色！")],
        description="所属角色",
        coerce=int,
        choices=[(obj.id, obj.name) for obj in Role.query.all()],
        render_kw={"class": "form-control", "required": "required"}
    )
    submit = SubmitField(
        label="添加",
        render_kw={"class": "btn btn-primary"}
    )
