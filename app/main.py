import openai
import spacy
from spacy.matcher import Matcher
import uuid
from fastapi import FastAPI, HTTPException
from app.config import Config
from pydantic import BaseModel, confloat
from enum import Enum
from datetime import datetime
from geopy.geocoders import Nominatim
import firebase_admin
from firebase_admin import credentials, firestore

app = FastAPI()
config = Config()

openai.api_key = Config.OPEN_API_KEY
SERVICE_ACCOUNT_KEY_FILE = Config.SERVICE_ACCOUNT_KEY_FILE

cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_FILE)
app_test = firebase_admin.initialize_app(cred)
db = firestore.client()

nlp = spacy.load("en_core_web_sm")


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


class Ticket(BaseModel):
    ticket_id: str
    problem_location: str
    problem_type: ProblemType
    summary: str
    bot_id: str
    status: TicketStatus


tickets = []
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

        messages = [
            {
                "role": "system",
                "content": "Kiwibot Issue Reporting System. Please provide the details of the problem, including the location, type of issue (software, hardware, or field), and any relevant information.",
            }
        ]
        content = report.content

        messages.append({"role": "user", "content": content})
        ## GTP-4 model wait list, waiting approval
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )
        print(response)
        response_content = response["choices"][0]["message"]["content"]

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

        tickets.append(ticket)
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
        return location.address
    except:
        return None


def get_problem_type(text):
    doc = nlp(text)
    for token in doc:
        if token.text.lower() in ["software", "hardware", "field"]:
            return ProblemType(token.text.lower())
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
