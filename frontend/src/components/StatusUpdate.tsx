import { useState } from "react";
import type { FormEvent } from "react";
import { updateStatus } from "../lib/api";

const STATUSES = ["open", "in progress", "closed"];

export default function StatusUpdate() {
  const [ticketId, setTicketId] = useState("");
  const [newStatus, setNewStatus] = useState(STATUSES[1]);
  const [reason, setReason] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      await updateStatus(ticketId.trim(), newStatus, reason);
      setSuccess(`Status updated to "${newStatus}"`);
      setTicketId("");
      setReason("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update status");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="panel-form">
      <h3>Change Ticket Status</h3>
      <label>
        Ticket ID
        <input
          value={ticketId}
          onChange={(e) => setTicketId(e.target.value)}
          placeholder="Enter ticket UUID..."
          required
        />
      </label>
      <label>
        New Status
        <select value={newStatus} onChange={(e) => setNewStatus(e.target.value)}>
          {STATUSES.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </label>
      <label>
        Reason
        <input
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="Reason for change..."
          required
        />
      </label>
      {error && <p className="error">{error}</p>}
      {success && <p className="success">{success}</p>}
      <button type="submit" disabled={loading}>
        {loading ? "Updating..." : "Update Status"}
      </button>
    </form>
  );
}
