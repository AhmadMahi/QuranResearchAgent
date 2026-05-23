export interface ResearchRequest {
  topic: string;
  city: string;
  country: string;
}

export interface QuranRef {
  surah_name: string;
  surah_number: number;
  ayah_number: number;
  text: string;
  reference: string;
}

export interface ResearchResult {
  report: string;
  quran_references: QuranRef[];
  prayer_times: Record<string, string>;
  weather_data: Record<string, unknown>;
  web_results: string[];
  steps: string[];
}

export interface SSEStep {
  step: string;
  agent: string;
}

type OnStep = (s: SSEStep) => void;
type OnComplete = (r: ResearchResult) => void;
type OnError = (msg: string) => void;

/** Parse a raw SSE stream from a POST request. */
export async function streamResearch(
  req: ResearchRequest,
  onStep: OnStep,
  onComplete: OnComplete,
  onError: OnError,
  signal?: AbortSignal
): Promise<void> {
  const backendUrl =
    process.env.NEXT_PUBLIC_BACKEND_URL || "";

  const res = await fetch(`${backendUrl}/api/research`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
    signal,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    onError(body.detail ?? "Request failed");
    return;
  }

  const reader = res.body?.getReader();
  if (!reader) { onError("No response body"); return; }

  const dec = new TextDecoder();
  let buf = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });

    const parts = buf.split("\n\n");
    buf = parts.pop() ?? "";

    for (const block of parts) {
      const lines = block.split("\n");
      let event = "";
      let data = "";
      for (const line of lines) {
        if (line.startsWith("event: ")) event = line.slice(7).trim();
        if (line.startsWith("data: ")) data = line.slice(6).trim();
      }
      if (!data) continue;

      try {
        const parsed = JSON.parse(data);
        if (event === "step" || (event === "status" && parsed.step)) {
          onStep({ step: parsed.step, agent: parsed.agent ?? "" });
        } else if (event === "complete") {
          onComplete(parsed as ResearchResult);
        } else if (event === "error") {
          onError(parsed.message ?? "Unknown error");
        }
      } catch {
        // ignore malformed chunk
      }
    }
  }
}
