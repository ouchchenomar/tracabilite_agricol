USERS = [
    {"username": "admin", "password": "admin123", "role": "admin"},
    {"username": "producteur1", "password": "prod123", "role": "producteur"},
    # Ajoute d'autres utilisateurs ici
]

def authenticate(username, password):
    for user in USERS:
        if user["username"] == username and user["password"] == password:
            return user
    return None 