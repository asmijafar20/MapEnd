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
    quizzes = db.relationship('Quiz', backref='interviewer',lazy=True)
    quiz_taken = db.Column(db.String(255))
    quizes_taken = db.Column(db.JSON, nullable=False)

    def __repr__(self):
        return f"User('{self.username}','{self.email}')"


class Article(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(100),nullable=False)
    date_posted = db.Column(db.DateTime,nullable=False,default=datetime.utcnow())
    body = db.Column(db.Text,nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    #Here using lower case User because this refers to the table name
    def __repr__(self):
        return f"Article('{self.title}','{self.date_posted}')"

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(255))
    questions = db.relationship('Question', backref='quiz', cascade='all, delete-orphan')
    interviewer_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    date_posted = db.Column(db.DateTime,nullable=False,default=datetime.utcnow())

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(255))
    options = db.relationship('Option', backref='question', cascade='all, delete-orphan', lazy=True)
    correct_answer = db.Column(db.String(255))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    option_text = db.Column(db.String(255))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    responses = db.Column(db.JSON, nullable=False)
    score = db.Column(db.Float)

    def calculate_score(self):
        # Get the quiz associated with this response
        quiz = Quiz.query.get(self.quiz_id)

        # Check if the quiz exists
        if quiz is not None:
            total_questions = len(quiz.questions)
            correct_responses = 0

            for question, response in zip(quiz.questions, self.responses):
                if response == question.correct_answer:
                    correct_responses += 1

            self.score = (correct_responses / total_questions) * 100
            db.session.commit()
        else:
            # Handle the case when the quiz does not exist
            # You can log an error or take appropriate action here
            print("no quiz exist")
            pass
        
