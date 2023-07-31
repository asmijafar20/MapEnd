from flask import Blueprint, flash, send_file, make_response, stream_with_context
from werkzeug.wsgi import FileWrapper
from journal.models import User,Article,Quiz,Question,Option,Response
from journal.main.forms import ArticleForm
from flask import render_template, flash,redirect,url_for, request,abort
from flask_login import current_user,login_required
from journal import db
from sqlalchemy import func
import csv
import io

main = Blueprint('main',__name__)

def count(object_):
    i = 0
    for x in object_:
        i = i+1
    return i

@main.route('/')
def index():
    return render_template('home.html')

#About
@main.route('/about')
def about():
    return render_template('about.html')

#courses
@main.route('/courses')
def articles():
    #debug this later
    articles = Article.query.order_by(Article.date_posted.desc())
    total = count(articles)
    if total>0:
        return render_template('articles.html',articles=articles)
    else:
        flash('Oops ! No Article found','success')
        return render_template('articles.html')

#Single course
@main.route('/articles/<string:id>/')
def article(id):
    article = Article.query.get_or_404(id)
    return render_template('article.html', article = article)

# Report
@main.route('/report')
def report():
    return render_template('report.html')

# generate CSV and export
@main.route('/generate_report')
def generate_report():
    # number of users, courses and quizes
    number_of_users = User.query.count()
    number_of_courses = Article.query.count()
    number_of_quizes = Quiz.query.count()
    # number % of users taking each quiz
    quiz_users = db.session.query(Quiz.title, Quiz.id, Response.student_id, Response.score).join(Response, Quiz.id == Response.quiz_id).distinct().subquery()
    quizes_userCount = db.session.query(quiz_users.c.title, func.count(quiz_users.c.student_id), func.avg(quiz_users.c.score).label("average_score")).group_by(quiz_users.c.id).all()
    percentage_per_quiz = [(title, count / number_of_users * 100,  count, average_score) for title, count, average_score in quizes_userCount]
    print(number_of_users)
    output = io.StringIO("")
    writer = csv.writer(output)
    writer.writerow(['Number of users', 'Number of courses', 'Number of quizes'])
    writer.writerow([number_of_users, number_of_courses, number_of_quizes])
    writer.writerow(['Quiz title', 'Percentage of users taking the quiz', 'Number of users taking the quiz', 'Average score'])
    for row in percentage_per_quiz:
        writer.writerow(row)

    data = output.getvalue()
    response = make_response(data)
    response.headers['Content-Disposition'] = 'attachment; filename=report.csv'
    response.mimetype = 'text/csv'

    return response

# Dashboard
@main.route('/dashboard')
def dashboard():
    #Debug this later
    user = User.query.filter_by(username=current_user.username)
    articles = Article.query.filter_by(user_id=current_user.id).order_by(Article.date_posted.desc())
    quizzes = Quiz.query.filter_by(interviewer_id=current_user.id).order_by(Quiz.date_posted.desc())
    users = User.query.order_by(User.id.asc())

    if current_user.role == 'admin':  
        return render_template('dashboard.html', users=users)
    elif current_user.role == 'interviewer':
        return render_template('dashboard.html', quizzes=quizzes)
    elif current_user.role == 'cs expert':
        return render_template('dashboard.html',articles=articles)
    else:
        return render_template('articles.html')
    # else:
    #     msg = 'No Articles Found'
    #     return render_template('dashboard.html', msg = msg)
   
    # #Close Connection
    # cur.close()

# Add course
@main.route('/add_course', methods=['GET','POST'])
@login_required
def add_article():
    form = ArticleForm()
    if form.validate_on_submit():
        # using author here (check backref in models.py)
        article = Article(title=form.title.data,body=form.body.data,author=current_user, subject=form.subject.data)
        db.session.add(article)
        db.session.commit()
        flash('Your course has been created !','success')
        return redirect(url_for('main.dashboard'))
    return render_template('add_article.html', form = form)


# Edit course
@main.route('/edit_course/<string:id>', methods=['GET','POST'])
@login_required
def edit_article(id):
    article = Article.query.get_or_404(id)
    if article.author != current_user:
        abort(403)

    form = ArticleForm()
    if form.validate_on_submit():
        article.title = form.title.data
        article.body = form.body.data
        db.session.commit()
        flash("Your article has been updated",'success')
        return redirect(url_for('main.article',id=article.id))
    elif request.method == 'GET':
        form.title.data = article.title
        form.body.data = article.body
    return render_template('edit_article.html',form=form)

# Delete course
@main.route("/article/<int:id>/delete",methods=['POST'])
@login_required
def delete(id):
    article = Article.query.get_or_404(id)
    if article.author != current_user:
        abort(403)
    db.session.delete(article)
    db.session.commit()
    flash("Your course has been deleted",'success')
    return redirect(url_for('main.dashboard'))

# Create Quiz
@main.route('/create_quiz', methods=['GET','POST'])
def create_quiz():

    if request.method == 'POST':
        # Get quiz details from the form
        title = request.form['title']
        questions = request.form.getlist('question')
        options = request.form.getlist('option')
        subject = request.form['subject']
        correct_answers = request.form.getlist('correct_answer')

        # Create a new quiz object
        quiz = Quiz(title=title,interviewer_id=current_user.id, subject=subject)

        optionCount=0

        # Create question and option objects and associate them with the quiz
        for question_text, correct_answer in zip(questions, correct_answers):
            question = Question(question_text=question_text, correct_answer=correct_answer, quiz=quiz)
            db.session.add(question)
            for i in range(optionCount,len(options)):
                option_text=options[i]
                option = Option(option_text=option_text, question=question)
                db.session.add(option)
                optionCount+=1
                if optionCount%4==0:
                    break

        # Commit the changes to the database
        db.session.commit()

        flash('Quiz created successfully!','success')
        return redirect(url_for('main.create_quiz'))
    
    return render_template('create_quiz.html')

# Display all quizzes
@main.route('/quizzes')
def quizzes():
    quizes_taken = current_user.quizes_taken
    quizes_taken_list = convert_string_to_list(quizes_taken)
    print(quizes_taken_list)

    #debug this later
    quizzes = Quiz.query.filter(Quiz.id.not_in(quizes_taken_list)).order_by(Quiz.date_posted.desc())
    total = count(quizzes)
    if total>0:
        return render_template('quizzes.html',quizzes=quizzes)
    else:
        flash('Oops ! No Article found','success')
        return render_template('quizzes.html')

# Delete Quiz
@main.route("/quizzes/<int:id>/delete_quiz",methods=['POST'])
@login_required
def delete_quiz(id):
    quiz = Quiz.query.get_or_404(id)
    if quiz.interviewer != current_user:
        abort(403)
    db.session.delete(quiz)
    db.session.commit()
    flash("Your quiz has been deleted",'success')
    return redirect(url_for('main.quiz_dashboard'))

# Dashboard
@main.route('/quiz_dashboard')
def quiz_dashboard():
    #Debug this later
    user = User.query.filter_by(username=current_user.username)
    quizzes = Quiz.query.filter_by(interviewer_id=current_user.id).order_by(Quiz.date_posted.desc())
    
    return render_template('quiz_dashboard.html',quizzes=quizzes)
    # else:
    #     msg = 'No Articles Found'
    #     return render_template('dashboard.html', msg = msg)
   
    # #Close Connection
    # cur.close()

@main.route('/quizzes/<int:id>', methods=['GET', 'POST'])
def take_quiz(id):
    quiz = Quiz.query.get_or_404(id)

    if request.method == 'POST':
        # Get student's responses from the form
        responses = request.form.getlist('response')

        # Create a new Response object and associate it with the quiz and the current user
        response = Response(quiz_id=quiz.id,student_id=current_user.id, responses=responses)

        # Save the response to the database
        db.session.add(response)
        db.session.commit()

        response.calculate_score()

        # Update the quizzes_taken for the current user
        quizes_taken_data = current_user.quizes_taken
        quizes_taken_data = add_to_quizes_taken(quiz, quizes_taken_data)
        current_user.quizes_taken = quizes_taken_data
        db.session.commit()
        flash('Quiz submitted successfully!', 'success')
        return redirect(url_for('main.quizzes'))

    return render_template('take_quiz.html', quiz=quiz)

def add_to_quizes_taken(quiz, quizes_taken_data):
    if not quizes_taken_data:
        quizes_taken_data = ""
        quizes_taken_data += f"{quiz.id},"
        current_user.quizes_taken = quizes_taken_data
    else :
        quizes_taken_set = convert_string_to_list(quizes_taken_data)
        if quiz.id not in quizes_taken_set:
            quizes_taken_data += f"{quiz.id},"

    return quizes_taken_data

def convert_string_to_list(quizes_taken_data):
    if not quizes_taken_data:
        return []
    quizes_taken_set = []
    number = ""
    for char in quizes_taken_data:
        if char != ',':
            number += char
            continue
        else :
            quizes_taken_set.append(int(number))
            number = ""
    return quizes_taken_set


@main.route('/admin_dashboard')
def admin_dashboard():
    #Debug this later
    # users = User.query.filter_by(id=current_user.id).order_by(User.id.desc())
    users = User.query.order_by(User.id.desc()).all()
    
    return render_template('dashboard.html',users=users)    

# Delete User
@main.route("/users/<int:id>/delete_user",methods=['POST'])
@login_required
def delete_user(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    flash("User has been deleted",'success')
    return redirect(url_for('main.admin_dashboard'))

#Response Dashboard

@main.route('/response_dashboard')
def response_dashboard():
    # Get all responses along with the associated user's email
    responses_with_email = db.session.query(Response, User.username, User.email).join(User, Response.student_id == User.id).all()
    # Create a list to store the data for each student
    student_scores = []

    for response, username, email in responses_with_email:
        # Calculate the score for each response
        response.calculate_score()

        # Append the response id, student's email, and score to the list
        student_scores.append({'id': response.id, 'username': username, 'email': email, 'score': response.score})

    return render_template('response_dashboard.html', student_scores=student_scores)