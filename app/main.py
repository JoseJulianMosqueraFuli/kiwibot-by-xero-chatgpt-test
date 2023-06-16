import uuid
from fastapi import FastAPI, HTTPException, Request
from app.config import Config
from datetime import datetime
from app.firebase import tickets_collection, creator_tickets_collection
import firebase_admin
from firebase_admin import auth
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
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


app = FastAPI()
app.title = "Kiwibot by Xero ChatGPT"
app.version = "v1.0"
config = Config()
templates = Jinja2Templates(directory="app/templates")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


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
    "/problem-report",
    tags=["Report"],
    description="Problem report recieve and processing to return a ticker",
)
async def problem_report_endpoint(report: ProblemReport, request: Request):
    try:
        headers = request.headers
        bearer = headers.get("Authorization")
        token = bearer.split()[1]
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token["uid"]
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=401, detail="Unauthorized")

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

        # notes = []

        # if report.heartbeat.battery_level < 15.00:
        #     notes.append("The battery is low. This could have generated the issue")

        # if report.heartbeat.software_version < "v1.2":
        #     notes.append(
        #         "The software version is outdated. Please update to the latest version"
        #     )

        # if report.heartbeat.hardware_version < "v1.2":
        #     notes.append(
        #         "The hardware version is outdated. Please update to the latest version"
        #     )

        # if len(notes) > 0:
        #     content += "\n*NOTE*: " + ", ".join(notes)

        # if len(notes) == 3:
        #     content += "\n*NOTE*: Urgent revision required."

        report_assistant = GPT.get_instance()

        response_content = report_assistant.generate_response(content)

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
        creator_ticket_data = {"creator_uuid": uid, "ticket_id": ticket_id}
        creator_tickets_collection.add(creator_ticket_data)

        return ticket.dict()
    except Exception as e:
        print(str(e))
        raise


@app.get(
    "/ticket/{ticket_id}",
    tags=["Ticket"],
    description="Get Ticket information by id",
)
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


@app.put(
    "/ticket/{ticket_id}/status",
    tags=["Ticket"],
    description="Modify Ticket status information by id adding a reason",
)
async def change_ticket_status(ticket_id: str, request: Request):
    try:
        headers = request.headers
        bearer = headers.get("Authorization")
        token = bearer.split()[1]
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token["uid"]
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        request_data = await request.json()
        new_status = request_data.get("new_status")
        reason = request_data.get("reason")

        if (
            new_status
            not in (TicketStatus.open, TicketStatus.in_progress, TicketStatus.closed)
            or not reason
        ):
            raise HTTPException(
                status_code=400,
                detail="Invalid 'new_status'  'open' 'in_progress'  'closed' value  in request body.",
            )

        if not reason:
            raise HTTPException(
                status_code=400,
                detail="Invalid 'reason', need a reason to known why change status",
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


@app.put(
    "/ticket/{ticket_id}/assign",
    tags=["Ticket"],
    description="Assign a ticket to a support agent",
)
async def assign_ticket(
    ticket_id: str, assign_request: AssignTicketRequest, request: Request
):
    try:
        headers = request.headers
        bearer = headers.get("Authorization")
        token = bearer.split()[1]
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token["uid"]
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        doc_ref = tickets_collection.document(ticket_id)
        ticket_doc = doc_ref.get()

        if ticket_doc.exists:
            ticket_data = ticket_doc.to_dict()
            ticket = Ticket(**ticket_data)

            if ticket.status in [TicketStatus.open, TicketStatus.in_progress]:
                ticket.assigned_agent = assign_request.agent_id

                doc_ref.set(ticket.dict())

                return ticket.dict()
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Ticket can only be assigned if the status is 'open' or 'in progress'",
                )
        else:
            raise HTTPException(
                status_code=404,
                detail="Ticket not found",
            )
    except Exception as e:
        print(str(e))
        raise
