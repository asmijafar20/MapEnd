from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,TextAreaField,SelectField
from wtforms.validators import DataRequired,Length

class ArticleForm(FlaskForm):
    title = StringField('Title',validators=[DataRequired(),Length(min=2,max=30)])
    body = TextAreaField('Content',validators=[DataRequired(),Length(min=2)])
    subject = SelectField('Subject', choices=[('english', 'English'), ('maths', 'Maths'), ('computer-science', 'Computer Science')])
    submit = SubmitField('Publish')