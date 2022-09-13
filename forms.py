from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email,EqualTo

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(),Email()])
    password = PasswordField('Password'#, validators=[InputRequired()])
                             )
    submit = SubmitField('Login')

class SignUp(FlaskForm):
    name = StringField("Name",validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(),Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    password2 = PasswordField("Confirm Password",
                              validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class Saver(FlaskForm):
    website = StringField("Website",validators=[InputRequired()])
    username = StringField('Username',validators=[InputRequired()])
    password = PasswordField('Password')
    submit = SubmitField('Save')

class Update(FlaskForm):
    website = StringField("Website",validators=[InputRequired()])
    username = StringField('Username',validators=[InputRequired()])
    password = PasswordField('Password')
    submit = SubmitField('Update')

class Forgot(FlaskForm):
    email = StringField('Email', validators=[InputRequired(),Email()])
    submit = SubmitField('Send')

class UpdatePassword(FlaskForm):
    password = PasswordField('Password', validators=[InputRequired()])
    password2 = PasswordField("Confirm Password",
                              validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Update Password')