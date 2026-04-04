import { createDataStreamResponse, formatDataStreamPart } from "ai";
import type { AnswerSource } from "@/types/ask";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";
const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === "true";

const MOCK_TOKENS = [
  "これは",
  "モック",
  "の",
  "ストリーミング",
  "回答",
  "です。\n\n",
  "## 検索結果\n\n",
  "データベースから",
  "関連情報が",
  "見つかりました。\n\n",
  "詳細は",
  "ソースを",
  "ご確認ください。",
];

const MOCK_SOURCES: AnswerSource[] = [
  {
    file: "doc-001",
    snippet: "関連するドキュメントの抜粋テキストです。詳細な情報が含まれています。",
    score: 0.95,
  },
  {
    file: "doc-002",
    snippet: "別のドキュメントからの関連情報の抜粋です。",
    score: 0.82,
  },
];

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function POST(req: Request) {
  const { messages } = await req.json();
  const question: string = messages.at(-1)?.content ?? "";
  const sessionId = crypto.randomUUID();

  if (USE_MOCK) {
    return createDataStreamResponse({
      execute: async (writer) => {
        for (const token of MOCK_TOKENS) {
          writer.write(formatDataStreamPart("text", token));
          await sleep(80 + Math.random() * 70);
        }
        writer.writeData([{ sources: MOCK_SOURCES as unknown as Record<string, unknown>[] }]);
      },
    });
  }

  const backendRes = await fetch(`${BACKEND_URL}/ask/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      question,
      options: { max_results: 5 },
    }),
  });

  if (!backendRes.ok || !backendRes.body) {
    return new Response("Backend error", { status: 502 });
  }

  return createDataStreamResponse({
    execute: async (writer) => {
      const reader = backendRes.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let currentEvent = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (line.startsWith("event: ")) {
            currentEvent = line.slice(7).trim();
          } else if (line.startsWith("data: ")) {
            const payload = line.slice(6);
            if (currentEvent === "sources") {
              try {
                const sources = JSON.parse(payload) as AnswerSource[];
                writer.writeData([{ sources } as unknown as Record<string, unknown>]);
              } catch {
                // ignore parse error
              }
            } else {
              try {
                const token = JSON.parse(payload) as string;
                writer.write(formatDataStreamPart("text", token));
              } catch {
                // fallback: send as-is
                writer.write(formatDataStreamPart("text", payload));
              }
            }
            currentEvent = "";
          }
        }
      }
    },
  });
}
