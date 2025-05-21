from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
    
db = SQLAlchemy()
class Producteur(db.Model):
        id = db.Column(db.String(64), primary_key=True)
        nom = db.Column(db.String(128), nullable=False)
        region = db.Column(db.String(64), nullable=False)
        est_verifie = db.Column(db.Boolean, default=False)
        date_ajout = db.Column(db.DateTime, default=datetime.utcnow)
        coordonnees_gps = db.Column(db.String(64))
        produits = db.relationship('Produit', backref='producteur_relation', lazy=True)
        
        def to_dict(self):
            return {
                'id': self.id,
                'nom': self.nom,
                'region': self.region,
                'est_verifie': self.est_verifie,
                'date_ajout': self.date_ajout.isoformat() if self.date_ajout else None,
                'coordonnees_gps': self.coordonnees_gps
            }
    
class Produit(db.Model):
        id = db.Column(db.String(64), primary_key=True)
        nom = db.Column(db.String(128), nullable=False)
        producteur_id = db.Column(db.String(64), db.ForeignKey('producteur.id'), nullable=False)
        region = db.Column(db.String(64), nullable=False)
        date_recolte = db.Column(db.DateTime, default=datetime.utcnow)
        est_bio = db.Column(db.Boolean, default=False)
        qualite_score = db.Column(db.Float)
        prix_marche = db.Column(db.Float)
        etapes = db.relationship('Etape', backref='produit_relation', lazy=True)
        
        def to_dict(self):
            return {
                'id': self.id,
                'nom': self.nom,
                'producteur_id': self.producteur_id,
                'region': self.region,
                'date_recolte': self.date_recolte.isoformat() if self.date_recolte else None,
                'est_bio': self.est_bio,
                'qualite_score': self.qualite_score,
                'prix_marche': self.prix_marche
            }
    
class Etape(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        produit_id = db.Column(db.String(64), db.ForeignKey('produit.id'), nullable=False)
        date = db.Column(db.DateTime, default=datetime.utcnow)
        operation = db.Column(db.String(64), nullable=False)
        operateur = db.Column(db.String(128), nullable=False)
        lieu = db.Column(db.String(128), nullable=False)
        temperature = db.Column(db.Float)
        humidite = db.Column(db.Float)
        
        def to_dict(self):
            return {
                'id': self.id,
                'produit_id': self.produit_id,
                'date': self.date.isoformat() if self.date else None,
                'operation': self.operation,
                'operateur': self.operateur,
                'lieu': self.lieu,
                'temperature': self.temperature,
                'humidite': self.humidite
            }
    
