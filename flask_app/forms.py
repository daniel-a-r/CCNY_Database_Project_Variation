from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from flask_app.models import User
from flask_app import bcrypt
from flask_login import current_user

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=32)])
    confirm_password = PasswordField('Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError("Email doesn't exist.")

    def validate_password(self, password):
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            password_match = bcrypt.check_password_hash(user.password, password.data)
            if not password_match:
                raise ValidationError('Incorrect password')


class AlbumSearchForm(FlaskForm):
    album_name = StringField('Album Name', validators=[DataRequired()])
    submit = SubmitField('Search')
    

class UpdateNameForm(FlaskForm):
    new_name = StringField('New Name', validators=[DataRequired()])
    submit = SubmitField('Update Name')


class UpdateEmailForm(FlaskForm):
    new_email = StringField('New Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update Email')

    def validate_new_email(self, new_email):
        user = User.query.filter(User.email == new_email.data, User.id != current_user.id).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class UpdatePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(max=32)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Update Password')

    def validate_old_password(self, old_password):
        old_password_match = bcrypt.check_password_hash(current_user.password, old_password.data)

        if not old_password_match:
            raise ValidationError('Incorrect password')
    