// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title TracabiliteAgricoleMaroc
 * @dev Système simplifié de traçabilité des produits agricoles marocains
 */
contract TracabiliteAgricoleMaroc {
    
    // Structure pour les producteurs
    struct Producteur {
        string id;              // CIN ou numéro d'identification
        string nom;             // Nom du producteur
        string region;          // Région d'origine
        bool estVerifie;        // Vérification officielle
    }
    
    // Structure pour les produits agricoles
    struct Produit {
        string id;              // Identifiant unique du produit (code-barres, QR code)
        string nom;             // Nom du produit (ex: Huile d'argan, Safran)
        string idProducteur;    // ID du producteur
        string region;          // Région de production
        uint dateRecolte;       // Date de récolte (timestamp)
        bool estBio;            // Si le produit est biologique
    }
    
    // Structure pour les étapes de la chaîne d'approvisionnement
    struct Etape {
        uint date;              // Date de l'opération
        string operation;       // Type d'opération (Récolte, Transformation, etc.)
        string operateur;       // Qui a effectué l'opération
        string lieu;            // Lieu de l'opération
    }
    
    // Mappages pour stocker les données
    mapping(string => Producteur) public producteurs;
    mapping(string => Produit) public produits;
    mapping(string => Etape[]) public etapesProduit;
    
    // Adresse du propriétaire du contrat
    address public proprietaire;
    
    // Événements pour surveiller les actions importantes
    event ProducteurAjoute(string id, string nom, string region);
    event ProduitEnregistre(string id, string nom, string idProducteur);
    event EtapeAjoutee(string idProduit, string operation);
    
    // Modificateur pour limiter certaines fonctions au propriétaire
    modifier seulementProprietaire() {
        require(msg.sender == proprietaire, "Seul le proprietaire peut executer cette fonction");
        _;
    }
    
    // Constructeur
    constructor() {
        proprietaire = msg.sender;
    }
    
    /**
     * @dev Ajoute un nouveau producteur au système
     * @param _id Identifiant du producteur
     * @param _nom Nom du producteur
     * @param _region Région d'origine
     */
    function ajouterProducteur(string memory _id, string memory _nom, string memory _region) public {
        // Vérifier que le producteur n'existe pas déjà
        require(bytes(producteurs[_id].id).length == 0, "Ce producteur existe deja");
        
        // Créer et stocker le nouveau producteur
        producteurs[_id] = Producteur({
            id: _id,
            nom: _nom,
            region: _region,
            estVerifie: false
        });
        
        emit ProducteurAjoute(_id, _nom, _region);
    }
    
    /**
     * @dev Vérifie un producteur (réservé au propriétaire)
     * @param _id Identifiant du producteur
     */
    function verifierProducteur(string memory _id) public seulementProprietaire {
        // Vérifier que le producteur existe
        require(bytes(producteurs[_id].id).length > 0, "Producteur inexistant");
        
        // Marquer le producteur comme vérifié
        producteurs[_id].estVerifie = true;
    }
    
    /**
     * @dev Enregistre un nouveau produit
     * @param _id Identifiant du produit
     * @param _nom Nom du produit
     * @param _idProducteur ID du producteur
     * @param _region Région de production
     * @param _estBio Si le produit est biologique
     */
    function enregistrerProduit(
        string memory _id, 
        string memory _nom, 
        string memory _idProducteur, 
        string memory _region, 
        bool _estBio
    ) public {
        // Vérifier que le producteur existe et est vérifié
        require(bytes(producteurs[_idProducteur].id).length > 0, "Producteur inexistant");
        require(producteurs[_idProducteur].estVerifie, "Producteur non verifie");
        
        // Vérifier que le produit n'existe pas déjà
        require(bytes(produits[_id].id).length == 0, "Ce produit existe deja");
        
        // Créer et stocker le nouveau produit
        produits[_id] = Produit({
            id: _id,
            nom: _nom,
            idProducteur: _idProducteur,
            region: _region,
            dateRecolte: block.timestamp,
            estBio: _estBio
        });
        
        // Ajouter automatiquement l'étape de récolte
        Etape memory premiereEtape = Etape({
            date: block.timestamp,
            operation: "Recolte",
            operateur: _idProducteur,
            lieu: _region
        });
        
        etapesProduit[_id].push(premiereEtape);
        
        emit ProduitEnregistre(_id, _nom, _idProducteur);
    }
    
    /**
     * @dev Ajoute une étape dans la chaîne d'approvisionnement d'un produit
     * @param _idProduit Identifiant du produit
     * @param _operation Type d'opération
     * @param _operateur Qui a effectué l'opération
     * @param _lieu Lieu de l'opération
     */
    function ajouterEtape(
        string memory _idProduit, 
        string memory _operation, 
        string memory _operateur, 
        string memory _lieu
    ) public {
        // Vérifier que le produit existe
        require(bytes(produits[_idProduit].id).length > 0, "Produit inexistant");
        
        // Créer et stocker la nouvelle étape
        Etape memory nouvelleEtape = Etape({
            date: block.timestamp,
            operation: _operation,
            operateur: _operateur,
            lieu: _lieu
        });
        
        etapesProduit[_idProduit].push(nouvelleEtape);
        
        emit EtapeAjoutee(_idProduit, _operation);
    }
    
    /**
     * @dev Récupère les informations d'un producteur
     * @param _id Identifiant du producteur
     * @return Les détails du producteur
     */
    function obtenirProducteur(string memory _id) public view returns (Producteur memory) {
        require(bytes(producteurs[_id].id).length > 0, "Producteur inexistant");
        return producteurs[_id];
    }
    
    /**
     * @dev Récupère les informations d'un produit
     * @param _id Identifiant du produit
     * @return Les détails du produit
     */
    function obtenirProduit(string memory _id) public view returns (Produit memory) {
        require(bytes(produits[_id].id).length > 0, "Produit inexistant");
        return produits[_id];
    }
    
    /**
     * @dev Récupère le nombre d'étapes pour un produit
     * @param _idProduit Identifiant du produit
     * @return Le nombre d'étapes
     */
    function nombreEtapes(string memory _idProduit) public view returns (uint) {
        return etapesProduit[_idProduit].length;
    }
    
    /**
     * @dev Récupère une étape spécifique d'un produit
     * @param _idProduit Identifiant du produit
     * @param _index Index de l'étape
     * @return Les détails de l'étape
     */
    function obtenirEtape(string memory _idProduit, uint _index) public view returns (Etape memory) {
        require(_index < etapesProduit[_idProduit].length, "Etape inexistante");
        return etapesProduit[_idProduit][_index];
    }
    
    /**
     * @dev Vérifie si un produit est authentique et retrace son parcours
     * @param _idProduit Identifiant du produit
     * @return estAuthentique Authentification du produit
     * @return producteur Informations sur le producteur
     * @return nombreEtapesTotal Nombre total d'étapes enregistrées
     */
    function verifierAuthenticiteProduit(string memory _idProduit) public view 
    returns (bool estAuthentique, Producteur memory producteur, uint nombreEtapesTotal) {
        // Vérifier que le produit existe
        if (bytes(produits[_idProduit].id).length == 0) {
            return (false, Producteur("", "", "", false), 0);
        }
        
        // Récupérer les informations du producteur
        string memory idProducteur = produits[_idProduit].idProducteur;
        Producteur memory producteurInfo = producteurs[idProducteur];
        
        // Vérifier si le producteur est vérifié
        if (!producteurInfo.estVerifie) {
            return (false, producteurInfo, etapesProduit[_idProduit].length);
        }
        
        return (true, producteurInfo, etapesProduit[_idProduit].length);
    }
}