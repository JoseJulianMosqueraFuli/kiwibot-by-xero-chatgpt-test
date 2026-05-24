import firebase_admin
from firebase_admin import credentials, firestore
from app.config import Config
from app.logging_config import get_logger

logger = get_logger(__name__)

_db = None
_tickets_collection = None
_creator_tickets_collection = None


def _initialize_firebase():
    global _db
    try:
        cred = credentials.Certificate(Config.SERVICE_ACCOUNT_KEY_FILE)
        firebase_admin.initialize_app(cred)
        _db = firestore.client()
        logger.info("Firebase initialized successfully")
    except ValueError:
        _db = firestore.client()
        logger.info("Firebase app already initialized, using existing instance")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        raise


def get_db():
    global _db
    if _db is None:
        _initialize_firebase()
    return _db


def get_tickets_collection():
    global _tickets_collection
    if _tickets_collection is None:
        db = get_db()
        _tickets_collection = db.collection("tickets")
    return _tickets_collection


def get_creator_tickets_collection():
    global _creator_tickets_collection
    if _creator_tickets_collection is None:
        db = get_db()
        _creator_tickets_collection = db.collection("report_creator")
    return _creator_tickets_collection
