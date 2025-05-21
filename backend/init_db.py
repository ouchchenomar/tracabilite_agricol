from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from config import Config
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation de la base de données
Base = declarative_base()
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)

# Modèles
class Producteur(Base):
    __tablename__ = 'producteur'
    
    id = Column(Integer, primary_key=True)
    nom = Column(String(100), nullable=False)
    region = Column(String(100), nullable=False)
    adresse = Column(String(200))
    telephone = Column(String(20))
    email = Column(String(100))
    data_hash = Column(String(64), unique=True)  # Hash de la blockchain
    
    produits = relationship("Produit", back_populates="producteur")

class Produit(Base):
    __tablename__ = 'produit'
    
    id = Column(Integer, primary_key=True)
    nom = Column(String(100), nullable=False)
    region = Column(String(100), nullable=False)
    qualite_score = Column(Float)
    est_bio = Column(Boolean, default=False)
    producteur_id = Column(Integer, ForeignKey('producteur.id'))
    data_hash = Column(String(64), unique=True)  # Hash de la blockchain
    
    producteur = relationship("Producteur", back_populates="produits")

def init_db():
    try:
        # Création des tables
        Base.metadata.create_all(engine)
        logger.info("Tables créées avec succès")
        
        # Création d'une session
        session = Session()
        
        # Données de test pour les producteurs
        producteurs = [
            Producteur(
                nom="Ferme Atlas",
                region="Marrakech-Safi",
                adresse="Route de l'Atlas, Marrakech",
                telephone="+212 524-123456",
                email="contact@ferme-atlas.ma"
            ),
            Producteur(
                nom="Coopérative Souss",
                region="Souss-Massa",
                adresse="Agadir, Souss",
                telephone="+212 528-789012",
                email="info@coop-souss.ma"
            ),
            Producteur(
                nom="Domaine Rif",
                region="Tanger-Tétouan-Al Hoceima",
                adresse="Tétouan, Rif",
                telephone="+212 539-345678",
                email="contact@domaine-rif.ma"
            )
        ]
        
        # Ajout des producteurs
        for p in producteurs:
            session.add(p)
        session.commit()
        logger.info("Producteurs ajoutés avec succès")
        
        # Données de test pour les produits
        produits = [
            Produit(
                nom="Olives",
                region="Marrakech-Safi",
                qualite_score=8.5,
                est_bio=True,
                producteur_id=1
            ),
            Produit(
                nom="Agrumes",
                region="Souss-Massa",
                qualite_score=9.0,
                est_bio=False,
                producteur_id=2
            ),
            Produit(
                nom="Raisins",
                region="Tanger-Tétouan-Al Hoceima",
                qualite_score=7.8,
                est_bio=True,
                producteur_id=3
            ),
            Produit(
                nom="Dattes",
                region="Drâa-Tafilalet",
                qualite_score=9.2,
                est_bio=True,
                producteur_id=1
            ),
            Produit(
                nom="Amandes",
                region="Fès-Meknès",
                qualite_score=8.7,
                est_bio=False,
                producteur_id=2
            )
        ]
        
        # Ajout des produits
        for p in produits:
            session.add(p)
        session.commit()
        logger.info("Produits ajoutés avec succès")
        
        session.close()
        logger.info("Base de données initialisée avec succès")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {str(e)}")
        raise

if __name__ == '__main__':
    init_db() 