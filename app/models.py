from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, confloat, constr, Field
from enum import Enum


class BotStatus(str, Enum):
    available = "available"
    busy = "busy"
    reserved = "reserved"


class BotHeartbeat(BaseModel):
    bot_id: str
    timestamp: str = Field(..., regex=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")
    location: Dict[constr(regex="^(lat|lon)$"), float]
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
    undefined = "undefined"


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
