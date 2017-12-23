# coding=utf-8
from app import create_app

app = create_app()


def forged():
    from forgery_py import basic, lorem_ipsum, internet
    from app import db
    from app.models import User, Admin, Role
    from uuid import uuid4

    db.drop_all()
    db.create_all()

    role = Role(name="超级管理员")
    db.session.add(role)
    db.session.commit()

    admin = Admin(
        name="admin",
        password="pbkdf2:sha256:50000$195qPZeh$dca6cde9acbea0ac96caa6c83f03f0285747a5c8a7861fee6019e1ddd2704cec",
        is_super=0,
        role_id=1
    )
    db.session.add(admin)
    db.session.commit()

    def generate_user(i):
        return User(
            name="%s%s" % (internet.user_name(), i),
            password=basic.text(8, at_least=8, spaces=False),
            email=internet.email_address(),
            phone=basic.text(11, at_least=11, lowercase=False, uppercase=False, spaces=False),
            info=lorem_ipsum.paragraphs(),
            photo="%s.jpg" % i,
            uuid=uuid4().hex,
        )

    users = [generate_user(i) for i in range(1, 21)]
    db.session.add_all(users)
    db.session.commit()


def forged_comment():
    from random import randint
    from forgery_py import lorem_ipsum
    from app import db
    from app.models import Comment, User, Movie

    users = User.query.all()
    movie = Movie.query.get(1)

    def generate_comment():
        return Comment(
            content=lorem_ipsum.word(),
            movie_id=movie.id,
            user_id=users[randint(1, 10)].id,
        )

    comments = [generate_comment() for i in range(20)]
    db.session.add_all(comments)
    db.session.commit()


def forged_movie_collect():
    from random import randint
    from app import db
    from app.models import MovieCollect, User, Movie

    users = User.query.all()
    movie = Movie.query.get(1)

    def generate_movie_collect():
        return MovieCollect(
            movie_id=movie.id,
            user_id=users[randint(1, 10)].id,
        )

    movie_collects = [generate_movie_collect() for i in range(20)]
    db.session.add_all(movie_collects)
    db.session.commit()


def forged_user_login_log():
    from random import randint
    from app import db
    from app.models import UserLog, User

    users = User.query.all()

    def generate_log():
        return UserLog(
            user_id=users[randint(1, 10)].id,
            ip="192.168.1.1",
        )

    logs = [generate_log() for i in range(10)]
    db.session.add_all(logs)
    db.session.commit()


if __name__ == '__main__':
    app.run()
