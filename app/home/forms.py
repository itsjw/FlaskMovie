# encoding: utf-8
from flask import session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Regexp
from sqlalchemy import or_

from app import db
from app.models import User


class RegisterForm(FlaskForm):
    name = StringField(
        label="用户名：",
        validators=[DataRequired("请输入用户名！")],
        description="用户名",
        render_kw={"class": "form-control input-lg", "required": "required", "placeholder": "请输入用户名！"}
    )
    password = PasswordField(
        label="密码：",
        validators=[DataRequired("请输入密码！")],
        description="密码",
        render_kw={"class": "form-control input-lg", "required": "required", "placeholder": "请输入密码！"}
    )
    repeat_password = PasswordField(
        label="确认密码：",
        validators=[DataRequired("请确认密码！"), EqualTo("password", "两次输入的密码不一致！")],
        description="确认密码",
        render_kw={"class": "form-control input-lg", "required": "required", "placeholder": "请确认密码！"}
    )
    email = StringField(
        label="邮箱：",
        validators=[DataRequired("请输入邮箱！"), Email("邮箱格式不正确！")],
        description="邮箱",
        render_kw={"class": "form-control input-lg", "required": "required", "placeholder": "请输入邮箱！"}
    )
    phone = StringField(
        label="手机：",
        validators=[DataRequired("请输入手机！"), Regexp(r"^1[3578]\d{9}$", message="手机格式不正确")],
        description="手机",
        render_kw={"class": "form-control input-lg", "required": "required", "placeholder": "请输入手机！"}
    )
    submit = SubmitField(
        label="注册",
        render_kw={"class": "btn btn-lg btn-success btn-block"}
    )

    @staticmethod
    def validate_name(field):
        count = User.query.filter_by(name=field.data).count()
        if count:
            raise ValidationError("此用户名已存在！")

    @staticmethod
    def validate_email(field):
        count = User.query.filter_by(email=field.data).count()
        if count:
            raise ValidationError("此邮箱已存在！")

    @staticmethod
    def validate_phone(field):
        count = User.query.filter_by(phone=field.data).count()
        if count:
            raise ValidationError("此手机号已存在！")


class LoginForm(FlaskForm):
    password = PasswordField(
        label="密码：",
        validators=[DataRequired("请输入密码！")],
        description="密码",
        render_kw={"class": "form-control input-lg", "required": "required", "placeholder": "请输入密码！"}
    )
    name = StringField(
        label="账号：",
        validators=[DataRequired("请输入账号！")],
        description="账号",
        render_kw={"class": "form-control input-lg", "required": "required", "placeholder": "请输入用户名/邮箱/手机号"}
    )
    submit = SubmitField(
        label="登录",
        render_kw={"class": "btn btn-lg btn-success btn-block"}
    )

    def validate_password(self, field):
        self.password_field = field.data

    def validate_name(self, field):
        user = User.query.filter(
            or_(User.name == field.data,
                User.email == field.data,
                User.phone == field.data)
        ).first()
        if not user:
            raise ValidationError("账号不存在！")
        else:
            from werkzeug.security import check_password_hash
            if not check_password_hash(user.password, self.password_field):
                raise ValidationError("密码错误！")
            else:
                from flask import session
                session["user"] = field.data
                session["user_id"] = user.id


class UserDetailForm(FlaskForm):
    email = StringField(
        label="邮箱：",
        validators=[DataRequired("邮箱不能为空！"), Email("邮箱格式不正确")],
        description="邮箱",
        render_kw={"class": "form-control", "required": "required", "placeholder": "请输入邮箱！"}
    )
    phone = StringField(
        label="手机：",
        validators=[DataRequired("手机不能为空！"), Regexp(r"^1[3578]\d{9}$", message="手机格式不正确")],
        description="手机",
        render_kw={"class": "form-control", "required": "required", "placeholder": "请输入手机！"}
    )
    photo = FileField(
        label="头像：",
        description="头像",
        render_kw={"style": "display:inline"}
    )
    info = TextAreaField(
        label="简介：",
        description="简介",
        render_kw={"class": "form-control", "rows": "10"}
    )
    submit = SubmitField(
        label="保存修改",
        render_kw={"class": "btn btn-success"}
    )


class PasswordForm(FlaskForm):
    new_password = PasswordField(
        label="新密码：",
        validators=[DataRequired("请输入新密码！")],
        description="新密码",
        render_kw={"class": "form-control", "required": "required", "placeholder": "请输入新密码！"}
    )
    old_password = PasswordField(
        label="旧密码：",
        validators=[DataRequired("请输入旧密码！")],
        description="旧密码",
        render_kw={"class": "form-control", "required": "required", "placeholder": "请输入旧密码！"}
    )
    submit = SubmitField(
        label="修改密码",
        render_kw={"class": "btn btn-success"}
    )

    def validate_new_password(self, field):
        self.password_field = field.data

    def validate_old_password(self, field):
        user = User.query.get(session.get("user_id"))
        from werkzeug.security import check_password_hash, generate_password_hash
        if not check_password_hash(user.password, field.data):
            raise ValidationError("旧密码错误！")
        user.password = generate_password_hash(self.password_field)
        db.session.add(user)
        db.session.commit()


class CommentForm(FlaskForm):
    content = TextAreaField(
        label="内容：",
        validators=[DataRequired("请输入内容！")],
        description="评论内容",
        render_kw={"id": "input_content", "required": "required"}
    )
    submit = SubmitField(
        label="提交评论",
        render_kw={"class": "btn btn-success", "id": "btn-sub"}
    )
