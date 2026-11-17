/**
 * ZYNX AGI Netlify Serverless API (Web Request/Response v2 handler)
 *
 * Serves:
 * - GET  /api/v1/health
 * - GET  /health
 * - POST /api/v1/chat/message
 * - POST /api/v1/cultural/analyze
 */

const PLACEHOLDER_KEYS = new Set([
  "",
  "your_ai_provider_api_key_here",
  "your_openai_api_key_here",
  "your_anthropic_api_key_here",
  "your_google_api_key_here",
  "changeme",
]);

const SUPPORTED_PROVIDERS = new Set(["openai", "anthropic", "google", "mock", "auto"]);

const POLITE_PARTICLES: Record<string, number> = {
  "ครับ": 1.0,
  "ค่ะ": 1.0,
  "ค่ะ/ครับ": 1.0,
  "ครับ/ค่ะ": 1.0,
  "ขอประทาน": 1.0,
  "กราบเรียน": 1.0,
  "กราบทูล": 1.0,
  "นะคะ": 0.8,
  "นะครับ": 0.8,
  "ขอโทษค่ะ": 0.8,
  "ขอโทษครับ": 0.8,
  "หรือคะ": 0.8,
  "หรือครับ": 0.8,
  "ไหมคะ": 0.8,
  "ไหมครับ": 0.8,
  "จ้ะ": 0.6,
  "จ้า": 0.6,
  "นะ": 0.5,
  "จ๋า": 0.4,
};

const CULTURAL_PATTERNS: Record<string, RegExp[]> = {
  kreng_jai: [/ไม่เป็นไร/, /ไม่ต้องกังวล/, /ไม่ต้องเกรงใจ/, /ไม่ต้องเป็นห่วง/],
  sanuk: [/สนุก/, /เฮฮา/, /รื่นเริง/, /มีความสุข/, /เพลิดเพลิน/],
  mai_pen_rai: [/ไม่เป็นไร/, /ช่างมัน/, /ไม่เป็นอะไร/],
  greng_jai: [/เกรงใจ/],
  jai_yen: [/ใจเย็น/],
  nam_jai: [/น้ำใจ/],
};

const FORMAL_INDICATORS = ["ดิฉัน", "กระผม", "ขออนุญาต", "กราบเรียน", "ขออภัย", "สวัสดีครับ", "สวัสดีค่ะ"];
const INFORMAL_INDICATORS = ["หวัดดี", "บอกเลย", "บอกมา", "บอกที"];

const CORE_ENGINE_STATUS = {
  intelligence: "ready",
  reasoning: "ready",
  strategy: "ready",
  evolution: "ready",
  chanont_theory: "specification_in_development",
} as const;

type ChatHistoryItem = {
  role: "user" | "assistant";
  content: string;
};

type ProviderConfiguration = {
  provider: "openai" | "anthropic" | "google" | "mock";
  model: string;
  configured: boolean;
  apiKey: string | null;
};

type AIResult = {
  message: string;
  provider: string;
  model: string;
  mode: "live" | "mock" | "fallback";
  isMock: boolean;
  usage: { prompt_tokens: number; completion_tokens: number; total_tokens: number } | null;
  error: string | null;
};

function getEnv(name: string): string | undefined {
  const netlifyGlobal = (
    globalThis as {
      Netlify?: { env?: { get?: (key: string) => string | undefined } };
    }
  ).Netlify;
  const fromNetlify = netlifyGlobal?.env?.get?.(name);
  if (typeof fromNetlify === "string") {
    return fromNetlify;
  }
  if (typeof process !== "undefined" && process.env) {
    return process.env[name];
  }
  return undefined;
}

function isValidSecret(value: string | undefined): value is string {
  if (!value) return false;
  const trimmed = value.trim();
  return Boolean(trimmed) && !PLACEHOLDER_KEYS.has(trimmed.toLowerCase());
}

function inferProvider(apiKey: string, model: string | undefined): "openai" | "anthropic" | "google" {
  if (model) {
    const lower = model.toLowerCase();
    if (lower.includes("claude")) return "anthropic";
    if (lower.includes("gemini")) return "google";
    if (lower.includes("gpt") || lower.startsWith("o1") || lower.startsWith("o3")) return "openai";
  }
  if (apiKey.startsWith("sk-ant-")) return "anthropic";
  if (apiKey.startsWith("AIza")) return "google";
  return "openai";
}

function defaultModelFor(provider: "openai" | "anthropic" | "google"): string {
  if (provider === "openai") return getEnv("OPENAI_MODEL")?.trim() || "gpt-4o-mini";
  if (provider === "anthropic") return getEnv("ANTHROPIC_MODEL")?.trim() || "claude-3-5-haiku-latest";
  return getEnv("GOOGLE_MODEL")?.trim() || "gemini-2.5-flash";
}

function keyForProvider(provider: "openai" | "anthropic" | "google"): string | null {
  const unified = getEnv("AI_API_KEY");
  if (isValidSecret(unified)) return unified.trim();

  if (provider === "openai") {
    const k = getEnv("OPENAI_API_KEY");
    return isValidSecret(k) ? k.trim() : null;
  }
  if (provider === "anthropic") {
    const k = getEnv("ANTHROPIC_API_KEY");
    return isValidSecret(k) ? k.trim() : null;
  }
  const googleKey = getEnv("GOOGLE_API_KEY") || getEnv("GEMINI_API_KEY");
  return isValidSecret(googleKey) ? googleKey.trim() : null;
}

function resolveProviderConfig(requestedModel?: string | null): ProviderConfiguration {
  let rawProvider = (getEnv("AI_PROVIDER") || "auto").trim().toLowerCase();
  if (!SUPPORTED_PROVIDERS.has(rawProvider)) {
    rawProvider = "auto";
  }

  if (rawProvider === "mock") {
    return { provider: "mock", model: "deeja-mock-v1", configured: false, apiKey: null };
  }

  const cleanRequested =
    requestedModel && !["auto", "deeja-v1"].includes(requestedModel.trim())
      ? requestedModel.trim()
      : undefined;
  const configuredModel = cleanRequested || getEnv("AI_MODEL")?.trim() || undefined;

  if (rawProvider === "openai" || rawProvider === "anthropic" || rawProvider === "google") {
    const apiKey = keyForProvider(rawProvider);
    if (!apiKey) {
      return { provider: "mock", model: "deeja-mock-v1", configured: false, apiKey: null };
    }
    return {
      provider: rawProvider,
      model: configuredModel || defaultModelFor(rawProvider),
      configured: true,
      apiKey,
    };
  }

  const unified = getEnv("AI_API_KEY");
  if (isValidSecret(unified)) {
    const inferred = inferProvider(unified.trim(), configuredModel);
    return {
      provider: inferred,
      model: configuredModel || defaultModelFor(inferred),
      configured: true,
      apiKey: unified.trim(),
    };
  }

  for (const candidate of ["openai", "anthropic", "google"] as const) {
    const apiKey = keyForProvider(candidate);
    if (apiKey) {
      return {
        provider: candidate,
        model: configuredModel || defaultModelFor(candidate),
        configured: true,
        apiKey,
      };
    }
  }

  return { provider: "mock", model: "deeja-mock-v1", configured: false, apiKey: null };
}

function analyzeMessageCulture(text: string) {
  const isThai = /[\u0E00-\u0E7F]/.test(text);
  const detectedParticles: string[] = [];
  let politenessScore = 0;

  for (const [particle, score] of Object.entries(POLITE_PARTICLES)) {
    if (text.includes(particle)) {
      detectedParticles.push(particle);
      politenessScore = Math.max(politenessScore, score);
    }
  }

  let formalityScore = 0;
  for (const token of FORMAL_INDICATORS) {
    if (text.includes(token)) formalityScore += 0.25;
  }
  for (const token of INFORMAL_INDICATORS) {
    if (text.includes(token)) formalityScore -= 0.2;
  }
  formalityScore = Math.max(0, Math.min(1, formalityScore));

  const detectedPatterns: string[] = [];
  for (const [name, regexList] of Object.entries(CULTURAL_PATTERNS)) {
    if (regexList.some((re) => re.test(text))) {
      detectedPatterns.push(name);
    }
  }

  const formalityLevel =
    formalityScore >= 0.7
      ? "formal"
      : formalityScore >= 0.4 || detectedParticles.length > 0
        ? "semi-formal"
        : "casual";

  const communicationStyle = isThai
    ? detectedParticles.length > 0
      ? "polite_thai"
      : "helpful_thai"
    : "helpful_international";

  return {
    isThai,
    culturalContext: {
      primaryCulture: isThai ? "thai" : "international",
      language: isThai ? "th-TH" : "en-US",
      formalityLevel,
      formalityScore: Number(formalityScore.toFixed(3)),
      politenessLevel: Number(politenessScore.toFixed(3)),
      culturalMarkers: detectedParticles.length > 0 ? detectedParticles : detectedPatterns,
      culturalPatterns: detectedPatterns,
      communicationStyle,
    },
  };
}

function buildSystemPrompt(culturalContext: Record<string, unknown>): string {
  return (
    "You are Deeja (ดีจ้า), the cultural-aware AI assistant of ZYNX AGI. " +
    "Respond helpfully, accurately, and concisely in the user's language (Thai or English). " +
    `Detected cultural context: primaryCulture=${String(culturalContext.primaryCulture)}, ` +
    `formality=${String(culturalContext.formalityLevel)}, style=${String(culturalContext.communicationStyle)}.`
  );
}

function normalizeHistory(rawHistory: unknown): ChatHistoryItem[] {
  if (!Array.isArray(rawHistory)) return [];
  const items: ChatHistoryItem[] = [];
  for (const entry of rawHistory.slice(-10)) {
    if (!entry || typeof entry !== "object") continue;
    const rec = entry as Record<string, unknown>;
    if (
      (rec.role === "user" || rec.role === "assistant") &&
      typeof rec.content === "string" &&
      rec.content.trim()
    ) {
      items.push({ role: rec.role, content: rec.content.trim().slice(0, 4000) });
    }
  }
  return items;
}

function buildMockResult(
  message: string,
  isThai: boolean,
  mode: "mock" | "fallback",
  provider = "mock",
  model = "deeja-mock-v1",
  error: string | null = null
): AIResult {
  const lower = message.toLowerCase();
  const isGreeting =
    message.includes("สวัสดี") ||
    lower
      .split(/\s+/)
      .some((word) => word === "hello" || word === "hi" || word === "hey");

  const prefixTh =
    mode === "fallback"
      ? "[โหมดสำรอง — ผู้ให้บริการ AI หลักไม่พร้อมใช้งานชั่วคราว] "
      : "[Mock Mode — ยังไม่ได้ตั้งค่า AI API Key บน Backend] ";
  const prefixEn =
    mode === "fallback"
      ? "[Fallback Mode — upstream AI provider temporarily unavailable] "
      : "[Mock Mode — no live AI provider API key configured on backend] ";

  let body: string;
  if (isThai) {
    body = isGreeting
      ? "สวัสดีค่ะ! ฉันคือ Deeja บนระบบ ZynxAGI 🌟 ขณะนี้ระบบกำลังตอบกลับจากโหมดจำลอง (Mock/Fallback) โดยวิเคราะห์บริบทภาษาไทยและระดับความสุภาพให้เรียบร้อยแล้วค่ะ"
      : `ได้รับข้อความของคุณแล้วค่ะ: "${message}" เมื่อตั้งค่า AI_API_KEY (หรือ OPENAI_API_KEY / ANTHROPIC_API_KEY / GOOGLE_API_KEY) ใน Netlify Environment Variables แล้ว ข้อความนี้จะถูกประมวลผลด้วยโมเดล AI จริงค่ะ`;
  } else {
    body = isGreeting
      ? "Hello! I'm Deeja on ZynxAGI 🌟 The backend is responding in mock/fallback mode with cultural context analysis active."
      : `Received your message: "${message}". Configure AI_API_KEY (or OPENAI_API_KEY / ANTHROPIC_API_KEY / GOOGLE_API_KEY) in Netlify Environment Variables to enable live AI generation.`;
  }

  return {
    message: `${isThai ? prefixTh : prefixEn}${body}`,
    provider,
    model,
    mode,
    isMock: true,
    usage: null,
    error,
  };
}

async function callUpstreamAI(
  config: ProviderConfiguration,
  systemPrompt: string,
  history: ChatHistoryItem[],
  message: string
): Promise<AIResult> {
  if (!config.configured || !config.apiKey || config.provider === "mock") {
    throw new Error("No AI provider configured");
  }

  const timeoutMs = Number(getEnv("AI_REQUEST_TIMEOUT") || "20") * 1000;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), Number.isFinite(timeoutMs) ? timeoutMs : 20000);

  try {
    if (config.provider === "openai") {
      const base = (getEnv("OPENAI_BASE_URL") || "https://api.openai.com/v1").replace(/\/+$/, "");
      const endpoint = base.endsWith("/v1") ? `${base}/chat/completions` : `${base}/v1/chat/completions`;
      const res = await fetch(endpoint, {
        method: "POST",
        signal: controller.signal,
        headers: {
          Authorization: `Bearer ${config.apiKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: config.model,
          messages: [{ role: "system", content: systemPrompt }, ...history, { role: "user", content: message }],
          max_tokens: 1000,
          temperature: 0.7,
        }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const payload = (await res.json()) as {
        choices?: Array<{ message?: { content?: string } }>;
        usage?: { prompt_tokens?: number; completion_tokens?: number; total_tokens?: number };
      };
      const text = payload.choices?.[0]?.message?.content?.trim();
      if (!text) throw new Error("Empty response from OpenAI");
      return {
        message: text,
        provider: "openai",
        model: config.model,
        mode: "live",
        isMock: false,
        usage: payload.usage
          ? {
              prompt_tokens: Number(payload.usage.prompt_tokens || 0),
              completion_tokens: Number(payload.usage.completion_tokens || 0),
              total_tokens: Number(payload.usage.total_tokens || 0),
            }
          : null,
        error: null,
      };
    }

    if (config.provider === "anthropic") {
      const base = (getEnv("ANTHROPIC_BASE_URL") || "https://api.anthropic.com").replace(/\/+$/, "");
      const endpoint = base.endsWith("/v1") ? `${base}/messages` : `${base}/v1/messages`;
      const res = await fetch(endpoint, {
        method: "POST",
        signal: controller.signal,
        headers: {
          "x-api-key": config.apiKey,
          "anthropic-version": "2023-06-01",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: config.model,
          max_tokens: 1000,
          temperature: 0.7,
          system: systemPrompt,
          messages: [...history, { role: "user", content: message }],
        }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const payload = (await res.json()) as {
        content?: Array<{ type?: string; text?: string }>;
        usage?: { input_tokens?: number; output_tokens?: number };
      };
      const text = (payload.content || [])
        .filter((b) => b.type === "text" && typeof b.text === "string")
        .map((b) => b.text)
        .join("\n")
        .trim();
      if (!text) throw new Error("Empty response from Anthropic");
      const inTok = Number(payload.usage?.input_tokens || 0);
      const outTok = Number(payload.usage?.output_tokens || 0);
      return {
        message: text,
        provider: "anthropic",
        model: config.model,
        mode: "live",
        isMock: false,
        usage: payload.usage
          ? { prompt_tokens: inTok, completion_tokens: outTok, total_tokens: inTok + outTok }
          : null,
        error: null,
      };
    }

    // Google Gemini
    const base = (
      getEnv("GOOGLE_GEMINI_BASE_URL") || "https://generativelanguage.googleapis.com"
    ).replace(/\/+$/, "");
    const versionPrefix = base.endsWith("/v1beta") ? base : `${base}/v1beta`;
    const endpoint = `${versionPrefix}/models/${encodeURIComponent(config.model)}:generateContent`;
    const contents = [
      ...history.map((item) => ({
        role: item.role === "assistant" ? "model" : "user",
        parts: [{ text: item.content }],
      })),
      { role: "user", parts: [{ text: message }] },
    ];
    const res = await fetch(endpoint, {
      method: "POST",
      signal: controller.signal,
      headers: {
        "x-goog-api-key": config.apiKey,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        systemInstruction: { parts: [{ text: systemPrompt }] },
        contents,
      }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const payload = (await res.json()) as {
      candidates?: Array<{ content?: { parts?: Array<{ text?: string }> } }>;
      usageMetadata?: {
        promptTokenCount?: number;
        candidatesTokenCount?: number;
        totalTokenCount?: number;
      };
    };
    const parts = payload.candidates?.[0]?.content?.parts || [];
    const text = parts
      .map((p) => (typeof p.text === "string" ? p.text : ""))
      .join("")
      .trim();
    if (!text) throw new Error("Empty response from Google Gemini");
    const promptTok = Number(payload.usageMetadata?.promptTokenCount || 0);
    const compTok = Number(payload.usageMetadata?.candidatesTokenCount || 0);
    return {
      message: text,
      provider: "google",
      model: config.model,
      mode: "live",
      isMock: false,
      usage: payload.usageMetadata
        ? {
            prompt_tokens: promptTok,
            completion_tokens: compTok,
            total_tokens: Number(payload.usageMetadata.totalTokenCount || promptTok + compTok),
          }
        : null,
      error: null,
    };
  } finally {
    clearTimeout(timer);
  }
}

export default async function handler(req: Request): Promise<Response> {
  const url = new URL(req.url);
  const path = url.pathname.replace(/\/+$/, "") || "/";

  if (req.method === "GET" && (path === "/api/v1/health" || path === "/health")) {
    const providerCfg = resolveProviderConfig();
    return Response.json({
      status: "healthy",
      app: "ZynxAGI",
      version: "1.0.0",
      runtime: "netlify-functions",
      mode: providerCfg.configured ? "live" : "mock",
      ai_provider: {
        provider: providerCfg.provider,
        model: providerCfg.model,
        configured: providerCfg.configured,
      },
      components: {
        api: "healthy",
        cultural_intelligence: "ready",
        ai_gateway: providerCfg.configured ? "live" : "mock_mode",
      },
      core_engines: CORE_ENGINE_STATUS,
      message: "ZynxAGI is running successfully!",
      thai_message: "ระบบ ZynxAGI ทำงานปกติค่ะ!",
    });
  }

  if (req.method === "POST" && path === "/api/v1/cultural/analyze") {
    let body: Record<string, unknown>;
    try {
      body = (await req.json()) as Record<string, unknown>;
    } catch {
      return Response.json({ detail: "Invalid JSON payload" }, { status: 422 });
    }
    const rawText = typeof body?.text === "string" ? body.text.trim() : "";
    if (!rawText || rawText.length > 4000) {
      return Response.json(
        { detail: "text must be a non-empty string up to 4000 characters" },
        { status: 422 }
      );
    }
    const { isThai, culturalContext } = analyzeMessageCulture(rawText);
    return Response.json({ ...culturalContext, isThai });
  }

  if (req.method === "POST" && path === "/api/v1/chat/message") {
    const startMs = Date.now();
    let body: Record<string, unknown>;
    try {
      body = (await req.json()) as Record<string, unknown>;
    } catch {
      return Response.json({ detail: "Invalid JSON payload" }, { status: 422 });
    }

    const rawMessage = typeof body?.message === "string" ? body.message.trim() : "";
    if (!rawMessage || rawMessage.length > 4000) {
      return Response.json(
        { detail: "message must be a non-empty string up to 4000 characters" },
        { status: 422 }
      );
    }

    const requestedModel = typeof body?.model === "string" ? body.model : null;
    const history = normalizeHistory(body?.conversation_history);
    const { isThai, culturalContext } = analyzeMessageCulture(rawMessage);
    const providerCfg = resolveProviderConfig(requestedModel);

    let aiResult: AIResult;
    if (!providerCfg.configured || !providerCfg.apiKey) {
      aiResult = buildMockResult(rawMessage, isThai, "mock");
    } else {
      try {
        aiResult = await callUpstreamAI(
          providerCfg,
          buildSystemPrompt(culturalContext),
          history,
          rawMessage
        );
      } catch (err) {
        const reason = err instanceof Error ? err.message : "Upstream error";
        aiResult = buildMockResult(
          rawMessage,
          isThai,
          "fallback",
          providerCfg.provider,
          providerCfg.model,
          `Upstream AI provider unavailable (${reason})`
        );
      }
    }

    const processingTime = Number(((Date.now() - startMs) / 1000).toFixed(4));
    return Response.json({
      message: aiResult.message,
      aiPlatform: aiResult.provider,
      model: aiResult.model,
      mode: aiResult.mode,
      isMock: aiResult.isMock,
      providerError: aiResult.error,
      culturalContext,
      processingTime,
      coreEngines: CORE_ENGINE_STATUS,
      usage: aiResult.usage,
    });
  }

  return Response.json({ detail: "Not Found" }, { status: 404 });
}

export const config = {
  path: [
    "/api/v1/health",
    "/health",
    "/api/v1/chat/message",
    "/api/v1/cultural/analyze",
  ],
};
