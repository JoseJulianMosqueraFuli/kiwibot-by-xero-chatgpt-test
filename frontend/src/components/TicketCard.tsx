import type { Ticket } from "../lib/api";

interface TicketCardProps {
  ticket: Ticket;
}

export default function TicketCard({ ticket }: TicketCardProps) {
  return (
    <article className="ticket-card">
      <header>
        <h4>Ticket: {ticket.ticket_id}</h4>
        <div className="badges">
          <span className={`badge badge-${ticket.status.replace(" ", "-")}`}>{ticket.status}</span>
          <span className="badge">{ticket.problem_type}</span>
        </div>
      </header>
      <dl>
        <div>
          <dt>Location</dt>
          <dd>{ticket.problem_location}</dd>
        </div>
        <div>
          <dt>Bot ID</dt>
          <dd>{ticket.bot_id}</dd>
        </div>
        <div>
          <dt>Summary</dt>
          <dd>{ticket.summary}</dd>
        </div>
        {ticket.assigned_agent && (
          <div>
            <dt>Assigned Agent</dt>
            <dd>{ticket.assigned_agent}</dd>
          </div>
        )}
      </dl>
      {ticket.status_changes.length > 0 && (
        <div className="status-history">
          <h5>Status History</h5>
          <ul>
            {ticket.status_changes.map((change, i) => (
              <li key={i}>
                <span className="change-status">{change.status}</span>
                <span className="change-reason">{change.reason}</span>
                <span className="change-timestamp">{new Date(change.timestamp).toLocaleString()}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </article>
  );
}
