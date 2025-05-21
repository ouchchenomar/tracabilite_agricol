import unittest
from flask import Flask
from dashboard import app
from auth import User, login, register, logout
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class TestDashboard(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config.from_object(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Créer les tables de test
        engine = create_engine(TestConfig.SQLALCHEMY_DATABASE_URI)
        Session = sessionmaker(bind=engine)
        self.session = Session()
        
    def tearDown(self):
        self.session.close()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_region_graph(self):
        response = self.client.get('/_dash-update-component', json={
            'output': 'region-graph',
            'inputs': [
                {'id': 'region-dropdown', 'value': 'all'},
                {'id': 'product-dropdown', 'value': 'all'}
            ]
        })
        self.assertEqual(response.status_code, 200)

class TestAuth(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.from_object(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Créer les tables de test
        engine = create_engine(TestConfig.SQLALCHEMY_DATABASE_URI)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def tearDown(self):
        self.session.close()
        self.app_context.pop()

    def test_register(self):
        # Test d'inscription réussie
        result = register('testuser', 'test@example.com', 'password123')
        self.assertTrue(result)
        
        # Test d'inscription avec email existant
        result = register('testuser2', 'test@example.com', 'password123')
        self.assertFalse(result)

    def test_login(self):
        # Créer un utilisateur de test
        register('testuser', 'test@example.com', 'password123')
        
        # Test de connexion réussie
        result = login('testuser', 'password123')
        self.assertTrue(result)
        
        # Test de connexion avec mauvais mot de passe
        result = login('testuser', 'wrongpassword')
        self.assertFalse(result)

    def test_logout(self):
        # Créer et connecter un utilisateur
        register('testuser', 'test@example.com', 'password123')
        login('testuser', 'password123')
        
        # Test de déconnexion
        logout()
        self.assertFalse(is_admin())

if __name__ == '__main__':
    unittest.main() 