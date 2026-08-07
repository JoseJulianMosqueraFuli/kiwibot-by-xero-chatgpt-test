import { useState } from "react";
import type { FormEvent } from "react";
import type { ProblemReport } from "../lib/api";

interface ReportFormProps {
  onSubmit: (report: ProblemReport) => Promise<void>;
}

export default function ReportForm({ onSubmit }: ReportFormProps) {
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);

    const report: ProblemReport = {
      content: String(data.get("content")),
      heartbeat: {
        bot_id: String(data.get("bot_id")),
        timestamp: String(data.get("timestamp")),
        location: {
          lat: Number(data.get("lat")),
          lon: Number(data.get("lon")),
        },
        status: "available",
        battery_level: Number(data.get("battery_level")),
        software_version: String(data.get("software_version") || ""),
        hardware_version: String(data.get("hardware_version") || ""),
      },
    };

    setLoading(true);
    setError(null);
    try {
      await onSubmit(report);
      form.reset();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit report");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="panel-form">
      <h3>New Problem Report</h3>
      <label>
        Bot ID
        <input name="bot_id" required placeholder="e.g. bot_12345" />
      </label>
      <label>
        Timestamp
        <input name="timestamp" type="datetime-local" required />
      </label>
      <div className="row">
        <label>
          Latitude
          <input name="lat" type="number" step="any" min="-90" max="90" required />
        </label>
        <label>
          Longitude
          <input name="lon" type="number" step="any" min="-180" max="180" required />
        </label>
      </div>
      <label>
        Battery Level (%)
        <input name="battery_level" type="number" step="0.01" min="0" max="100" required />
      </label>
      <div className="row">
        <label>
          Software Version
          <input name="software_version" placeholder="e.g. v2.1.0" />
        </label>
        <label>
          Hardware Version
          <input name="hardware_version" placeholder="e.g. v3.0" />
        </label>
      </div>
      <label>
        Issue Description
        <textarea name="content" required rows={4} placeholder="Describe the problem..." />
      </label>
      {error && <p className="error">{error}</p>}
      <button type="submit" disabled={loading}>
        {loading ? "Submitting..." : "Submit Report"}
      </button>
    </form>
  );
}
