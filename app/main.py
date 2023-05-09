import openai
import spacy
from spacy.matcher import Matcher
import uuid
from fastapi import FastAPI, HTTPException, Request
from app.config import Config
from pydantic import BaseModel, confloat
from enum import Enum
from datetime import datetime
from geopy.geocoders import Nominatim
import firebase_admin
from firebase_admin import credentials, firestore
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
config = Config()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

OPEN_API_KEY = Config.OPEN_API_KEY
SERVICE_ACCOUNT_KEY_FILE = Config.SERVICE_ACCOUNT_KEY_FILE
GOOGLE_MAPS_API_KEY = Config.GOOGLE_MAPS_API_KEY

cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_FILE)
app_test = firebase_admin.initialize_app(cred)
db = firestore.client()

nlp = spacy.load("en_core_web_sm")
messages = [
    {
        "role": "system",
        "content": "You're a great Problem Report tool to summary the information error like software, hardware or field inside of reports ",
    },
    {
        "role": "user",
        "content": "I need that you response must be clear an concise for the next information no more to two sentences, and don't add formalizims only summary of the report issue.",
    },
    {
        "role": "assistant",
        "content": "Understood! Please provide me with the information from the report, and I'll summarize the issue for you in two concise sentences.",
    },
    {
        "role": "user",
        "content": "If your input seems like: I'm experiencing a hardware issue with my Kiwibot at location New York. The issue is related to the wheels not moving properly. I noticed this problem when the bot was attempting to navigate uneven surfaces. The wheels seem to get stuck frequently. Response some like the next: The Kiwibot at our NY location is experiencing a hardware problem with the wheels, causing frequent sticking and hindering its mobility, especially on uneven surfaces.",
    },
]


class ChatGPT:
    _instance = None
    openai.api_key = Config.OPEN_API_KEY

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ChatGPT()
        return cls._instance

    def __init__(self):
        self.context = messages

    def generate_response(self, message):
        self.context.append({"role": "user", "content": message})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=self.context
        )
        self.context.append(
            {
                "role": "assistant",
                "content": response["choices"][0]["message"]["content"],
            }
        )
        return response["choices"][0]["message"]["content"]


class BotStatus(str, Enum):
    available = "available"
    busy = "busy"
    reserved = "reserved"


class BotHeartbeat(BaseModel):
    bot_id: str
    timestamp: datetime
    location: dict
    status: BotStatus
    battery_level: confloat(ge=0, le=100)
    software_version: str
    hardware_version: str


class ProblemReport(BaseModel):
    content: str
    heartbeat: BotHeartbeat


class ProblemType(str, Enum):
    software = "software"
    hardware = "hardware"
    field = "field"


class TicketStatus(str, Enum):
    open = "open"
    in_progress = "in progress"
    closed = "closed"


class TicketStatusChange(BaseModel):
    timestamp: datetime
    status: TicketStatus
    reason: str


class Ticket(BaseModel):
    ticket_id: str
    problem_location: str
    problem_type: ProblemType
    summary: str
    bot_id: str
    status: TicketStatus
    status_changes: Optional[List[TicketStatusChange]] = []


tickets_collection = db.collection("tickets")


@app.post("/problem-report")
async def problem_report_endpoint(report: ProblemReport):
    try:
        ticket_id = str(uuid.uuid4())

        if not (-90 <= report.heartbeat.location["lat"] <= 90) or not (
            -180 <= report.heartbeat.location["lon"] <= 180
        ):
            raise HTTPException(
                status_code=400,
                detail="Invalid location range Latitude between [-90,90] Longitude [-180,180], check your values",
            )

        content = report.content

        assistant = ChatGPT.get_instance()

        response_content = assistant.generate_response(content)

        ticket = Ticket(
            ticket_id=ticket_id,
            problem_location=get_problem_location(
                report.heartbeat.location["lat"],
                report.heartbeat.location["lon"],
            ),
            problem_type=get_problem_type(response_content),
            summary=response_content,
            bot_id=report.heartbeat.bot_id,
            status=TicketStatus.open,
        )

        ticket_dict = ticket.dict()
        tickets_collection.document(ticket_id).set(ticket_dict)

        return ticket.dict()
    except Exception as e:
        print(str(e))
        raise


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
    doc = nlp(text)
    for token in doc:
        if token.text.lower() in ["software", "hardware", "field"]:
            return ProblemType(token.text.lower())
    return None


def get_location_info(location_text):
    doc = nlp(location_text)

    location_entities = []

    for ent in doc.ents:
        if ent.label_ in ["GPE", "LOC"]:
            location_entities.append(ent.text)

    if location_entities:
        return ", ".join(location_entities)

    return None


@app.get("/ticket/{ticket_id}")
async def get_ticket(ticket_id: str):
    try:
        doc_ref = tickets_collection.document(ticket_id)
        ticket_doc = doc_ref.get()

        if ticket_doc.exists:
            ticket_data = ticket_doc.to_dict()
            return ticket_data
        else:
            raise HTTPException(
                status_code=404,
                detail="Ticket not found",
            )
    except Exception as e:
        print(str(e))
        raise


@app.patch("/ticket/{ticket_id}/status")
async def change_ticket_status(ticket_id: str, request: Request):
    try:
        request_data = await request.json()
        new_status = request_data.get("new_status")
        reason = request_data.get("reason")

        if not new_status or not reason:
            raise HTTPException(
                status_code=400,
                detail="Missing 'new_status' or 'reason' in request body.",
            )

        doc_ref = tickets_collection.document(ticket_id)
        ticket_doc = doc_ref.get()

        if ticket_doc.exists:
            ticket_data = ticket_doc.to_dict()
            ticket = Ticket(**ticket_data)

            change = TicketStatusChange(
                timestamp=datetime.now(), status=new_status, reason=reason
            )
            ticket.status_changes.append(change)
            ticket.status = new_status

            doc_ref.set(ticket.dict())

            return ticket.dict()
        else:
            raise HTTPException(
                status_code=404,
                detail="Ticket not found",
            )
    except Exception as e:
        print(str(e))
        raise
