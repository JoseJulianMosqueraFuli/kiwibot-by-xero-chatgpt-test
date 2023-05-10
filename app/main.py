import uuid
from fastapi import FastAPI, HTTPException, Request
from app.config import Config
from datetime import datetime
from .firebase import tickets_collection
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from app.models import (
    ProblemReport,
    TicketStatus,
    TicketStatusChange,
    Ticket,
)
from app.gpt import GPT
from app.problem_utils import get_problem_location, get_problem_type


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


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post(
    "/problem-report",
    tags=["Report"],
    description="Problem report recieve and processing to return a ticker",
)
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
