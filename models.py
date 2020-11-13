from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify
from flask_login import LoginManager, login_required, login_user, logout_user, current_user, UserMixin
from datetime import datetime
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://azeez:azeez007@localhost/bot'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://dataslid:azeez007@dataslid.mysql.pythonanywhere-services.com/dataslid$betbot'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['SECRET_KEY'] = "d27e0926-13d9-11eb-900d-18f46ae7891e"
app.config['TOKEN_EXPIRY_TIME'] = "10"


db = SQLAlchemy(app)

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

class User(db.Model, UserMixin ):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30))
    is_admin = db.Column(db.Boolean, default=False)
    phone = db.Column(db.String(15))
    email = db.Column(db.String(200))
    password = db.Column(db.String(150))

class Bet_49ja(db.Model):
    __tablename__ = "bet_49ja"
    id = db.Column(db.Integer, primary_key=True)
    user  = db.relationship(User, backref=db.backref('bet_49ja', uselist=False), lazy=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(User.id))
    is_updated = db.Column(db.Boolean, default=False)
    has_compiled = db.Column(db.Boolean, default=False)
    is_demo  = db.Column(db.Boolean, default=True)
    is_paid_bot = db.Column(db.Boolean, default=False)
    bot_type = db.Column(db.String(200), default="demo")
    bot_path = db.Column(db.String(200))
    is_subscribe = db.Column(db.Boolean, default=False)
    sub_exp_date = db.Column(db.String(500), default="0")

class Make_request(db.Model):
    __tablename__ = "make_request"
    id = db.Column(db.Integer, primary_key=True)
    user  = db.relationship(User, backref='make_request', lazy=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(User.id))
    request = db.Column(db.Text)
    not_seen = db.Column(db.Boolean, default=True)
    datetime = db.Column(db.DateTime, default=datetime.now())

class Testimonial(db.Model):
    __tablename__ = "testimonial"
    id = db.Column(db.Integer, primary_key=True)
    user  = db.relationship(User, backref='testimonial', lazy=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(User.id))
    testimony = db.Column(db.Text)
    datetime = db.Column(db.DateTime, default=datetime.now())

class Reset_password(db.Model):
    __tablename__ = 'reset_password'
    id = db.Column(db.Integer, primary_key=True)
    user  = db.relationship(User, backref='reset_password', lazy=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(User.id))
    mail = db.Column(db.String(100))
    dateTime = db.Column(db.String(500), default=0)
    token = db.Column(db.String(150))
    
class Confirm_mail(db.Model):
    __tablename__ = 'confirm_mail'
    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String(100))
    user_details = db.Column(db.String(500))
    dateTime = db.Column(db.Integer)
    dateTime = db.Column(db.String(500), default=0)
    token = db.Column(db.String(150))

class Buy_pin(db.Model):
    __tablename__ = 'buy_pin'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(150))
    datetime = db.Column(db.DateTime, default=datetime.now())
    
class Subcribe_pin(db.Model):
    __tablename__ = 'subscribe_pin'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(150))
    datetime = db.Column(db.DateTime, default=datetime.now())
    

class Financial_data(db.Model):
    __tablename__ = 'financial_data'
    id = db.Column(db.Integer, primary_key=True)
    user  = db.relationship(User, backref='financial_data', lazy=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(User.id))
    datetime = db.Column(db.DateTime, default=datetime.now())
    price = db.Column(db.String(15))
    bot_type = db.Column(db.String(60))

if __name__ == '__main__':
    manager.run()
