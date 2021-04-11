from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from flask import Blueprint
from functools import wraps
from journal import db,bcrypt
from flask import render_template, flash,redirect,url_for, request,current_app
from flask_login import login_user,current_user,logout_user,login_required
from journal.auth.forms import LoginForm,RegistrationForm
from journal.models import User


auth = Blueprint('auth',__name__)

@auth.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.articles'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}! You are able to Login.','success')
        return redirect(url_for('auth.login'))
    return render_template('register.html',form=form)


@auth.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.blog'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        try:
            check = bcrypt.check_password_hash(user.password,form.password.data)
        except:
            check = None
        if user and check != None:
            # login_user takes user and remember as arg
            login_user(user,remember=form.remember.data)
            flash('You have been logged in.','success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Login Unsucessful. Please check email and password','danger')
    return render_template('login.html',form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))
