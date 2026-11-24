import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Send, Trash2, Moon, Sun } from "lucide-react";
import deejaLogo from "@/assets/deeja-logo.png";
import deejaAvatar from "@/assets/deeja-avatar.png";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";

type Role = "user" | "assistant";
interface Message {
  id: string;
  role: Role;
  content: string;
}

const MODES = [
  { value: "P", label: "P · Prompt Engineer", tag: "Optimize prompts" },
  { value: "T", label: "T · Teach", tag: "Learn step-by-step" },
  { value: "E", label: "E · Explore", tag: "Brainstorm ideas" },
  { value: "F", label: "F · Focus", tag: "Sharp & concise" },
  { value: "R", label: "R · Reflect", tag: "Deeper thinking" },
];

const STARTERS: Record<string, string[]> = {
  P: [
    "ปรับ prompt นี้ให้ได้ output 10/10: 'เขียนโพสต์ขายของ'",
    "สร้าง prompt สำหรับวิเคราะห์คู่แข่งทางธุรกิจ",
    "ออกแบบ prompt ให้ AI สอนเขียนโค้ดแบบมืออาชีพ",
    "ทำ prompt template สำหรับ content marketing",
  ],
  T: [
    "อธิบาย quantum entanglement แบบเข้าใจง่าย",
    "สอนใช้ React hooks ตั้งแต่เริ่มต้น",
    "TypeScript generics ทำงานยังไง?",
    "อธิบาย RAG ในระบบ AI แบบสั้นๆ",
  ],
  E: [
    "ไอเดียโปรเจกต์ AI สำหรับสุดสัปดาห์",
    "Brainstorm ชื่อแบรนด์สำหรับ AI startup",
    "เสนอ 5 มุมมองใหม่ของการใช้ LLM",
    "ไอเดีย side project ที่ทำเงินได้",
  ],
  F: [
    "สรุปข้อดี-ข้อเสียของ Vercel vs Netlify",
    "เขียน follow-up email สั้นๆ ให้สุภาพ",
    "List 5 ข้อในการ optimize React app",
    "Action plan 1 สัปดาห์เพิ่ม productivity",
  ],
  R: [
    "ฉันควรเปลี่ยนงานหรือไม่? ช่วยถามคำถามสะท้อนคิด",
    "วิเคราะห์ pattern ความล้มเหลวที่ผ่านมา",
    "ช่วยวางเป้าหมายชีวิต 5 ปีข้างหน้า",
    "สะท้อนสิ่งที่เรียนรู้จากสัปดาห์นี้",
  ],
};

const FOLLOWUPS = [
  "ขยายความให้ลึกขึ้น",
  "ยกตัวอย่างประกอบ",
  "ทำเป็น checklist ใช้ได้จริง",
  "เปรียบเทียบทางเลือกอื่น",
];

const FN_URL = `/functions/v1/chat`;
const LANDING_URL = "https://deeja-landing.vercel.app";

const ChatBubble = ({ m, streaming }: { m: Message; streaming?: boolean }) => {
  const isUser = m.role === "user";
  return (
    <div className={`fade-in flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] rounded-3xl px-5 py-3 shadow-soft ${
          isUser
            ? "bg-[hsl(var(--bubble-user))] text-[hsl(var(--bubble-user-foreground))] rounded-br-md"
            : "bg-[hsl(var(--bubble-assistant))] text-[hsl(var(--bubble-assistant-foreground))] rounded-bl-md border"
        }`}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap leading-relaxed">{m.content}</p>
        ) : (
          <div
            className={`prose prose-sm dark:prose-invert max-w-none prose-pre:bg-secondary prose-pre:text-foreground prose-code:before:hidden prose-code:after:hidden ${
              streaming && !m.content ? "blink-caret" : ""
            } ${streaming ? "after:content-['▍'] after:ml-0.5 after:animate-pulse" : ""}`}
          >
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {m.content || "…"}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
};

const Index = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [mode, setMode] = useState("P");
  const [streaming, setStreaming] = useState(false);
  const [dark, setDark] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    const prefers = window.matchMedia("(prefers-color-scheme: dark)").matches;
    setDark(prefers);
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  const send = async () => {
    const text = input.trim();
    if (!text || streaming) return;
    if (text.length > 4000) {
      toast.error("Message too long (max 4000 chars).");
      return;
    }

    const userMsg: Message = { id: crypto.randomUUID(), role: "user", content: text };
    const assistantMsg: Message = { id: crypto.randomUUID(), role: "assistant", content: "" };
    const next = [...messages, userMsg];
    setMessages([...next, assistantMsg]);
    setInput("");
    setStreaming(true);

    const ctrl = new AbortController();
    abortRef.current = ctrl;

    try {
      const resp = await fetch(FN_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          mode,
          messages: next.map(({ role, content }) => ({ role, content })),
        }),
        signal: ctrl.signal,
      });

      if (!resp.ok) {
        if (resp.status === 429) toast.error("Rate limit reached. Please wait a moment.");
        else if (resp.status === 402) toast.error("AI credits exhausted. Add credits in workspace settings.");
        else toast.error("Something went wrong.");
        setMessages((m) => m.filter((x) => x.id !== assistantMsg.id));
        return;
      }

      const reader = resp.body!.getReader();
      const decoder = new TextDecoder();
      let buf = "";
      let acc = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true });
        const lines = buf.split("\n");
        buf = lines.pop() || "";
        for (const line of lines) {
          const t = line.trim();
          if (!t.startsWith("data:")) continue;
          const data = t.slice(5).trim();
          if (data === "[DONE]") continue;
          try {
            const json = JSON.parse(data);
            const delta = json.choices?.[0]?.delta?.content;
            if (delta) {
              acc += delta;
              setMessages((m) =>
                m.map((x) => (x.id === assistantMsg.id ? { ...x, content: acc } : x))
              );
            }
          } catch {
            /* ignore */
          }
        }
      }
    } catch (e: any) {
      if (e.name !== "AbortError") toast.error("Connection error.");
      setMessages((m) => m.filter((x) => x.id !== assistantMsg.id || x.content));
    } finally {
      setStreaming(false);
      abortRef.current = null;
    }
  };

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  const clearChat = () => {
    if (!window.confirm("ลบแชตทั้งหมดใช่ไหม?")) return;
    abortRef.current?.abort();
    setMessages([]);
  };

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b bg-background/60 backdrop-blur-xl sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center gap-3">
          <div className="ring-gradient-persona shadow-persona">
            <img src={deejaLogo} alt="Deeja logo" className="h-9 w-9 rounded-full bg-background object-cover" />
          </div>
          <div className="flex-1">
            <h1 className="text-lg font-semibold tracking-tight">
              <span className="text-gradient-persona">Deeja</span>{" "}
              <span className="text-gradient-brand">v2.0</span>
            </h1>
            <p className="text-xs text-muted-foreground -mt-0.5">AI Prompt Engineer · Guided Experience</p>
          </div>
          <Select value={mode} onValueChange={setMode}>
            <SelectTrigger className="w-[200px] rounded-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {MODES.map((m) => (
                <SelectItem key={m.value} value={m.value}>
                  <div className="flex flex-col">
                    <span>{m.label}</span>
                    <span className="text-xs text-muted-foreground">{m.tag}</span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <a
            href={LANDING_URL}
            className="hidden sm:inline-flex h-9 items-center rounded-full border bg-card px-3 text-xs font-medium text-muted-foreground transition hover:border-primary/40 hover:text-foreground"
          >
            Back to Deeja Landing
          </a>
          <div className="flex items-center gap-1 rounded-full border px-1.5 py-1 bg-card">
          <Button variant="ghost" size="icon" onClick={() => setDark((d) => !d)} aria-label="Toggle theme">
            {dark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </Button>
          </div>
          <div className="flex items-center gap-1 rounded-full border border-destructive/30 px-1.5 py-1 bg-card">
          <Button variant="ghost" size="icon" onClick={clearChat} aria-label="Clear chat">
            <Trash2 className="h-4 w-4" />
          </Button>
          </div>
        </div>
      </header>

      <main ref={scrollRef} className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-4 py-4 lg:py-6 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center py-6 lg:py-8 fade-in">
              <div className="inline-block ring-gradient-persona shadow-persona mb-5">
                <img src={deejaAvatar} alt="Deeja avatar" className="h-20 w-20 rounded-full bg-background object-cover" />
              </div>
              <h2 className="text-3xl lg:text-4xl font-semibold tracking-tight mb-2">
                สวัสดี, ฉันคือ <span className="text-gradient-persona">Deeja</span>
              </h2>
              <p className="text-muted-foreground max-w-lg mx-auto">
                AI Prompt Engineer ที่ช่วยคุณออกแบบ prompt ให้ได้ผลลัพธ์ 10/10 — เลือกโหมดแล้วเริ่มต้นด้วย template ด้านล่างได้เลย
              </p>
              <p className="text-xs text-muted-foreground mt-3">
                1) เลือกโหมด 2) เลือกเทมเพลต 3) กดส่ง
              </p>

              <div className="flex flex-wrap justify-center gap-2 mt-6">
                {MODES.map((m) => (
                  <button
                    key={m.value}
                    onClick={() => setMode(m.value)}
                    className={`text-xs px-3 py-1.5 rounded-full border transition ${
                      mode === m.value
                        ? "bg-gradient-brand text-white border-transparent shadow-glow"
                        : "bg-card hover:border-primary/40"
                    }`}
                  >
                    {m.label}
                  </button>
                ))}
              </div>

              <div className="max-w-3xl mx-auto mt-5 mb-4">
                <div className="flex items-end gap-2 rounded-3xl border bg-card p-2 shadow-soft focus-within:shadow-glow transition-shadow">
                  <Textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={onKeyDown}
                    placeholder={`พิมพ์ข้อความหา Deeja ในโหมด ${mode}...`}
                    rows={1}
                    className="min-h-[44px] max-h-40 resize-none border-0 focus-visible:ring-0 bg-transparent"
                  />
                  <Button
                    onClick={send}
                    disabled={!input.trim() || streaming}
                    size="icon"
                    className="rounded-full bg-gradient-persona hover:opacity-90 shadow-persona h-10 w-10 shrink-0 text-white"
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              <div className="grid sm:grid-cols-2 gap-3 mt-4 max-w-3xl mx-auto text-left">
                {(STARTERS[mode] ?? STARTERS.P).map((s) => (
                  <button
                    key={s}
                    onClick={() => setInput(s)}
                    className="group text-sm rounded-2xl border bg-card hover:shadow-soft hover:border-primary/40 transition px-4 py-3 text-card-foreground cursor-pointer"
                  >
                    <span className="text-xs text-gradient-persona font-medium block mb-1 group-hover:underline">
                      ▸ เทมเพลตพร้อมใช้
                    </span>
                    {s}
                    <span className="block text-[11px] text-muted-foreground mt-2">คลิกเพื่อใส่ในช่องข้อความ</span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((m, i) => (
                <ChatBubble
                  key={m.id}
                  m={m}
                  streaming={streaming && i === messages.length - 1 && m.role === "assistant"}
                />
              ))}
              {!streaming && messages.length > 0 && messages[messages.length - 1].role === "assistant" && (
                <div className="fade-in pt-2">
                  <p className="text-xs text-muted-foreground mb-2">✨ Smart Assist · ลองถามต่อ:</p>
                  <div className="flex flex-wrap gap-2">
                    {FOLLOWUPS.map((f) => (
                      <button
                        key={f}
                        onClick={() => setInput(f)}
                        className="text-xs px-3 py-1.5 rounded-full border bg-card hover:border-primary/40 hover:shadow-soft transition"
                      >
                        {f}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </main>

      <footer className="border-t bg-background/60 backdrop-blur-xl sticky bottom-0">
        <div className="max-w-3xl mx-auto px-4 py-4">
          <div className="flex items-end gap-2 rounded-3xl border bg-card p-2 shadow-soft focus-within:shadow-glow transition-shadow">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={onKeyDown}
              placeholder={`Message Deeja in ${mode} mode…`}
              rows={1}
              className="min-h-[44px] max-h-40 resize-none border-0 focus-visible:ring-0 bg-transparent"
            />
            <Button
              onClick={send}
              disabled={!input.trim() || streaming}
              size="icon"
              className="rounded-full bg-gradient-persona hover:opacity-90 shadow-persona h-10 w-10 shrink-0 text-white"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
          <p className="text-xs text-muted-foreground text-center mt-2">
            Enter to send · Shift+Enter for newline · Mode <span className="text-gradient-persona font-semibold">{mode}</span>
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
