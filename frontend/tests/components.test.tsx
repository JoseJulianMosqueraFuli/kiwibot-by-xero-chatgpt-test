import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import LoginForm from "../src/components/LoginForm";
import ReportForm from "../src/components/ReportForm";
import TicketLookup from "../src/components/TicketLookup";
import StatusUpdate from "../src/components/StatusUpdate";
import TicketCard from "../src/components/TicketCard";
import { login, getTicket, updateStatus, submitProblemReport } from "../src/lib/api";

vi.mock("../src/lib/api", () => ({
  login: vi.fn(),
  getTicket: vi.fn(),
  updateStatus: vi.fn(),
  submitProblemReport: vi.fn(),
}));

describe("LoginForm", () => {
  it("submits email and password to login and calls onSuccess", async () => {
    const user = userEvent.setup();
    const onSuccess = vi.fn();
    (login as ReturnType<typeof vi.fn>).mockResolvedValue("tok123");

    render(<LoginForm onSuccess={onSuccess} />);

    await user.type(screen.getByLabelText(/email/i), "user@example.com");
    await user.type(screen.getByLabelText(/password/i), "secret");
    await user.click(screen.getByRole("button", { name: /login/i }));

    await waitFor(() => expect(login).toHaveBeenCalledWith("user@example.com", "secret"));
    await waitFor(() => expect(onSuccess).toHaveBeenCalledWith("tok123"));
  });
});

describe("ReportForm", () => {
  it("builds the problem report payload and calls onSubmit", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn().mockResolvedValue(undefined);

    render(<ReportForm onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText(/bot id/i), "bot_123");
    fireEvent.change(screen.getByLabelText(/timestamp/i), {
      target: { value: "2023-05-10T12:00" },
    });
    await user.type(screen.getByLabelText(/issue description/i), "El bot no responde");
    await user.type(screen.getByLabelText(/latitude/i), "19.4326");
    await user.type(screen.getByLabelText(/longitude/i), "-99.1332");
    await user.type(screen.getByLabelText(/battery level/i), "80");
    await user.click(screen.getByRole("button", { name: /submit report/i }));

    await waitFor(() => expect(onSubmit).toHaveBeenCalledTimes(1));
    const payload = onSubmit.mock.calls[0][0];
    expect(payload.content).toBe("El bot no responde");
    expect(payload.heartbeat.bot_id).toBe("bot_123");
    expect(payload.heartbeat.location).toEqual({ lat: 19.4326, lon: -99.1332 });
  });
});

describe("TicketLookup", () => {
  it("fetches the ticket and renders its details", async () => {
    const user = userEvent.setup();
    (getTicket as ReturnType<typeof vi.fn>).mockResolvedValue({
      ticket_id: "ticket_123",
      problem_location: "Mexico City, Mexico",
      problem_type: "hardware",
      summary: "wheels stuck",
      bot_id: "bot_123",
      status: "open",
      status_changes: [],
      assigned_agent: null,
    });

    render(<TicketLookup />);

    await user.type(screen.getByLabelText(/ticket id/i), "ticket_123");
    await user.click(screen.getByRole("button", { name: /search/i }));

    await waitFor(() => expect(getTicket).toHaveBeenCalledWith("ticket_123"));
    await waitFor(() => expect(screen.getByText(/wheels stuck/i)).toBeInTheDocument());
  });

  it("shows an error message when the ticket is not found", async () => {
    const user = userEvent.setup();
    (getTicket as ReturnType<typeof vi.fn>).mockRejectedValue(new Error("Ticket not found"));

    render(<TicketLookup />);

    await user.type(screen.getByLabelText(/ticket id/i), "missing");
    await user.click(screen.getByRole("button", { name: /search/i }));

    await waitFor(() => expect(screen.getByText(/ticket not found/i)).toBeInTheDocument());
  });
});

describe("StatusUpdate", () => {
  it("calls updateStatus with ticket id, status and reason", async () => {
    const user = userEvent.setup();
    (updateStatus as ReturnType<typeof vi.fn>).mockResolvedValue({
      ticket_id: "ticket_123",
      problem_location: "x",
      problem_type: "hardware",
      summary: "s",
      bot_id: "b",
      status: "closed",
      status_changes: [],
      assigned_agent: null,
    });

    render(<StatusUpdate />);

    await user.type(screen.getByLabelText(/ticket id/i), "ticket_123");
    await user.type(screen.getByLabelText(/reason/i), "Ticket finished");
    await user.click(screen.getByRole("button", { name: /update status/i }));

    await waitFor(() =>
      expect(updateStatus).toHaveBeenCalledWith("ticket_123", "in progress", "Ticket finished"),
    );
  });
});

describe("TicketCard", () => {
  it("renders ticket fields", () => {
    render(
      <TicketCard
        ticket={{
          ticket_id: "ticket_123",
          problem_location: "Mexico City",
          problem_type: "software",
          summary: "summary text",
          bot_id: "bot_123",
          status: "open",
          status_changes: [{ timestamp: "2023-01-01T00:00:00", status: "open", reason: "created" }],
          assigned_agent: null,
        }}
      />,
    );

    expect(screen.getByText(/ticket_123/)).toBeInTheDocument();
    expect(screen.getByText("summary text")).toBeInTheDocument();
    expect(screen.getByText("Mexico City")).toBeInTheDocument();
  });
});
