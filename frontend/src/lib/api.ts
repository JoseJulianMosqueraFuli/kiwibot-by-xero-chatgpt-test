const TOKEN_KEY = "kiwibot_token";

export interface BotHeartbeat {
  bot_id: string;
  timestamp: string;
  location: { lat: number; lon: number };
  status: "available" | "busy" | "reserved";
  battery_level: number;
  software_version: string;
  hardware_version: string;
}

export interface ProblemReport {
  content: string;
  heartbeat: BotHeartbeat;
}

export interface StatusChange {
  timestamp: string;
  status: string;
  reason: string;
}

export interface Ticket {
  ticket_id: string;
  problem_location: string;
  problem_type: string;
  summary: string;
  bot_id: string;
  status: string;
  status_changes: StatusChange[];
  assigned_agent: string | null;
}

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  const token = getToken();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  const response = await fetch(path, { ...init, headers });
  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`;
    try {
      const body = await response.json();
      if (body && typeof body.detail === "string") {
        detail = body.detail;
      }
    } catch {
      // ignore non-JSON error bodies
    }
    throw new ApiError(detail, response.status);
  }
  return response.json();
}

export async function login(email: string, password: string): Promise<string> {
  const body = new URLSearchParams({ email, password });
  const response = await fetch("/login_user", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!response.ok) {
    throw new ApiError("Login failed", response.status);
  }
  const data = await response.json();
  setToken(data.idToken);
  return data.idToken as string;
}

export function submitProblemReport(report: ProblemReport): Promise<Ticket> {
  return request<Ticket>("/v1/problem-reports", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(report),
  });
}

export function getTicket(ticketId: string): Promise<Ticket> {
  return request<Ticket>(`/v1/ticket/${encodeURIComponent(ticketId)}`);
}

export function updateStatus(
  ticketId: string,
  newStatus: string,
  reason: string,
): Promise<Ticket> {
  return request<Ticket>(`/v1/ticket/${encodeURIComponent(ticketId)}/status`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ new_status: newStatus, reason }),
  });
}

export function assignAgent(ticketId: string, agentId: string): Promise<Ticket> {
  return request<Ticket>(`/v1/ticket/${encodeURIComponent(ticketId)}/assign`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ agent_id: agentId }),
  });
}
