import firebase_admin
from firebase_admin import credentials, firestore
from app.config import Config

SERVICE_ACCOUNT_KEY_FILE = Config.SERVICE_ACCOUNT_KEY_FILE
cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_FILE)
firebase_admin.initialize_app(cred)
db = firestore.client()
tickets_collection = db.collection("tickets")
creator_tickets_collection = db.collection("report_creator")
