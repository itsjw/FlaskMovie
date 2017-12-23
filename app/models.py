# encoding: utf-8
from datetime import datetime
from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(128))
    email = db.Column(db.String(50), unique=True)
    phone = db.Column(db.String(11), unique=True)
    info = db.Column(db.Text, default="")
    photo = db.Column(db.String(128), unique=True)
    uuid = db.Column(db.String(128), unique=True)
    add_time = db.Column(db.DATETIME, index=True, default=datetime.now)
    userlogs = db.relationship("UserLog", backref="user")
    comments = db.relationship("Comment", backref="user")
    moviecollects = db.relationship("MovieCollect", backref="user")

    def __repr__(self):
        return "<User %s>" % self.name


class UserLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(128))
    add_time = db.Column(db.DATETIME, index=True, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return "<UserLog %s:%s>" % (self.id, self.ip)


# house_facility = db.Table(
#     "movie_tag",
#     db.Column("movie_id", db.Integer, db.ForeignKey("Movie.id"), primary_key=True),
#     db.Column("tag_id", db.Integer, db.ForeignKey("Tag.id"), primary_key=True)
# )


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)
    movies = db.relationship("Movie", backref="tag")

    def __repr__(self):
        return "<Tag %s>" % self.name


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), unique=True)
    url = db.Column(db.String(255), unique=True)
    info = db.Column(db.Text)
    logo = db.Column(db.String(128), unique=True)
    star_level = db.Column(db.SmallInteger)
    play_num = db.Column(db.Integer, default=0)
    comment_num = db.Column(db.Integer, default=0)
    area = db.Column(db.String(128))
    length = db.Column(db.String(128))
    release_time = db.Column(db.Date)
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)
    tag_id = db.Column(db.Integer, db.ForeignKey("tag.id"))
    comments = db.relationship("Comment", backref="movie")
    moviecollects = db.relationship("MovieCollect", backref="movie")

    def __repr__(self):
        return "<Movie %s>" % self.title


class Preview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), unique=True)
    logo = db.Column(db.String(128), unique=True)
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return "<Preview %s>" % self.title


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)
    movie_id = db.Column(db.Integer, db.ForeignKey("movie.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return "<Comment %s>" % self.id


class MovieCollect(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)
    movie_id = db.Column(db.Integer, db.ForeignKey("movie.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return "<MovieCollect %s>" % self.id


class Auth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    url = db.Column(db.String(255), unique=True)
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return "<Auth %s>" % self.name


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    auths = db.Column(db.String(500))
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)
    admins = db.relationship("Admin", backref="role")

    def __repr__(self):
        return "<Role %s>" % self.name


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(128))
    is_super = db.Column(db.SmallInteger)
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))
    adminlogs = db.relationship("AdminLog", backref="admin")
    operationlogs = db.relationship("OperationLog", backref="admin")

    def __repr__(self):
        return "<Admin %s>" % self.name

    def check_password(self, passwrod):
        pass


class AdminLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(128))
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)
    admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"))

    def __repr__(self):
        return "<AdminLog %s>" % self.id


class OperationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(128))
    reason = db.Column(db.String(500))
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)
    admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"))

    def __repr__(self):
        return "<OperationLog %s>" % self.id
