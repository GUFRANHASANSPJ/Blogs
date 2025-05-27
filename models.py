from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id',name='fk_user_id'), nullable=True)
    image = db.Column(db.String(100))

class User(db.Model,UserMixin):
    id= db.Column(db.Integer,primary_key=True)
    username= db.Column(db.String(50),unique=True,nullable=False)
    password= db.Column(db.String(50),nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True, default= '')  # New
    phone = db.Column(db.String(15), unique=True, nullable=True,default= '')    # New
    image = db.Column(db.String(100), nullable=True,default='default.jpg') 
    blogs = db.relationship('Blog', backref='author', lazy=True)