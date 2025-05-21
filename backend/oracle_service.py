import time
import schedule
import json
import requests
from web3 import Web3
import psycopg2
from datetime import datetime
import random

# Configuration
WEB3_PROVIDER = 'http://localhost:7545'
CONTRACT_ADDRESS = '0x480608b80112000Fd2854EfDb37Bd2e4CbE29F92'  # Remplacez par l'adresse de votre contrat

# Connexion à la base de données
DB_PARAMS = {
    'dbname': 'tracabilite_agricole',
    'user': 'root',
    'password': '12345',
    'host': 'localhost'
}

# Charger l'ABI du contrat
def load_contract_abi():
    try:
        with open('../build/contracts/TracabiliteAgricoleMaroc.json', 'r') as f:
            contract_json = json.load(f)
        return contract_json['abi']
    except Exception as e:
        print(f"Erreur lors du chargement de l'ABI: {e}")
        return None

# Initialiser Web3 et le contrat
def init_contract():
    try:
        web3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER))
        contract_abi = load_contract_abi()
        if not contract_abi:
            return None, None
            
        contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)
        return web3, contract
    except Exception as e:
        print(f"Erreur lors de l'initialisation du contrat: {e}")
        return None, None

# Synchroniser les événements de la blockchain
def synchroniser_blockchain():
    print("Synchronisation de la blockchain...")
    web3, contract = init_contract()
    if not web3 or not contract:
        print("Impossible d'initialiser la connexion à la blockchain")
        return
    
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        # Synchroniser les producteurs
        producteur_filter = contract.events.ProducteurAjoute.createFilter(fromBlock=0)
        for event in producteur_filter.get_all_entries():
            args = event['args']
            
            # Vérifier si le producteur existe déjà
            cur.execute("SELECT id FROM producteur WHERE id = %s", (args['id'],))
            if not cur.fetchone():
                # Ajouter le producteur à la base de données
                cur.execute(
                    "INSERT INTO producteur (id, nom, region, est_verifie, date_ajout) VALUES (%s, %s, %s, %s, %s)",
                    (args['id'], args['nom'], args['region'], False, datetime.now())
                )
        
        # Synchroniser les produits
        produit_filter = contract.events.ProduitEnregistre.createFilter(fromBlock=0)
        for event in produit_filter.get_all_entries():
            args = event['args']
            
            # Vérifier si le produit existe déjà
            cur.execute("SELECT id FROM produit WHERE id = %s", (args['id'],))
            if not cur.fetchone():
                # Récupérer les détails du produit depuis le contrat
                produit_details = contract.functions.obtenirProduit(args['id']).call()
                
                # Ajouter le produit à la base de données
                cur.execute(
                    """INSERT INTO produit 
                       (id, nom, producteur_id, region, date_recolte, est_bio, qualite_score, prix_marche) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                    (
                        args['id'], 
                        args['nom'], 
                        args['idProducteur'], 
                        produit_details[3],  # région
                        datetime.fromtimestamp(produit_details[4]),  # date_recolte
                        produit_details[5],  # est_bio
                        random.uniform(60, 95),  # qualité fictive
                        random.uniform(10, 100)  # prix fictif
                    )
                )
        
        # Synchroniser les étapes
        etape_filter = contract.events.EtapeAjoutee.createFilter(fromBlock=0)
        for event in etape_filter.get_all_entries():
            args = event['args']
            produit_id = args['idProduit']
            
            # Récupérer le nombre d'étapes pour ce produit
            etapes_count = contract.functions.nombreEtapes(produit_id).call()
            
            # Récupérer toutes les étapes du produit
            for i in range(etapes_count):
                etape_details = contract.functions.obtenirEtape(produit_id, i).call()
                
                # Vérifier si cette étape existe déjà
                cur.execute(
                    """SELECT id FROM etape 
                       WHERE produit_id = %s AND operation = %s AND operateur = %s AND lieu = %s AND 
                             date = %s""",
                    (
                        produit_id, 
                        etape_details[1],  # operation
                        etape_details[2],  # operateur
                        etape_details[3],  # lieu
                        datetime.fromtimestamp(etape_details[0])  # date
                    )
                )
                
                if not cur.fetchone():
                    # Ajouter l'étape à la base de données
                    cur.execute(
                        """INSERT INTO etape 
                           (produit_id, date, operation, operateur, lieu, temperature, humidite) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                        (
                            produit_id,
                            datetime.fromtimestamp(etape_details[0]),  # date
                            etape_details[1],  # operation
                            etape_details[2],  # operateur
                            etape_details[3],  # lieu
                            random.uniform(20, 30),  # température fictive
                            random.uniform(40, 80)  # humidité fictive
                        )
                    )
        
        conn.commit()
        print("Synchronisation terminée avec succès")
    
    except Exception as e:
        print(f"Erreur lors de la synchronisation: {e}")
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# Mettre à jour les prix de marché (simulation)
def mettre_a_jour_prix_marche():
    print("Mise à jour des prix de marché...")
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        # Récupérer tous les produits
        cur.execute("SELECT id, nom FROM produit")
        produits = cur.fetchall()
        
        for produit_id, produit_nom in produits:
            # Simuler une fluctuation de prix
            nouveau_prix = random.uniform(10, 100)
            
            # Mettre à jour le prix dans la base de données
            cur.execute(
                "UPDATE produit SET prix_marche = %s WHERE id = %s",
                (nouveau_prix, produit_id)
            )
        
        conn.commit()
        print("Prix de marché mis à jour avec succès")
    
    except Exception as e:
        print(f"Erreur lors de la mise à jour des prix: {e}")
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# Programme principal
def main():
    print("Démarrage du service d'oracle et d'indexation...")
    
    # Exécuter la synchronisation immédiatement au démarrage
    synchroniser_blockchain()
    mettre_a_jour_prix_marche()
    
    # Planifier les tâches récurrentes
    schedule.every(5).minutes.do(synchroniser_blockchain)
    schedule.every(1).hour.do(mettre_a_jour_prix_marche)
    
    # Boucle principale
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()