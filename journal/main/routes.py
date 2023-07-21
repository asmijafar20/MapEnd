from flask import Blueprint, flash
from journal.models import User,Article,Quiz,Question,Option,Response
from journal.main.forms import ArticleForm
from flask import render_template, flash,redirect,url_for, request,abort
from flask_login import current_user,login_required
from journal import db
import json

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

#Articles
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

#Single Article
@main.route('/articles/<string:id>/')
def article(id):
    article = Article.query.get_or_404(id)
    return render_template('article.html', article = article)

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

# Add Article
@main.route('/add_course', methods=['GET','POST'])
@login_required
def add_article():
    form = ArticleForm()
    if form.validate_on_submit():
        # using author here (check backref in models.py)
        article = Article(title=form.title.data,body=form.body.data,author=current_user)
        db.session.add(article)
        db.session.commit()
        flash('Your article has been created !','success')
        return redirect(url_for('main.dashboard'))
    return render_template('add_article.html', form = form)


# Edit Article
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

# Delete Article
@main.route("/article/<int:id>/delete",methods=['POST'])
@login_required
def delete(id):
    article = Article.query.get_or_404(id)
    if article.author != current_user:
        abort(403)
    db.session.delete(article)
    db.session.commit()
    flash("Your article has been deleted",'success')
    return redirect(url_for('main.dashboard'))

# Create Quiz
@main.route('/create_quiz', methods=['GET','POST'])
def create_quiz():

    if request.method == 'POST':
        # Get quiz details from the form
        title = request.form['title']
        questions = request.form.getlist('question')
        options = request.form.getlist('option')
        correct_answers = request.form.getlist('correct_answer')

        # Create a new quiz object
        quiz = Quiz(title=title,interviewer_id=current_user.id)

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
    #debug this later
    quizzes = Quiz.query.order_by(Quiz.date_posted.desc())
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
        if not quizes_taken_data:
            quizes_taken_data = []
        quizes_taken_data.append(quiz.id)
        current_user.quizes_taken = quizes_taken_data
        print(quizes_taken_data)
        db.session.commit()


        flash('Quiz submitted successfully!', 'success')
        return redirect(url_for('main.quizzes'))

    return render_template('take_quiz.html', quiz=quiz)


@main.route('/admin_dashboard')
def admin_dashboard():
    #Debug this later
    user = User.query.filter_by(username=current_user.username)
    users = User.query.filter_by(id=current_user.id).order_by(User.id.desc())
    
    return render_template('dashboard.html',users=users)
    # else:
    #     msg = 'No Articles Found'
    #     return render_template('dashboard.html', msg = msg)
   
    # #Close Connection
    # cur.close()
    

# Delete User
@main.route("/users/<int:id>/delete_user",methods=['POST'])
@login_required
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete_user(user)
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