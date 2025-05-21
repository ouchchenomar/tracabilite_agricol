import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from sqlalchemy import create_engine
from flask import Flask, session as flask_session
from config import Config
from functools import lru_cache
import logging
from datetime import datetime
import dash_bootstrap_components as dbc
from sqlalchemy.orm import sessionmaker
from init_db import Base, Producteur, Produit
from blockchain import DataSecurity
import qrcode
import io
import base64
from users import authenticate

REGIONS = [
    {'label': 'Drâa-Tafilalet', 'value': 'Drâa-Tafilalet'},
    {'label': 'Fès-Meknès', 'value': 'Fès-Meknès'},
    {'label': 'Marrakech-Safi', 'value': 'Marrakech-Safi'},
    {'label': 'Souss-Massa', 'value': 'Souss-Massa'},
    {'label': 'Tanger-Tétouan-Al Hoceïma', 'value': 'Tanger-Tétouan-Al Hoceïma'},
    # ... ajoute toutes les régions souhaitées
]

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='dashboard.log'
)
logger = logging.getLogger(__name__)

# Connexion à la base de données avec gestion des erreurs
try:
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    logger.info("Connexion à la base de données établie avec succès")
except Exception as e:
    logger.error(f"Erreur de connexion à la base de données: {str(e)}")
    raise

# Initialiser l'application Flask
server = Flask(__name__)
server.config['SECRET_KEY'] = Config.SECRET_KEY

# Initialiser l'application Dash
app = dash.Dash(
    __name__,
    server=server,
    url_base_pathname='/dashboard/',
    external_stylesheets=[
        dbc.themes.FLATLY,
        'https://use.fontawesome.com/releases/v5.15.4/css/all.css'
    ],
    suppress_callback_exceptions=True
)

# Initialiser la sécurité blockchain
data_security = DataSecurity()

# Créer une session pour la base de données
Session = sessionmaker(bind=engine)

# Cache pour les requêtes fréquentes
@lru_cache(maxsize=128)
def get_cached_data(query, params=None):
    try:
        return pd.read_sql(query, engine, params=params)
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de la requête: {str(e)}")
        return pd.DataFrame()

tabs_layout = dbc.Tabs([
    # Onglet Tableau de bord
    dbc.Tab(label="Tableau de bord", children=[
        # Indicateurs clés pour les autorités
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H5("Producteurs", className="card-title"),
                    html.H2(id="kpi-producteurs", className="card-text")
                ])
            ], color="primary", inverse=True), width=2),
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H5("Produits", className="card-title"),
                    html.H2(id="kpi-produits", className="card-text")
                ])
            ], color="success", inverse=True), width=2),
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H5("Produits Bio", className="card-title"),
                    html.H2(id="kpi-bio", className="card-text")
                ])
            ], color="info", inverse=True), width=2),
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H5("Régions", className="card-title"),
                    html.H2(id="kpi-regions", className="card-text")
                ])
            ], color="warning", inverse=True), width=2),
        ], className="mb-4"),
        # Graphique évolution mensuelle
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-chart-area me-2"),
                        "Nouveaux producteurs par mois"
                    ]),
                    dbc.CardBody([
                        dcc.Graph(id="evolution-producteurs-graph")
                    ])
                ])
            ], width=12)
        ], className="mb-4"),
        dbc.Row([
            # Filtres
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-filter me-2"),
                        "Filtres"
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    dbc.Label("Région:"),
                                    dcc.Dropdown(
                                        id='region-dropdown',
                                        options=[],
                                        value='all',
                                        clearable=False
                                    ),
                                ], className="mb-3"),
                                html.Div([
                                    dbc.Label("Produit:"),
                                    dcc.Dropdown(
                                        id='product-dropdown',
                                        options=[],
                                        value='all',
                                        clearable=False
                                    ),
                                ], className="mb-3"),
                            ], width=3),
                        ]),
                    ])
                ], className="shadow-sm")
            ], width=3),
            # Graphiques
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-map-marked-alt me-2"),
                        "Distribution des produits"
                    ]),
                    dbc.CardBody([
                        dcc.Graph(id='region-graph')
                    ])
                ], className="shadow-sm mb-4"),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.I(className="fas fa-star me-2"),
                                "Qualité des produits"
                            ]),
                            dbc.CardBody([
                                dcc.Graph(id='quality-graph')
                            ])
                        ], className="shadow-sm")
                    ], width=6),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.I(className="fas fa-leaf me-2"),
                                "Produits bio vs conventionnels"
                            ]),
                            dbc.CardBody([
                                dcc.Graph(id='bio-graph')
                            ])
                        ], className="shadow-sm")
                    ], width=6)
                ])
            ], width=9)
        ])
    ]),
    # Onglet Ajouter données
    dbc.Tab(label="Ajouter données", children=[
        dbc.Tabs([
            dbc.Tab(label="Ajouter un producteur", children=[
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    dbc.Label("Nom du producteur:"),
                                    dbc.Input(id="producteur-nom", type="text", placeholder="Entrez le nom"),
                                ], className="mb-3"),
                                html.Div([
                                    dbc.Label("Région:"),
                                    dcc.Dropdown(
                                        id="producteur-region",
                                        options=REGIONS,
                                        placeholder="Sélectionnez la région"
                                    ),
                                ], className="mb-3"),
                            ], width=6),
                            dbc.Col([
                                html.Div([
                                    dbc.Label("Adresse:"),
                                    dbc.Input(id="producteur-adresse", type="text", placeholder="Entrez l'adresse"),
                                ], className="mb-3"),
                                html.Div([
                                    dbc.Label("Téléphone:"),
                                    dbc.Input(id="producteur-telephone", type="text", placeholder="Entrez le téléphone"),
                                ], className="mb-3"),
                            ], width=6),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    dbc.Label("Email:"),
                                    dbc.Input(id="producteur-email", type="email", placeholder="Entrez l'email"),
                                ], className="mb-3"),
                            ], width=6),
                        ]),
                        dbc.Button([
                            html.I(className="fas fa-save me-2"),
                            "Ajouter le producteur"
                        ], id="add-producteur-btn", color="success", className="mt-3"),
                        html.Div(id="producteur-message", className="mt-3")
                    ])
                ], className="shadow-sm")
            ]),
            dbc.Tab(label="Ajouter un produit", children=[
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    dbc.Label("Nom du produit:"),
                                    dbc.Input(id="produit-nom", type="text", placeholder="Entrez le nom"),
                                ], className="mb-3"),
                                html.Div([
                                    dbc.Label("Région:"),
                                    dcc.Dropdown(
                                        id="produit-region",
                                        options=REGIONS,
                                        placeholder="Sélectionnez la région"
                                    ),
                                ], className="mb-3"),
                            ], width=6),
                            dbc.Col([
                                html.Div([
                                    dbc.Label("Score de qualité (0-10):"),
                                    dbc.Input(id="produit-qualite", type="number", min=0, max=10, step=0.1),
                                ], className="mb-3"),
                                html.Div([
                                    dbc.Label("Producteur:"),
                                    dcc.Dropdown(id="produit-producteur", options=[]),
                                ], className="mb-3"),
                            ], width=6),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    dbc.Checkbox(id="produit-bio", className="me-2"),
                                    dbc.Label("Produit biologique", html_for="produit-bio"),
                                ], className="mt-2"),
                            ], width=6),
                        ]),
                        dbc.Button([
                            html.I(className="fas fa-save me-2"),
                            "Ajouter le produit"
                        ], id="add-produit-btn", color="success", className="mt-3"),
                        html.Div(id="produit-message", className="mt-3")
                    ])
                ], className="shadow-sm")
            ])
        ])
    ]),
    # Onglet Sécurité Blockchain
    dbc.Tab(label="Sécurité Blockchain", children=[
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-shield-alt me-2"),
                        "Statut de la Blockchain"
                    ]),
                    dbc.CardBody([
                        html.Div(id="blockchain-status"),
                        dbc.Button([
                            html.I(className="fas fa-check-circle me-2"),
                            "Vérifier l'intégrité"
                        ], id="verify-blockchain-btn", color="success", className="mt-3"),
                    ])
                ], className="shadow-sm")
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-history me-2"),
                        "Historique des transactions"
                    ]),
                    dbc.CardBody([
                        html.Div(id="blockchain-history")
                    ])
                ], className="shadow-sm")
            ], width=6)
        ])
    ])
])

def main_layout(user):
    return dbc.Container([
        # Barre de navigation
        dbc.Navbar(
            dbc.Container([
                dbc.NavbarBrand([
                    html.I(className="fas fa-seedling me-2"),
                    "Traçabilité Agricole Maroc"
                ], className="text-white"),
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink([
                        html.I(className="fas fa-chart-line me-2"),
                        "Tableau de bord"
                    ], href="#dashboard", className="text-white")),
                    dbc.NavItem(dbc.NavLink([
                        html.I(className="fas fa-plus-circle me-2"),
                        "Ajouter données"
                    ], href="#add-data", className="text-white")),
                    dbc.NavItem(dbc.NavLink([
                        html.I(className="fas fa-shield-alt me-2"),
                        "Sécurité Blockchain"
                    ], href="#blockchain", className="text-white")),
                    dbc.NavItem(dbc.NavLink([
                        html.I(className="fas fa-sign-out-alt me-2"),
                        "Déconnexion"
                    ], href="#logout", className="text-white")),
                ], className="ms-auto"),
            ]),
            color="success",
            dark=True,
            className="mb-4"
        ),
        # Contenu principal
        html.Div(id="main-content")
    ], fluid=True)

# Ajout d'un composant dcc.Interval pour rafraîchir les données
interval_component = dcc.Interval(id='interval-component', interval=5*1000, n_intervals=0)

# Layout amélioré avec debug et intervalle
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='current-user', storage_type='session'),
    html.Div(id='page-content'),
    html.Div(id='main-content'),
    html.Div(id='global-error', style={'color': 'red', 'margin': '10px'}),
    interval_component
])

# Page de login
login_layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H2("Connexion", className="mb-4"),
                    dbc.Input(id="login-username", placeholder="Nom d'utilisateur", type="text", className="mb-3"),
                    dbc.Input(id="login-password", placeholder="Mot de passe", type="password", className="mb-3"),
                    dbc.Button("Se connecter", id="login-btn", color="primary", className="mb-3"),
                    html.Div(id="login-message", className="mt-2")
                ])
            ])
        ], width=6)
    ], justify="center")
])

# Callback combiné pour afficher la bonne page et le contenu principal avec debug
@app.callback(
    Output('page-content', 'children'),
    Output('main-content', 'children'),
    Output('global-error', 'children'),
    Input('url', 'pathname'),
    State('current-user', 'data')
)
def display_and_render(pathname, user):
    try:
        if pathname == '/logout':
            flask_session.clear()
            return login_layout, '', ''
        if user is None:
            return login_layout, '', ''
        # Affichage du layout principal
        try:
            role = user.get('role')
            if not role:
                return main_layout(user), html.Div(f"Utilisateur sans rôle : {user}"), ''
            if role == 'admin':
                return main_layout(user), tabs_layout, ''
            else:
                return main_layout(user), dbc.Tabs(tabs_layout.children[1:]), ''
        except Exception as e:
            return main_layout(user), html.Div("Erreur lors de l'affichage du contenu principal."), f"render_main_content: {str(e)}"
    except Exception as e:
        return html.Div("Erreur lors de l'affichage de la page."), '', f"display_page: {str(e)}"

# Callback pour gérer la connexion (debug inclus)
@app.callback(
    Output('login-message', 'children'),
    Output('current-user', 'data'),
    Output('url', 'pathname'),
    Input('login-btn', 'n_clicks'),
    State('login-username', 'value'),
    State('login-password', 'value')
)
def login(n_clicks, username, password):
    if not n_clicks:
        return '', None, dash.no_update
    user = authenticate(username, password)
    if user:
        flask_session['user'] = user
        return '', user, '/dashboard/'
    else:
        return dbc.Alert("Nom d'utilisateur ou mot de passe incorrect", color="danger"), None, dash.no_update

# Callback pour mettre à jour la liste des producteurs
@app.callback(
    Output('produit-producteur', 'options'),
    [Input('interval-component', 'n_intervals')]
)
def update_producteur_list(n):
    session = Session()
    producteurs = session.query(Producteur).all()
    options = [{'label': p.nom, 'value': p.id} for p in producteurs]
    session.close()
    return options

# Callback pour générer le QR code
def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{img_b64}"

# Callback pour ajouter un producteur
@app.callback(
    Output('producteur-message', 'children'),
    [Input('add-producteur-btn', 'n_clicks')],
    [State('producteur-nom', 'value'),
     State('producteur-region', 'value'),
     State('producteur-adresse', 'value'),
     State('producteur-telephone', 'value'),
     State('producteur-email', 'value')]
)
def add_producteur(n_clicks, nom, region, adresse, telephone, email):
    if n_clicks is None:
        return ""
    if not all([nom, region]):
        return dbc.Alert("Le nom et la région sont obligatoires", color="danger")
    try:
        # Créer les données sécurisées
        producteur_data = {
            "type": "producteur",
            "nom": nom,
            "region": region,
            "adresse": adresse,
            "telephone": telephone,
            "email": email,
            "timestamp": datetime.now().isoformat()
        }
        # Sécuriser les données dans la blockchain
        data_hash = data_security.secure_data(producteur_data)
        # Sauvegarder dans la base de données
        session = Session()
        new_producteur = Producteur(
            nom=nom,
            region=region,
            adresse=adresse,
            telephone=telephone,
            email=email,
            data_hash=data_hash
        )
        session.add(new_producteur)
        session.commit()
        producteur_id = new_producteur.id
        session.close()
        # Générer le QR code (par exemple avec l'ID et le hash)
        qr_data = f"Producteur ID: {producteur_id}\nHash: {data_hash}"
        qr_img = generate_qr_code(qr_data)
        return html.Div([
            dbc.Alert("Producteur ajouté avec succès et sécurisé dans la blockchain!", color="success"),
            html.P("QR code d'authentification du producteur :"),
            html.Img(src=qr_img, style={"width": "200px", "margin": "10px 0"})
        ])
    except Exception as e:
        return dbc.Alert(f"Erreur lors de l'ajout: {str(e)}", color="danger")

# Callback pour ajouter un produit
@app.callback(
    Output('produit-message', 'children'),
    [Input('add-produit-btn', 'n_clicks')],
    [State('produit-nom', 'value'),
     State('produit-region', 'value'),
     State('produit-qualite', 'value'),
     State('produit-producteur', 'value'),
     State('produit-bio', 'value')]
)
def add_produit(n_clicks, nom, region, qualite, producteur_id, est_bio):
    if n_clicks is None:
        return ""
    
    if not all([nom, region, producteur_id]):
        return dbc.Alert("Le nom, la région et le producteur sont obligatoires", color="danger")
    
    try:
        # Créer les données sécurisées
        produit_data = {
            "type": "produit",
            "nom": nom,
            "region": region,
            "qualite_score": qualite,
            "producteur_id": producteur_id,
            "est_bio": bool(est_bio),
            "timestamp": datetime.now().isoformat()
        }
        
        # Sécuriser les données dans la blockchain
        data_hash = data_security.secure_data(produit_data)
        
        # Sauvegarder dans la base de données
        session = Session()
        new_produit = Produit(
            nom=nom,
            region=region,
            qualite_score=qualite,
            producteur_id=producteur_id,
            est_bio=bool(est_bio),
            data_hash=data_hash  # Stocker l'hash de la blockchain
        )
        session.add(new_produit)
        session.commit()
        session.close()
        
        return dbc.Alert("Produit ajouté avec succès et sécurisé dans la blockchain!", color="success")
    except Exception as e:
        return dbc.Alert(f"Erreur lors de l'ajout: {str(e)}", color="danger")

# Callback pour mettre à jour les filtres
@app.callback(
    [Output('region-dropdown', 'options'),
     Output('product-dropdown', 'options')],
    [Input('interval-component', 'n_intervals')]
)
def update_dropdown_options(n):
    try:
        regions_df = get_cached_data("SELECT DISTINCT region FROM produit")
        region_options = [{'label': 'Toutes les régions', 'value': 'all'}] + \
                        [{'label': r, 'value': r} for r in regions_df['region'].dropna().tolist()]
        
        products_df = get_cached_data("SELECT DISTINCT nom FROM produit")
        product_options = [{'label': 'Tous les produits', 'value': 'all'}] + \
                         [{'label': p, 'value': p} for p in products_df['nom'].dropna().tolist()]
        
        return region_options, product_options
    except Exception as e:
        logger.error(f"Erreur dans update_dropdown_options: {str(e)}")
        return [], []

# Callback pour graphique région
@app.callback(
    Output('region-graph', 'figure'),
    [Input('region-dropdown', 'value'),
     Input('product-dropdown', 'value'),
     Input('interval-component', 'n_intervals')]
)
def update_region_graph(selected_region, selected_product, n):
    try:
        query = "SELECT region, COUNT(*) as count FROM produit"
        filters = []
        params = {}

        if selected_region != 'all':
            filters.append("region = :region")
            params['region'] = selected_region
        if selected_product != 'all':
            filters.append("nom = :nom")
            params['nom'] = selected_product

        if filters:
            query += " WHERE " + " AND ".join(filters)

        query += " GROUP BY region"

        df = pd.read_sql(query, engine, params=params)

        if df.empty:
            return {
                'data': [],
                'layout': go.Layout(
                    title="Aucune donnée disponible",
                    annotations=[{
                        'text': 'Aucune donnée disponible',
                        'xref': 'paper',
                        'yref': 'paper',
                        'showarrow': False,
                        'font': {'size': 20}
                    }]
                )
            }

        fig = px.bar(
            df,
            x='region',
            y='count',
            title="Nombre de produits par région",
            color='region',
            labels={'count': 'Nombre de produits', 'region': 'Région'}
        )
        
        fig.update_layout(
            xaxis_title="Région",
            yaxis_title="Nombre de produits",
            template="plotly_white",
            hovermode="x unified"
        )
        
        return fig
    except Exception as e:
        logger.error(f"Erreur dans update_region_graph: {str(e)}")
        return {
            'data': [],
            'layout': go.Layout(
                title="Erreur lors du chargement des données",
                annotations=[{
                    'text': 'Une erreur est survenue',
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False,
                    'font': {'size': 20}
                }]
            )
        }

# Callback pour qualité
@app.callback(
    Output('quality-graph', 'figure'),
    [Input('region-dropdown', 'value'),
     Input('product-dropdown', 'value'),
     Input('interval-component', 'n_intervals')]
)
def update_quality_graph(selected_region, selected_product, n):
    query = "SELECT nom, qualite_score FROM produit WHERE qualite_score IS NOT NULL"
    filters, params = [], {}

    if selected_region != 'all':
        filters.append("region = :region")
        params['region'] = selected_region
    if selected_product != 'all':
        filters.append("nom = :nom")
        params['nom'] = selected_product

    if filters:
        query += " AND " + " AND ".join(filters)

    df = pd.read_sql(query, engine, params=params)

    if df.empty:
        return {'data': [], 'layout': go.Layout(title="Aucune donnée de qualité disponible")}

    return px.box(df, y='qualite_score', title="Distribution des scores de qualité")

# Callback bio vs conventionnel
@app.callback(
    Output('bio-graph', 'figure'),
    [Input('region-dropdown', 'value'),
     Input('product-dropdown', 'value'),
     Input('interval-component', 'n_intervals')]
)
def update_bio_graph(selected_region, selected_product, n):
    query = "SELECT est_bio, COUNT(*) as count FROM produit"
    filters, params = [], {}

    if selected_region != 'all':
        filters.append("region = :region")
        params['region'] = selected_region
    if selected_product != 'all':
        filters.append("nom = :nom")
        params['nom'] = selected_product

    if filters:
        query += " WHERE " + " AND ".join(filters)

    query += " GROUP BY est_bio"

    df = pd.read_sql(query, engine, params=params)

    if df.empty:
        return {'data': [], 'layout': go.Layout(title="Aucune donnée disponible")}

    df['type'] = df['est_bio'].apply(lambda x: 'Biologique' if x else 'Conventionnel')

    return px.pie(df, values='count', names='type', title="Répartition des produits biologiques vs conventionnels", hole=0.3)

# Callback pour vérifier l'intégrité de la blockchain
@app.callback(
    Output('blockchain-status', 'children'),
    [Input('verify-blockchain-btn', 'n_clicks')]
)
def verify_blockchain(n_clicks):
    if n_clicks is None:
        return ""
    
    is_valid = data_security.is_valid()
    if is_valid:
        return dbc.Alert("La blockchain est valide et sécurisée", color="success")
    else:
        return dbc.Alert("ATTENTION: La blockchain a été compromise!", color="danger")

# Callbacks pour les indicateurs clés
@app.callback(
    Output("kpi-producteurs", "children"),
    Output("kpi-produits", "children"),
    Output("kpi-bio", "children"),
    Output("kpi-regions", "children"),
    Input('interval-component', 'n_intervals')
)
def update_kpis(n):
    session = Session()
    nb_producteurs = session.query(Producteur).count()
    nb_produits = session.query(Produit).count()
    nb_bio = session.query(Produit).filter_by(est_bio=True).count()
    nb_regions = session.query(Producteur.region).distinct().count()
    session.close()
    return nb_producteurs, nb_produits, nb_bio, nb_regions

# Callback pour l'évolution mensuelle des producteurs
@app.callback(
    Output("evolution-producteurs-graph", "figure"),
    Input('interval-component', 'n_intervals')
)
def update_evolution_producteurs(n):
    session = Session()
    producteurs = session.query(Producteur).all()
    session.close()
    if not producteurs:
        return go.Figure(layout=go.Layout(title="Aucune donnée disponible"))
    df = pd.DataFrame([
        {"date": p.data_hash[:10] if p.data_hash else None} for p in producteurs
    ])
    # Si tu as une colonne date d'ajout, utilise-la à la place de data_hash
    if "date" in df.columns:
        df["mois"] = pd.to_datetime(df["date"], errors='coerce').dt.to_period("M")
        evolution = df.groupby("mois").size().reset_index(name="Nouveaux producteurs")
        fig = px.bar(evolution, x="mois", y="Nouveaux producteurs", title="Nouveaux producteurs par mois")
        return fig
    else:
        return go.Figure(layout=go.Layout(title="Aucune donnée de date disponible"))

# Lancement de l'application
if __name__ == '__main__':
    try:
        logger.info("Démarrage du serveur dashboard")
        app.run(
            debug=Config.DEBUG,
            port=Config.PORT,
            host=Config.HOST,
            use_reloader=True
        )
    except Exception as e:
        logger.error(f"Erreur lors du démarrage du serveur: {str(e)}")
        raise