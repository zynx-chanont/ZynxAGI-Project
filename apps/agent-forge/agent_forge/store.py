from __future__ import annotations
import json, os, sqlite3, uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

class Store:
    def __init__(self, path: str | None = None):
        self.path = path or os.getenv("AGENT_FORGE_DB", "./agent-forge.db")
        Path(self.path).parent.mkdir(parents=True, exist_ok=True) if self.path != ":memory:" else None
        self._init()

    def connect(self):
        db = sqlite3.connect(self.path, timeout=15)
        db.row_factory = sqlite3.Row
        return db

    def _init(self):
        with self.connect() as db:
            db.executescript("""
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS projects(id TEXT PRIMARY KEY,name TEXT NOT NULL,context TEXT NOT NULL DEFAULT '{}',created_at TEXT NOT NULL,updated_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY,project_id TEXT NOT NULL,task TEXT NOT NULL,agent_id TEXT NOT NULL,status TEXT NOT NULL,result TEXT NOT NULL DEFAULT '{}',error TEXT,created_at TEXT NOT NULL,updated_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS approvals(id TEXT PRIMARY KEY,run_id TEXT NOT NULL,action TEXT NOT NULL,payload TEXT NOT NULL,status TEXT NOT NULL,requested_by TEXT NOT NULL,reviewed_by TEXT,created_at TEXT NOT NULL,updated_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY AUTOINCREMENT,event_id TEXT UNIQUE NOT NULL,actor TEXT NOT NULL,action TEXT NOT NULL,resource TEXT NOT NULL,payload TEXT NOT NULL,previous_hash TEXT NOT NULL,event_hash TEXT NOT NULL,created_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS memories(id TEXT PRIMARY KEY,project_id TEXT NOT NULL,kind TEXT NOT NULL,content TEXT NOT NULL,metadata TEXT NOT NULL,created_at TEXT NOT NULL);
            """)

    def audit(self, actor: str, action: str, resource: str, payload: dict[str, Any]):
        import hashlib
        with self.connect() as db:
            row = db.execute("SELECT event_hash FROM audit ORDER BY id DESC LIMIT 1").fetchone()
            previous = row["event_hash"] if row else "GENESIS"
            created = now()
            event = {"event_id":str(uuid.uuid4()),"actor":actor,"action":action,"resource":resource,"payload":payload,"previous_hash":previous,"created_at":created}
            digest = hashlib.sha256(json.dumps(event,sort_keys=True,separators=(",",":")).encode()).hexdigest()
            db.execute("INSERT INTO audit(event_id,actor,action,resource,payload,previous_hash,event_hash,created_at) VALUES(?,?,?,?,?,?,?,?)",
                (event["event_id"],actor,action,resource,json.dumps(payload),previous,digest,created))
            return {**event,"event_hash":digest}

    def create_project(self,name:str,context:dict):
        pid=str(uuid.uuid4()); stamp=now()
        with self.connect() as db:
            db.execute("INSERT INTO projects VALUES(?,?,?,?,?)",(pid,name,json.dumps(context),stamp,stamp))
        self.audit("system","project.created",pid,{"name":name})
        return self.get_project(pid)

    def get_project(self,pid:str):
        with self.connect() as db: row=db.execute("SELECT * FROM projects WHERE id=?",(pid,)).fetchone()
        return dict(row) | {"context":json.loads(row["context"])} if row else None

    def list_projects(self):
        with self.connect() as db: rows=db.execute("SELECT * FROM projects ORDER BY updated_at DESC").fetchall()
        return [dict(r)|{"context":json.loads(r["context"])} for r in rows]

    def update_context(self,pid:str,context:dict):
        with self.connect() as db:
            db.execute("UPDATE projects SET context=?,updated_at=? WHERE id=?",(json.dumps(context),now(),pid))
        self.audit("user","project.context.updated",pid,{"keys":list(context.keys())})
        return self.get_project(pid)

    def create_run(self,pid:str,task:str,agent_id:str):
        rid=str(uuid.uuid4()); stamp=now()
        with self.connect() as db:
            db.execute("INSERT INTO runs VALUES(?,?,?,?,?,?,?,?,?)",(rid,pid,task,agent_id,"queued","{}",None,stamp,stamp))
        self.audit("orchestrator","run.created",rid,{"project_id":pid,"agent_id":agent_id})
        return self.get_run(rid)

    def set_run(self,rid:str,status:str,result:dict|None=None,error:str|None=None):
        with self.connect() as db:
            db.execute("UPDATE runs SET status=?,result=?,error=?,updated_at=? WHERE id=?",(status,json.dumps(result or {}),error,now(),rid))
        self.audit("orchestrator","run."+status,rid,{"error":error} if error else {})
        return self.get_run(rid)

    def get_run(self,rid:str):
        with self.connect() as db: row=db.execute("SELECT * FROM runs WHERE id=?",(rid,)).fetchone()
        return dict(row)|{"result":json.loads(row["result"])} if row else None

    def list_runs(self,limit:int=50):
        with self.connect() as db: rows=db.execute("SELECT * FROM runs ORDER BY created_at DESC LIMIT ?",(limit,)).fetchall()
        return [dict(r)|{"result":json.loads(r["result"])} for r in rows]

    def request_approval(self,rid:str,action:str,payload:dict,actor:str):
        aid=str(uuid.uuid4()); stamp=now()
        with self.connect() as db:
            db.execute("INSERT INTO approvals VALUES(?,?,?,?,?,?,?,?,?)",(aid,rid,action,json.dumps(payload),"pending",actor,None,stamp,stamp))
        self.audit(actor,"approval.requested",aid,{"run_id":rid,"action":action})
        return self.get_approval(aid)

    def get_approval(self,aid:str):
        with self.connect() as db: row=db.execute("SELECT * FROM approvals WHERE id=?",(aid,)).fetchone()
        return dict(row)|{"payload":json.loads(row["payload"])} if row else None

    def list_approvals(self):
        with self.connect() as db: rows=db.execute("SELECT * FROM approvals ORDER BY created_at DESC").fetchall()
        return [dict(r)|{"payload":json.loads(r["payload"])} for r in rows]

    def decide_approval(self,aid:str,decision:str,reviewer:str):
        if decision not in {"approved","rejected"}: raise ValueError("decision must be approved or rejected")
        with self.connect() as db:
            row=db.execute("SELECT status FROM approvals WHERE id=?",(aid,)).fetchone()
            if not row: return None
            if row["status"]!="pending": raise ValueError("approval is already decided")
            db.execute("UPDATE approvals SET status=?,reviewed_by=?,updated_at=? WHERE id=?",(decision,reviewer,now(),aid))
        self.audit(reviewer,"approval."+decision,aid,{})
        return self.get_approval(aid)

    def add_memory(self,pid:str,kind:str,content:str,metadata:dict):
        mid=str(uuid.uuid4())
        with self.connect() as db:
            db.execute("INSERT INTO memories VALUES(?,?,?,?,?,?)",(mid,pid,kind,content,json.dumps(metadata),now()))
        self.audit("agent","memory.created",mid,{"project_id":pid,"kind":kind})
        return {"id":mid,"project_id":pid,"kind":kind,"content":content,"metadata":metadata}

    def search_memory(self,pid:str,q:str,limit:int=10):
        with self.connect() as db:
            rows=db.execute("SELECT * FROM memories WHERE project_id=? AND content LIKE ? ORDER BY created_at DESC LIMIT ?",(pid,f"%{q}%",limit)).fetchall()
        return [dict(r)|{"metadata":json.loads(r["metadata"])} for r in rows]

    def list_audit(self,limit:int=100):
        with self.connect() as db: rows=db.execute("SELECT * FROM audit ORDER BY id DESC LIMIT ?",(limit,)).fetchall()
        return [dict(r)|{"payload":json.loads(r["payload"])} for r in rows]
