from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session, redirect, url_for, flash
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import Config

# Initialisation de la base de données
Base = declarative_base()
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)

# Modèle utilisateur
class User(UserMixin, Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128))
    is_admin = Column(Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Initialisation de Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'

@login_manager.user_loader
def load_user(user_id):
    db_session = Session()
    user = db_session.query(User).get(int(user_id))
    db_session.close()
    return user

def init_auth(app):
    login_manager.init_app(app)
    Base.metadata.create_all(engine)

def login(username, password):
    db_session = Session()
    user = db_session.query(User).filter_by(username=username).first()
    db_session.close()
    
    if user and user.check_password(password):
        login_user(user)
        return True
    return False

def logout():
    logout_user()

def register(username, email, password, is_admin=False):
    db_session = Session()
    try:
        user = User(username=username, email=email, is_admin=is_admin)
        user.set_password(password)
        db_session.add(user)
        db_session.commit()
        return True
    except Exception as e:
        db_session.rollback()
        return False
    finally:
        db_session.close()

def is_admin():
    return session.get('is_admin', False) 