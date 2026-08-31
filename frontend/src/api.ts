import type {
  Report,
  ResearchEvent,
} from "./types";

const API_BASE_URL =
  "http://127.0.0.1:8000";

export async function getReports(): Promise<Report[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/reports`
  );

  if (!response.ok) {
    throw new Error(
      "Failed to load reports"
    );
  }

  return response.json();
}

export async function getReport(
  reportId: number
): Promise<Report> {
  const response = await fetch(
    `${API_BASE_URL}/api/reports/${reportId}`
  );

  if (!response.ok) {
    throw new Error(
      "Failed to load report"
    );
  }

  return response.json();
}

export async function researchCompany(
  companyName: string,
  onEvent: (event: ResearchEvent) => void
): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/api/research`,
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json",
      },

      body: JSON.stringify({
        company_name: companyName,
      }),
    }
  );

  if (!response.ok) {
    throw new Error(
      "Research request failed"
    );
  }

  if (!response.body) {
    throw new Error(
      "Response body is unavailable"
    );
  }

  const reader =
    response.body.getReader();

  const decoder =
    new TextDecoder();

  let buffer = "";

  while (true) {
    const {
      value,
      done,
    } = await reader.read();

    if (done) {
      break;
    }

    buffer += decoder.decode(
      value,
      {
        stream: true,
      }
    );

    const events =
      buffer.split("\n\n");

    buffer =
      events.pop() ?? "";

    for (const event of events) {
      const line = event
        .split("\n")
        .find((line) =>
          line.startsWith("data:")
        );

      if (!line) {
        continue;
      }

      const json = line.replace(
        /^data:\s*/,
        ""
      );

      const parsed =
        JSON.parse(json) as ResearchEvent;

      onEvent(parsed);
    }
  }
}

export async function deleteReport(
  id: number
): Promise<void> {
  const response = await fetch(
    `http://127.0.0.1:8000/api/reports/${id}`,
    {
      method: "DELETE",
    }
  );

  if (!response.ok) {
    throw new Error(
      "Failed to delete report"
    );
  }
}