from __future__ import annotations
import os
import httpx

class ModelRouter:
    """Minimal provider router. Keys are read only from environment variables."""
    async def generate(self, prompt: str, provider: str | None = None) -> dict:
        provider=(provider or os.getenv("DEFAULT_MODEL_PROVIDER","openai")).lower()
        timeout=httpx.Timeout(60)
        async with httpx.AsyncClient(timeout=timeout) as client:
            if provider=="openai":
                key=os.getenv("OPENAI_API_KEY"); model=os.getenv("OPENAI_MODEL","gpt-4o-mini")
                if not key: return {"provider":provider,"model":model,"status":"unconfigured"}
                r=await client.post("https://api.openai.com/v1/chat/completions",headers={"Authorization":f"Bearer {key}"},json={"model":model,"messages":[{"role":"user","content":prompt}]})
                r.raise_for_status(); data=r.json()
                return {"provider":provider,"model":model,"text":data["choices"][0]["message"]["content"],"usage":data.get("usage",{})}
            if provider=="anthropic":
                key=os.getenv("ANTHROPIC_API_KEY"); model=os.getenv("ANTHROPIC_MODEL","claude-3-5-haiku-latest")
                if not key: return {"provider":provider,"model":model,"status":"unconfigured"}
                r=await client.post("https://api.anthropic.com/v1/messages",headers={"x-api-key":key,"anthropic-version":"2023-06-01"},json={"model":model,"max_tokens":1200,"messages":[{"role":"user","content":prompt}]})
                r.raise_for_status(); data=r.json()
                return {"provider":provider,"model":model,"text":"".join(x.get("text","") for x in data.get("content",[])),"usage":data.get("usage",{})}
            if provider=="google":
                key=os.getenv("GOOGLE_API_KEY"); model=os.getenv("GOOGLE_MODEL","gemini-2.0-flash")
                if not key: return {"provider":provider,"model":model,"status":"unconfigured"}
                r=await client.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",json={"contents":[{"parts":[{"text":prompt}]}]})
                r.raise_for_status(); data=r.json()
                return {"provider":provider,"model":model,"text":data["candidates"][0]["content"]["parts"][0]["text"],"usage":data.get("usageMetadata",{})}
            if provider=="local":
                base=os.getenv("LOCAL_LLM_BASE_URL"); model=os.getenv("LOCAL_LLM_MODEL","local-model")
                if not base: return {"provider":provider,"model":model,"status":"unconfigured"}
                r=await client.post(base.rstrip("/")+"/v1/chat/completions",json={"model":model,"messages":[{"role":"user","content":prompt}]})
                r.raise_for_status(); data=r.json()
                return {"provider":provider,"model":model,"text":data["choices"][0]["message"]["content"],"usage":data.get("usage",{})}
        raise ValueError(f"Unsupported provider: {provider}")
