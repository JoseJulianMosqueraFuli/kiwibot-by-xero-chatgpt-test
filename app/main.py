import uuid
import logging
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import Config
from datetime import datetime
from app.firebase import get_tickets_collection, get_creator_tickets_collection
import firebase_admin
from firebase_admin import auth
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from app.middleware import RequestIDMiddleware
from app.models import (
    ProblemReport,
    TicketStatus,
    TicketStatusChange,
    Ticket,
    AssignTicketRequest,
)
from app.gpt import GPT
from app.problem_utils import get_problem_location, get_problem_type
from app.identify import sign_in_with_email_and_password
from app.logging_config import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

app = FastAPI()
app.title = "Kiwibot by Xero ChatGPT"
app.version = "v1.0"
config = Config()
templates = Jinja2Templates(directory="app/templates")

security = HTTPBearer()

origins = ["*"]

app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    try:
        decoded_token = auth.verify_id_token(credentials.credentials)
        return decoded_token["uid"]
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/", tags=["Home"])
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/login_user", tags=["User"])
async def login_user(request: Request):
    form_data = await request.form()
    email = form_data.get("email")
    password = form_data.get("password")
    token = sign_in_with_email_and_password(email, password)
    return token


@app.post(
    "/v1/problem-reports",
    tags=["Report"],
    description="Problem report recieve and processing to return a ticker",
)
async def problem_report_endpoint(report: ProblemReport, uid: str = Depends(get_current_user)):
    try:
        if not (-90 <= report.heartbeat.location["lat"] <= 90) or not (
            -180 <= report.heartbeat.location["lon"] <= 180
        ):
            raise HTTPException(
                status_code=400,
                detail="Invalid location range Latitude between [-90,90] Longitude [-180,180], check your values",
            )

        content = report.content
        report_assistant = GPT.get_instance()
        response_content = report_assistant.generate_response(content)

        ticket_id = str(uuid.uuid4())
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

        ticket_dict = ticket.model_dump(mode="json")
        tickets_collection = get_tickets_collection()
        tickets_collection.document(ticket_id).set(ticket_dict)

        creator_tickets_collection = get_creator_tickets_collection()
        creator_ticket_data = {"creator_uuid": uid, "ticket_id": ticket_id}
        creator_tickets_collection.add(creator_ticket_data)

        logger.info(f"Ticket created: {ticket_id}")
        return ticket_dict
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing problem report: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get(
    "/v1/ticket/{ticket_id}",
    tags=["Ticket"],
    description="Get Ticket information by id",
)
async def get_ticket(ticket_id: str):
    try:
        tickets_collection = get_tickets_collection()
        doc_ref = tickets_collection.document(ticket_id)
        ticket_doc = doc_ref.get()

        if ticket_doc.exists:
            return ticket_doc.to_dict()
        else:
            raise HTTPException(status_code=404, detail="Ticket not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ticket {ticket_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.put(
    "/v1/ticket/{ticket_id}/status",
    tags=["Ticket"],
    description="Modify Ticket status information by id adding a reason",
)
async def change_ticket_status(
    ticket_id: str,
    request: Request,
    uid: str = Depends(get_current_user),
):
    try:
        request_data = await request.json()
        new_status = request_data.get("new_status")
        reason = request_data.get("reason")

        valid_statuses = [TicketStatus.open, TicketStatus.in_progress, TicketStatus.closed]
        if new_status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail="Invalid 'new_status' value. Must be 'open', 'in progress', or 'closed'.",
            )

        if not reason:
            raise HTTPException(
                status_code=400,
                detail="Invalid 'reason', need a reason to known why change status",
            )

        tickets_collection = get_tickets_collection()
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

            doc_ref.set(ticket.model_dump(mode="json"))
            logger.info(f"Ticket {ticket_id} status changed to {new_status}")
            return ticket.model_dump(mode="json")
        else:
            raise HTTPException(status_code=404, detail="Ticket not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing ticket status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.put(
    "/v1/ticket/{ticket_id}/assign",
    tags=["Ticket"],
    description="Assign a ticket to a support agent",
)
async def assign_ticket(
    ticket_id: str,
    assign_request: AssignTicketRequest,
    uid: str = Depends(get_current_user),
):
    try:
        tickets_collection = get_tickets_collection()
        doc_ref = tickets_collection.document(ticket_id)
        ticket_doc = doc_ref.get()

        if ticket_doc.exists:
            ticket_data = ticket_doc.to_dict()
            ticket = Ticket(**ticket_data)

            if ticket.status in [TicketStatus.open, TicketStatus.in_progress]:
                ticket.assigned_agent = assign_request.agent_id
                doc_ref.set(ticket.model_dump(mode="json"))
                logger.info(f"Ticket {ticket_id} assigned to agent {assign_request.agent_id}")
                return ticket.model_dump(mode="json")
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Ticket can only be assigned if the status is 'open' or 'in progress'",
                )
        else:
            raise HTTPException(status_code=404, detail="Ticket not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning ticket: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
