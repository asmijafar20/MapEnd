from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,TextAreaField
from wtforms.validators import DataRequired,Length

class ArticleForm(FlaskForm):
    title = StringField('Title',validators=[DataRequired(),Length(min=2,max=30)])
    body = TextAreaField('Content',validators=[DataRequired(),Length(min=2)])
    submit = SubmitField('Publish')