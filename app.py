from flask import Flask,render_template,session, redirect, url_for
from forms import LoginForm,SignUp,Saver,Update,Forgot
from flask_sqlalchemy import SQLAlchemy
from emailer import Email,Message
import os, random, string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dfewfew123213rwdsgert34tgfd1234trgf'
URL = 'postgresql://izefqraayqbwjn:445239457459d91c6b305a815d5a71d923e64798768cfc00421f6d928c41e465@ec2-44-207-253-50.compute-1.amazonaws.com:5432/d5u4f0l2vtgjhm'
app.config['SQLALCHEMY_DATABASE_URI'] = URL
db = SQLAlchemy(app)

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
        user = User.query.filter_by(email=form.email.data, password=form.password.data).first()
        if user is None:
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
            newUser=User(email=form.email.data,password=form.password.data)
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

@app.route('/update/<int:id>', methods = ['POST', 'GET'])
def update(id):
    account_to_update = Vault.query.get(id)
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

    return render_template('update.html',form = form , account = account_to_update )

@app.route('/forgotpassword', methods = ['POST', 'GET'])
def forgot():
    form = Forgot()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            message = Message()
            message.newMessage['To'] = user.email
            message.newMessage['Subject'] = 'Password'
            message.newMessage.set_content(f"Password: {user.password}")
            SendEmail = Email()
            SendEmail.sendEmail(message)
            return render_template('forgot.html',message="Password Sent to Email!")
        return render_template('forgot.html',form=form, message="This account does not exist.")
    return render_template('forgot.html', form=form)


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