from geopy.geocoders import Nominatim
import googlemaps
import spacy
from spacy.matcher import Matcher
from app.config import Config
from app.models import ProblemType
from app.logging_config import get_logger

logger = get_logger(__name__)

_nlp = None
_geolocator = None
_gmaps = None


def _get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


def _get_geolocator():
    global _geolocator
    if _geolocator is None:
        _geolocator = Nominatim(user_agent="kiwibot-problems")
    return _geolocator


def _get_gmaps():
    global _gmaps
    if _gmaps is None:
        _gmaps = googlemaps.Client(key=Config.GOOGLE_MAPS_API_KEY)
    return _gmaps


def get_problem_location(lat, lon):
    geolocator = _get_geolocator()

    try:
        location = geolocator.reverse((lat, lon))
        if location:
            return location.address
    except Exception as e:
        logger.warning(f"Error retrieving location with Nominatim: {e}")

    gmaps = _get_gmaps()
    try:
        results = gmaps.reverse_geocode((lat, lon))
        if results:
            return results[0]["formatted_address"]
    except Exception as e:
        logger.warning(f"Error retrieving location with Google Maps API: {e}")

    return f"Flat coordinates: ({lat}, {lon})"


def get_problem_type(text):
    try:
        nlp = _get_nlp()
        doc = nlp(text)
        for token in doc:
            if token.text.lower() in ["software", "hardware", "field", "undefined"]:
                return ProblemType(token.text.lower())
    except Exception as e:
        logger.error(f"An error occurred while determining problem type: {e}")
    return ProblemType.undefined
