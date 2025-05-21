# Système de Traçabilité Agricole du Maroc

## Réalisateurs
- Ouchchen Omar (Numéro 29)
- Tahri Mohamed (Numéro 37)

## Description Détaillée
Ce projet est une application web complète de traçabilité agricole développée pour le Maroc. Il permet de suivre, gérer et analyser l'ensemble de la chaîne de production agricole, depuis le producteur jusqu'au consommateur final. L'application intègre un système de sécurité blockchain pour garantir l'authenticité et l'intégrité des données.

## Fonctionnalités Principales

### 1. Tableau de Bord Interactif
- Visualisation en temps réel des statistiques agricoles
- Indicateurs clés de performance (KPI)
- Graphiques évolutifs des productions
- Cartographie des régions agricoles

### 2. Gestion des Producteurs
- Enregistrement détaillé des producteurs
- Suivi des informations personnelles et professionnelles
- Historique des productions
- Système de notation et d'évaluation

### 3. Suivi des Produits Agricoles
- Enregistrement des produits avec leurs caractéristiques
- Classification par catégories et types
- Suivi de la qualité et des certifications
- Distinction entre produits biologiques et conventionnels

### 4. Système de Sécurité Blockchain
- Protection des données contre la falsification
- Traçabilité complète des transactions
- Génération de QR codes pour l'authentification
- Historique immuable des modifications

### 5. Filtrage et Recherche
- Filtrage par région géographique
- Recherche par type de produit
- Filtres par période de production
- Recherche avancée multi-critères

### 6. Statistiques et Analyses
- Rapports détaillés de production
- Analyses de tendances
- Statistiques régionales
- Indicateurs de performance

## Technologies Utilisées

### Backend
- Python 3.x
- Dash/Plotly pour les visualisations
- SQLAlchemy pour la gestion de base de données
- Flask pour le serveur web
- Système blockchain personnalisé

### Frontend
- Bootstrap pour l'interface utilisateur
- Dash pour les composants interactifs
- CSS personnalisé
- JavaScript pour les interactions

### Base de Données
- SQLAlchemy ORM
- Système de cache pour les performances
- Migrations de base de données

## Installation Détaillée

1. Prérequis
```bash
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Git
```

2. Cloner le Repository
```bash
git clone [URL_DU_REPO]
cd produit-agricol
```

3. Créer un Environnement Virtuel
```bash
python -m venv venv
# Pour Windows
venv\Scripts\activate
# Pour Linux/Mac
source venv/bin/activate
```

4. Installer les Dépendances
```bash
pip install -r requirements.txt
```

5. Configuration de la Base de Données
```bash
python init_db.py
```

6. Configuration de l'Environnement
Créez un fichier `config.py` avec les paramètres suivants:
```python
class Config:
    SQLALCHEMY_DATABASE_URI = 'votre_uri_base_de_donnees'
    SECRET_KEY = 'votre_cle_secrete'
    DEBUG = True
    PORT = 8050
    HOST = 'localhost'
```

7. Lancer l'Application
```bash
python backend/dashboard.py
```

## Sécurité

### Authentification
- Système de connexion sécurisé
- Gestion des rôles utilisateurs
- Protection contre les attaques CSRF
- Sessions sécurisées

### Protection des Données
- Chiffrement des données sensibles
- Validation des entrées utilisateur
- Protection contre les injections SQL
- Sauvegarde régulière des données

### Blockchain
- Vérification de l'intégrité des données
- Horodatage des transactions
- Traçabilité complète
- Protection contre la falsification

## Structure du Projet
```
produit-agricol/
├── backend/
│   ├── app/
│   │   ├── models/          # Modèles de données
│   │   ├── routes/          # Routes de l'API
│   │   ├── services/        # Services métier
│   │   └── utils/           # Utilitaires
│   ├── dashboard.py         # Application principale
│   ├── auth.py             # Authentification
│   ├── config.py           # Configuration
│   ├── tests.py            # Tests unitaires
│   └── requirements.txt    # Dépendances
├── tracabilite_agricole_maroc/
│   ├── static/             # Fichiers statiques
│   └── templates/          # Templates HTML
└── README.md
```

## Contribution
Pour contribuer au projet, veuillez suivre ces étapes:

1. Fork du projet
2. Création d'une branche pour votre fonctionnalité
3. Développement de votre fonctionnalité
4. Tests unitaires
5. Documentation
6. Pull Request

## Support et Contact
Pour toute question ou suggestion:
- Ouvrir une issue sur GitHub
- Contacter les développeurs:
  - Ouchchen Omar (omar.ouchchen@email.com)
  - Tahri Mohamed (mohamed.tahri@email.com)

## Licence
Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails. 