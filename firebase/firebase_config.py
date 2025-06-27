import firebase_admin
from firebase_admin import credentials, db

# Verifica se o Firebase já foi inicializado
if not firebase_admin._apps:
    # cred = credentials.Certificate("firebase/nutria.json")
    cred = credentials.Certificate("/etc/secrets/nutria.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://nutria-eafaa-default-rtdb.firebaseio.com/'
    })
