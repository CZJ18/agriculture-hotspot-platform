import { config } from "../config.js";

type Query = Record<string, string | number | undefined>;

function buildUrl(path: string, query: Query = {}) {
  const url = new URL(path, config.fastapiBaseUrl);
  for (const [key, value] of Object.entries(query)) {
    if (value !== undefined) url.searchParams.set(key, String(value));
  }
  return url;
}

export class FastapiClient {
  async get(path: string, query?: Query) {
    const response = await fetch(buildUrl(path, query));
    return this.parse(response);
  }

  async post(path: string, body: unknown = {}) {
    const response = await fetch(buildUrl(path), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    return this.parse(response);
  }

  async exportUrl(path: string, query?: Query) {
    return buildUrl(path, query).toString();
  }

  private async parse(response: Response) {
    const text = await response.text();
    if (!response.ok) {
      throw new Error(`FastAPI ${response.status}: ${text}`);
    }
    return text ? JSON.parse(text) : null;
  }
}
