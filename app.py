from flask import Flask,render_template,session, redirect, url_for
from forms import LoginForm,SignUp,Saver,Update,Forgot,UpdatePassword
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from emailer import Email,Message
from itsdangerous import URLSafeTimedSerializer
import os, random, string

app = Flask(__name__)
secret=app.config['SECRET_KEY'] = 'jadhdndmladineonddnkenkenknlsklsnlxleiiooosoomnchiuei'
URL = 'postgresql://zchwcojfbphbxd:85f7fd4795fe96ea00fe2ee046e5b383aa4d2a4146a81c49e3dd073463bb306d@ec2-34-231-42-166.compute-1.amazonaws.com:5432/d3sa35mr80olmb'
app.config['SQLALCHEMY_DATABASE_URI'] = URL
db = SQLAlchemy(app)

s = URLSafeTimedSerializer(secret)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String,unique=True)
    password = db.Column(db.String)
    websites = db.relationship('Vault')

class Vault(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    website = db.Column(db.String)
    user = db.Column(db.String)
    password = db.Column(db.String)
    owner = db.Column(db.Integer,db.ForeignKey('user.id'))


db.create_all()

def randomPassword():
    length = 13
    chars = string.ascii_letters + string.digits + '!@#$%^&*()'
    random.seed = (os.urandom(1024))
    return ''.join(random.choice(chars) for i in range(length))
def buildPasswordList(accounts,user):
    m = ''
    for acc in accounts:
        m += f'Website: {acc.website}, Username: {acc.user}, Password: {acc.password}\n'
    message = Message()
    message.newMessage['To'] = user.email
    message.newMessage['Subject'] = 'Password Vault'
    message.newMessage.set_content(m)
    SendEmail = Email()
    SendEmail.sendEmail(message)

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        session.pop('user')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user or check_password_hash(user.password,form.password.data) == False:
            return render_template('login.html', form=form, message='Wrong Credentials. Please Try Again.')
        else:
            session['user'] = user.id
            # return render_template('login.html',message='Successful Login!')
            return redirect(url_for('passwords'))
    return render_template('login.html', form=form)



@app.route('/signup', methods=['POST', 'GET'])
def signup():
    form = SignUp()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            return render_template('signup.html',form=form,message="Account already exist!")
        else:
            newUser=User(email=form.email.data,password=generate_password_hash(form.password.data))
            db.session.add(newUser)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
            finally:
                db.session.close()
            user = User.query.filter_by(email = form.email.data).first()
            session['user'] = user.id
            #return render_template('signup.html', message="Successful Signup!")
            return redirect(url_for('passwords'))
    return render_template('signup.html',form=form)

@app.route("/logout")
def logout():
    if 'user' in session:
        session.pop('user')
    return redirect(url_for('login'))

@app.route("/passwords", methods=['POST', 'GET'])
def passwords():
    if 'user' in session:
        user = User.query.filter_by(id=session['user']).first()
        if user:
            accounts = Vault.query.filter_by(owner=user.id)
            return render_template('passwords.html',user=user,accounts=accounts)
    return redirect(url_for('login'))

@app.route("/input", methods=['POST', 'GET'])
def input():
    if 'user' in session:
        form = Saver()
        if form.validate_on_submit():
            if form.password.data=='':
                form.password.data = randomPassword()
            data = Vault(website = form.website.data, user = form.username.data,password = form.password.data,owner =session['user'])
            db.session.add(data)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
            finally:
                db.session.close()
            return redirect(url_for('passwords'))
        return render_template('input.html',form = form)
    return redirect(url_for('login'))

@app.route('/delete/<int:id>')
def delete(id):
    account_to_delete = Vault.query.get(id)
    db.session.delete(account_to_delete)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('passwords'))
@app.route('/update/<string:id>', methods = ['POST', 'GET'])
def update(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    account_to_update = Vault.query.get(id)
    print(account_to_update.owner)
    print(session['user'])
    if account_to_update.owner!=session['user']:
        return redirect(url_for('passwords'))
    form = Update()
    if form.validate_on_submit():
        account_to_update.website = form.website.data
        account_to_update.user = form.username.data
        account_to_update.password = form.password.data
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
        finally:
            db.session.close()
        return redirect(url_for('passwords'))
    return render_template('update.html',form = form , account = account_to_update,id=id )

@app.route('/forgotpassword', methods = ['POST', 'GET'])
def forgot():
    form = Forgot()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = s.dumps(user.id, salt='reset')
            message = Message()
            message.newMessage['To'] = user.email
            message.newMessage['Subject'] = 'Password Reset Link'
            message.newMessage.set_content(f"https://supersecretpasswordvault.herokuapp.com/reset/{token}")
            SendEmail = Email()
            SendEmail.sendEmail(message)
            return render_template('forgot.html',message="Link sent to email!")
        return render_template('forgot.html',form=form, message="This account does not exist.")
    return render_template('forgot.html', form=form)

@app.route('/reset/<string:token>', methods = ['POST', 'GET'])
def reset(token):
    id = s.loads(token,salt='reset',max_age=600)
    form = UpdatePassword()
    user = User.query.filter_by(id=id).first()
    if form.validate_on_submit():
        if user:
            user.password=generate_password_hash(form.password.data)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
            finally:
                db.session.close()
            return redirect(url_for('login'))
    return render_template('reset.html', form=form ,token = token,user=user)

@app.route('/export/', methods = ['POST', 'GET'])
def export():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(id=session['user']).first()
    if user:
        accounts = Vault.query.filter_by(owner=user.id)
        if accounts:
            buildPasswordList(accounts,user)
            return render_template('export.html',message = "Passwords have been sent to email.")
        return render_template('export.html', message="No Accounts.")
    return redirect(url_for('login'))





if __name__ == "__main__":
    app.run()