import { useState } from "react";
import LoginForm from "./LoginForm";
import ReportForm from "./ReportForm";
import TicketLookup from "./TicketLookup";
import StatusUpdate from "./StatusUpdate";
import TicketCard from "./TicketCard";
import { getToken, submitProblemReport } from "../lib/api";
import type { Ticket } from "../lib/api";

export default function App() {
  const [token, setToken] = useState<string | null>(getToken());
  const [submittedTicket, setSubmittedTicket] = useState<Ticket | null>(null);

  return (
    <div className="app">
      {token ? (
        <div className="dashboard">
          <header className="app-header">
            <h1>Kiwibot Reports</h1>
            <button
              className="logout"
              onClick={() => {
                localStorage.removeItem("kiwibot_token");
                setToken(null);
              }}
            >
              Logout
            </button>
          </header>
          <main className="grid">
            <ReportForm
              onSubmit={async (report) => {
                const ticket = await submitProblemReport(report);
                setSubmittedTicket(ticket);
              }}
            />
            <div className="side">
              <TicketLookup />
              <StatusUpdate />
            </div>
          </main>
          {submittedTicket && <TicketCard ticket={submittedTicket} />}
        </div>
      ) : (
        <LoginForm onSuccess={setToken} />
      )}
    </div>
  );
}
