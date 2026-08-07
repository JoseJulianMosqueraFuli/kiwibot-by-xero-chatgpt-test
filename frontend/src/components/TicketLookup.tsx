import { useState } from "react";
import type { FormEvent } from "react";
import { getTicket } from "../lib/api";
import type { Ticket } from "../lib/api";
import TicketCard from "./TicketCard";

export default function TicketLookup() {
  const [ticketId, setTicketId] = useState("");
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setTicket(null);
    try {
      const result = await getTicket(ticketId.trim());
      setTicket(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ticket not found");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <form onSubmit={handleSubmit} className="panel-form">
        <h3>Lookup Ticket</h3>
        <label>
          Ticket ID
          <input
            value={ticketId}
            onChange={(e) => setTicketId(e.target.value)}
            placeholder="Enter ticket UUID..."
            required
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={loading}>
          {loading ? "Searching..." : "Search"}
        </button>
      </form>
      {ticket && <TicketCard ticket={ticket} />}
    </div>
  );
}
