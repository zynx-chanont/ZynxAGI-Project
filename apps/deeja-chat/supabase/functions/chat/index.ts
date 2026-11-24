// Deeja v2.0 AI streaming chat via Lovable AI Gateway
const DEFAULT_ALLOWED_ORIGINS = [
  "http://localhost:3000",
  "http://localhost:3001",
  "http://localhost:3002",
];

function getAllowedOrigins() {
  const raw = Deno.env.get("CORS_ALLOWED_ORIGINS");
  if (!raw) return DEFAULT_ALLOWED_ORIGINS;
  return raw.split(",").map((s) => s.trim()).filter(Boolean);
}

function buildCorsHeaders(origin: string | null) {
  const allowedOrigins = getAllowedOrigins();
  const allowOrigin = origin && allowedOrigins.includes(origin) ? origin : allowedOrigins[0];
  return {
    "Access-Control-Allow-Origin": allowOrigin,
    "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
    "Vary": "Origin",
  };
}

const PROMPT_ENGINEER_FRAMEWORK = `🧠 ACTIVE MODE: Prompt Engineer (Deeja v2.0 Framework)

ทำหน้าที่เป็น AI Prompt Engineer ขั้นสูง วิเคราะห์และยกระดับ prompt ของผู้ใช้ให้ได้คุณภาพ 10/10

4-Step Framework:
1) Multi-Dimensional Analysis — Technical (structure, clarity, parameters, constraints), Business (goal, ROI, scalability), UX (usability, maintainability)
2) Strategic Verification — Goal / Problem / Audience / Impact / Constraints / Success metrics
3) Scoring (1–10) — Clarity, Specificity, Structure, Expected Outcome
4) Prompt Rewrite — เขียนใหม่ให้ได้ 10/10

ตอบกลับด้วยรูปแบบนี้เท่านั้น (ภาษาไทย):

📌 วิเคราะห์: [หัวข้อ]

📊 Analysis Scores:
Clarity: X/10 | Specificity: X/10 | Structure: X/10 | Outcome: X/10

✅ Strategic Summary:
Purpose: [สรุป]
Target: [สรุป]
Impact: [สรุป]

📊 Overall Score: X/10

🧠 Coaching Tip: [เฉพาะเมื่อคะแนนรวม < 10]

✨ Improved Prompt:
[prompt ที่เขียนใหม่ พร้อมคัดลอกใช้งานได้ทันที — ใช้ markdown ที่ชัดเจน]

กฎ: Always improve never just explain · concise but high-value · avoid generic answers · ask follow-up only if critical`;

const MODE_PROMPTS: Record<string, string> = {
  T: "Mode T (Teach): Explain like a patient teacher. Use clear structure, examples, and step-by-step breakdowns.",
  E: "Mode E (Explore): Be curious and exploratory. Suggest ideas, alternatives, and creative angles.",
  F: "Mode F (Focus): Be concise and direct. Give only the essential answer with no fluff.",
  R: "Mode R (Reflect): Be thoughtful and analytical. Reflect on tradeoffs, implications, and nuance.",
  P: PROMPT_ENGINEER_FRAMEWORK,
};

const BASE_PERSONA = `You are "Deeja v2.0" — a thoughtful AI assistant for Thai users. ตอบเป็นภาษาไทยเป็นหลัก ใช้ศัพท์เทคนิคภาษาอังกฤษเมื่อจำเป็น น้ำเสียง professional, insightful, efficient ใช้ markdown เมื่อช่วยให้อ่านง่ายขึ้น`;

// Simple in-memory rate limit per IP (best-effort, per-instance)
const rateMap = new Map<string, { count: number; reset: number }>();
const LIMIT = 20; // requests
const WINDOW_MS = 60_000; // per minute

function rateLimited(ip: string) {
  const now = Date.now();
  const entry = rateMap.get(ip);
  if (!entry || entry.reset < now) {
    rateMap.set(ip, { count: 1, reset: now + WINDOW_MS });
    return false;
  }
  entry.count++;
  return entry.count > LIMIT;
}

type ChatRole = "user" | "assistant";
type ChatMessage = { role: ChatRole; content: string };

function parseAndValidateBody(body: unknown): { mode: string; messages: ChatMessage[] } {
  if (!body || typeof body !== "object") throw new Error("invalid request body");
  const source = body as Record<string, unknown>;
  const mode = typeof source.mode === "string" ? source.mode : "F";
  const messages = source.messages;
  if (!Array.isArray(messages) || messages.length === 0) {
    throw new Error("messages required");
  }

  const cleaned = messages
    .filter((m): m is Record<string, unknown> => !!m && typeof m === "object")
    .filter((m) => (m.role === "user" || m.role === "assistant") && typeof m.content === "string")
    .map((m) => ({ role: m.role as ChatRole, content: (m.content as string).slice(0, 8000) }));

  if (cleaned.length === 0) throw new Error("no valid messages");
  return { mode, messages: cleaned };
}

Deno.serve(async (req) => {
  const corsHeaders = buildCorsHeaders(req.headers.get("origin"));
  if (req.method === "OPTIONS") return new Response(null, { headers: corsHeaders });

  try {
    const ip = req.headers.get("x-forwarded-for")?.split(",")[0].trim() || "unknown";
    if (rateLimited(ip)) {
      return new Response(JSON.stringify({ error: "Rate limit exceeded. Try again in a minute." }), {
        status: 429,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    let parsed: { mode: string; messages: ChatMessage[] };
    try {
      parsed = parseAndValidateBody(await req.json());
    } catch (err) {
      return new Response(JSON.stringify({ error: "messages required" }), {
        status: 400,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }
    const { mode, messages: cleaned } = parsed;

    // Trim history: keep last 20 messages for cost control
    const trimmed = cleaned.slice(-20);

    const systemPrompt = `${BASE_PERSONA}\n\n${MODE_PROMPTS[mode] ?? MODE_PROMPTS.F}`;

    const apiKey = Deno.env.get("LOVABLE_API_KEY");
    if (!apiKey) {
      return new Response(JSON.stringify({ error: "AI gateway not configured" }), {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const upstream = await fetch("https://ai.gateway.lovable.dev/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: "google/gemini-3-flash-preview",
        stream: true,
        messages: [{ role: "system", content: systemPrompt }, ...trimmed],
      }),
    });

    if (!upstream.ok) {
      const text = await upstream.text();
      const status = upstream.status === 429 || upstream.status === 402 ? upstream.status : 500;
      return new Response(JSON.stringify({ error: text || "AI gateway error" }), {
        status,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    return new Response(upstream.body, {
      headers: {
        ...corsHeaders,
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
      },
    });
  } catch (e) {
    return new Response(JSON.stringify({ error: (e as Error).message }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
