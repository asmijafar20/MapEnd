from flask import Blueprint
from journal.models import Quiz, User,Article
from journal.main.forms import ArticleForm, QuizForm
from flask import render_template, flash,redirect,url_for, request,abort
from flask_login import current_user,login_required
from journal import db

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
    
    return render_template('dashboard.html',articles=articles)
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

# Add quiz
@main.route('/add_quiz', methods=['GET','POST'])
@login_required
def add_quiz():
    form = QuizForm()
    if form.validate_on_submit():
        # using author here (check backref in models.py)
        quiz = Quiz(question=form.title.data,choices=form.body.data,answer=current_user)
        db.session.add(quiz)
        db.session.commit()
        flash('Your quiz has been created !','success')
        return redirect(url_for('main.dashboard'))
    return render_template('add_quiz.html', form = form)


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

@main.route('/quizes')
def quizes():
    articles = Quiz.query.all()
    total = count(articles)
    if total>0:
        return render_template('quizes.html',articles=articles)
    else:
        flash('Oops ! No Article found','success')
        return render_template('quizes.html')
    # else:
    #     msg = 'No Articles Found'
    #     return render_template('dashboard.html', msg = msg)
   
    # #Close Connection
    # cur.close()


#Single quiz
@main.route('/quiz/<string:id>/')
def quiz(id):
    quiz = Quiz.query.get_or_404(id)
    return render_template('quiz.html', quiz = quiz)
