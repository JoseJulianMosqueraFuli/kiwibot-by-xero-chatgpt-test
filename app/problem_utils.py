from geopy.geocoders import Nominatim
import googlemaps
import spacy
from spacy.matcher import Matcher
from app.config import Config
from app.models import ProblemType

nlp = spacy.load("en_core_web_sm")
GOOGLE_MAPS_API_KEY = Config.GOOGLE_MAPS_API_KEY


def get_problem_location(lat, lon):
    geolocator = Nominatim(user_agent="kiwibot-problems")

    try:
        location = geolocator.reverse((lat, lon))
        if location:
            return location.address
    except Exception as e:
        print(f"Error retrieving location with Nominatim: {e}")

    gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
    try:
        results = gmaps.reverse_geocode((lat, lon))
        if results:
            return results[0]["formatted_address"]
    except Exception as e:
        print(f"Error retrieving location with Google Maps API: {e}")

    return f"Flat coordinates: ({lat}, {lon})"


def get_problem_type(text):
    try:
        doc = nlp(text)
        for token in doc:
            if token.text.lower() in ["software", "hardware", "field", "undefined"]:
                return ProblemType(token.text.lower())
    except Exception as e:
        print("An error occurred:", str(e))
    return ProblemType.undefined
