from app.api import bp
from flask import jsonify, request
from app.models import db, Producteur, Produit, Etape
from app.blockchain import get_contract, get_web3
import pandas as pd
from datetime import datetime
from sqlalchemy import func
import os
import matplotlib
matplotlib.use('Agg')  # Pour générer des graphiques sans interface graphique
import matplotlib.pyplot as plt
import seaborn as sns

# Route pour synchroniser les données de la blockchain
@bp.route('/sync', methods=['GET'])
def sync_blockchain():
    try:
        contract = get_contract()
        web3 = get_web3()
        
        # Synchroniser les producteurs
        producteur_filter = contract.events.ProducteurAjoute.createFilter(fromBlock=0)
        producteur_events = producteur_filter.get_all_entries()
        
        for event in producteur_events:
            args = event['args']
            producteur = Producteur.query.get(args['id'])
            if not producteur:
                producteur = Producteur(
                    id=args['id'],
                    nom=args['nom'],
                    region=args['region'],
                    date_ajout=datetime.now()
                )
                db.session.add(producteur)
        
        # Synchroniser les produits
        produit_filter = contract.events.ProduitEnregistre.createFilter(fromBlock=0)
        produit_events = produit_filter.get_all_entries()
        
        for event in produit_events:
            args = event['args']
            produit = Produit.query.get(args['id'])
            if not produit:
                # Récupérer les détails du produit depuis le contrat
                produit_details = contract.functions.obtenirProduit(args['id']).call()
                
                produit = Produit(
                    id=args['id'],
                    nom=args['nom'],
                    producteur_id=args['idProducteur'],
                    region=produit_details[3],  # Indice de région dans le retour de la fonction
                    date_recolte=datetime.fromtimestamp(produit_details[4]),  # Timestamp Unix
                    est_bio=produit_details[5]  # Est biologique
                )
                db.session.add(produit)
        
        # Synchroniser les étapes
        etape_filter = contract.events.EtapeAjoutee.createFilter(fromBlock=0)
        etape_events = etape_filter.get_all_entries()
        
        for event in etape_events:
            args = event['args']
            # Vous devrez récupérer les détails de l'étape depuis le contrat
            produit_id = args['idProduit']
            etapes_count = contract.functions.nombreEtapes(produit_id).call()
            
            # Récupérer toutes les étapes du produit
            for i in range(etapes_count):
                etape_details = contract.functions.obtenirEtape(produit_id, i).call()
                
                # Vérifier si cette étape existe déjà
                existing_etape = Etape.query.filter_by(
                    produit_id=produit_id, 
                    operation=etape_details[1],
                    operateur=etape_details[2],
                    lieu=etape_details[3]
                ).first()
                
                if not existing_etape:
                    etape = Etape(
                        produit_id=produit_id,
                        date=datetime.fromtimestamp(etape_details[0]),
                        operation=etape_details[1],
                        operateur=etape_details[2],
                        lieu=etape_details[3],
                        # Données supplémentaires (fictives pour l'exemple)
                        temperature=25.0,
                        humidite=60.0
                    )
                    db.session.add(etape)
        
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Données synchronisées avec succès'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Route pour obtenir des statistiques par région
@bp.route('/stats/regions', methods=['GET'])
def stats_regions():
    try:
        # Compter les produits par région
        query = db.session.query(
            Produit.region, 
            func.count(Produit.id).label('count')
        ).group_by(Produit.region).all()
        
        data = [{'region': r, 'count': c} for r, c in query]
        
        # Créer une visualisation
        df = pd.DataFrame(data)
        
        plt.figure(figsize=(10, 6))
        sns.barplot(x='region', y='count', data=df)
        plt.title('Nombre de produits par région')
        plt.xticks(rotation=45)
        
        # Sauvegarder le graphique
        static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../static')
        os.makedirs(static_dir, exist_ok=True)
        plt.savefig(os.path.join(static_dir, 'regions.png'), bbox_inches='tight')
        plt.close()
        
        return jsonify({
            'data': data,
            'image_url': '/static/regions.png'
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Route pour analyser la qualité des produits
@bp.route('/analyse/qualite', methods=['GET'])
def analyse_qualite():
    try:
        # Récupérer les produits et leurs étapes
        produits = Produit.query.all()
        resultats = []
        
        for produit in produits:
            etapes = Etape.query.filter_by(produit_id=produit.id).all()
            
            if etapes:
                # Calculer un score de qualité fictif basé sur les données
                # Dans un cas réel, vous utiliseriez un modèle ML
                temperatures = [e.temperature for e in etapes if e.temperature is not None]
                humidites = [e.humidite for e in etapes if e.humidite is not None]
                
                if temperatures and humidites:
                    avg_temp = sum(temperatures) / len(temperatures)
                    avg_hum = sum(humidites) / len(humidites)
                    
                    # Formule fictive pour calculer la qualité
                    qualite = 100 - abs(25 - avg_temp) - abs(60 - avg_hum) / 2
                    qualite = max(0, min(100, qualite))
                    
                    # Mettre à jour le score de qualité dans la base de données
                    produit.qualite_score = qualite
                    
                    resultats.append({
                        'produit_id': produit.id,
                        'nom': produit.nom,
                        'region': produit.region,
                        'qualite': qualite
                    })
        
        db.session.commit()
        
        # Créer une visualisation des scores de qualité
        if resultats:
            df = pd.DataFrame(resultats)
            
            plt.figure(figsize=(12, 6))
            ax = sns.boxplot(x='region', y='qualite', data=df)
            plt.title('Distribution des scores de qualité par région')
            plt.xticks(rotation=45)
            
            # Sauvegarder le graphique
            static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../static')
            os.makedirs(static_dir, exist_ok=True)
            plt.savefig(os.path.join(static_dir, 'qualite.png'), bbox_inches='tight')
            plt.close()
            
            return jsonify({
                'data': resultats,
                'image_url': '/static/qualite.png'
            })
        else:
            return jsonify({'message': 'Pas de données suffisantes pour l\'analyse'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500