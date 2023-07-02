from journal import db,login_manager
from datetime import datetime
from flask_login import UserMixin

'''
Will be using UserMixin because User model should have functions like is_authenticated,get_id
We can create them but it's easier to inherit them from UserMixin
'''

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20),unique=True,nullable=False)
    email = db.Column(db.String(100),unique=True,nullable=False)
    password = db.Column(db.String(60),nullable=False)
    role = db.Column(db.String(100),nullable=False)
    posts = db.relationship('Article',backref='author',lazy=True)

    def __repr__(self):
        return f"User('{self.username}','{self.email}')"


class Article(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(100),nullable=False)
    date_posted = db.Column(db.DateTime,nullable=False,default=datetime.utcnow())
    body = db.Column(db.Text,nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    quizid = db.Column(db.Integer,nullable=False)
    #Here using lower case User because this refers to the table name
    def __repr__(self):
        return f"Article('{self.title}','{self.date_posted}')"

class Quiz(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    question = db.Column(db.Text,nullable=False)
    answer = db.Column(db.Text,nullable=False)
    choiceA = db.Column(db.Text,nullable=False)
    choiceB = db.Column(db.Text,nullable=False)
    choiceC = db.Column(db.Text,nullable=False)
    #Here using lower case User because this refers to the table name
    def __repr__(self):
        return f"Quiz('{self.title}','{self.date_posted}')"