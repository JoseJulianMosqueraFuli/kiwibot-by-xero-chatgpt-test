import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  login,
  submitProblemReport,
  getTicket,
  updateStatus,
  assignAgent,
  ApiError,
  setToken,
  getToken,
} from "../src/lib/api";

const TOKEN_KEY = "kiwibot_token";

const ticketFixture = {
  ticket_id: "ticket_123",
  problem_location: "Mexico City, Mexico",
  problem_type: "hardware",
  summary: "hardware problem with the wheels",
  bot_id: "bot_123",
  status: "open",
  status_changes: [],
  assigned_agent: null,
};

const reportFixture = {
  content: "El bot no responde",
  heartbeat: {
    bot_id: "bot_123",
    timestamp: "2023-05-10T12:00:00",
    location: { lat: 19.4326, lon: -99.1332 },
    status: "available",
    battery_level: 80.0,
    software_version: "1.0.0",
    hardware_version: "2.0.0",
  },
};

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

beforeEach(() => {
  localStorage.clear();
  vi.restoreAllMocks();
});

describe("login", () => {
  it("posts credentials as form data and returns idToken", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(jsonResponse({ idToken: "abc123" }));

    const token = await login("user@example.com", "pass");

    expect(token).toBe("abc123");
    expect(fetchMock).toHaveBeenCalledWith(
      "/login_user",
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({
          "Content-Type": "application/x-www-form-urlencoded",
        }),
      }),
    );
    const body = fetchMock.mock.calls[0][1].body as URLSearchParams;
    expect(body.get("email")).toBe("user@example.com");
    expect(body.get("password")).toBe("pass");
  });

  it("stores the idToken for subsequent requests", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(jsonResponse({ idToken: "abc123" }));
    await login("user@example.com", "pass");
    expect(getToken()).toBe("abc123");
  });

  it("throws ApiError on failed login", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(jsonResponse({ detail: "INVALID_PASSWORD" }, 400));
    await expect(login("user@example.com", "wrong")).rejects.toThrow(ApiError);
  });
});

describe("submitProblemReport", () => {
  it("posts the report as JSON with the bearer token", async () => {
    setToken("tok123");
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(jsonResponse(ticketFixture));

    const result = await submitProblemReport(reportFixture);

    expect(result).toEqual(ticketFixture);
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe("/v1/problem-reports");
    expect(init.method).toBe("POST");
    expect((init.headers as Headers).get("Authorization")).toBe("Bearer tok123");
    expect(JSON.parse(init.body)).toEqual(reportFixture);
  });

  it("throws ApiError with server detail on error", async () => {
    setToken("tok123");
    vi.spyOn(globalThis, "fetch").mockResolvedValue(jsonResponse({ detail: "Bad thing" }, 500));
    await expect(submitProblemReport(reportFixture)).rejects.toMatchObject({
      message: "Bad thing",
      status: 500,
    });
  });
});

describe("getTicket", () => {
  it("fetches the ticket without requiring a token", async () => {
    localStorage.clear();
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(jsonResponse(ticketFixture));

    const result = await getTicket("ticket_123");

    expect(result.ticket_id).toBe("ticket_123");
    expect(fetchMock).toHaveBeenCalledWith("/v1/ticket/ticket_123", expect.anything());
  });

  it("throws ApiError on 404", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(jsonResponse({ detail: "Ticket not found" }, 404));
    await expect(getTicket("missing")).rejects.toMatchObject({ status: 404 });
  });
});

describe("updateStatus", () => {
  it("PUTs the new status and reason", async () => {
    setToken("tok123");
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(jsonResponse({ ...ticketFixture, status: "closed" }));

    const result = await updateStatus("ticket_123", "closed", "Ticket finished");

    expect(result.status).toBe("closed");
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe("/v1/ticket/ticket_123/status");
    expect(init.method).toBe("PUT");
    expect(JSON.parse(init.body)).toEqual({ new_status: "closed", reason: "Ticket finished" });
  });
});

describe("assignAgent", () => {
  it("PUTs the agent id", async () => {
    setToken("tok123");
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(jsonResponse({ ...ticketFixture, assigned_agent: "agent_001" }));

    const result = await assignAgent("ticket_123", "agent_001");

    expect(result.assigned_agent).toBe("agent_001");
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe("/v1/ticket/ticket_123/assign");
    expect(JSON.parse(init.body)).toEqual({ agent_id: "agent_001" });
  });
});
