#!/usr/bin/env python3
"""Read-only localhost dashboard for CyberLab. Standard library only."""
from __future__ import annotations
import json,re,subprocess
from datetime import datetime,timezone
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
HOST="127.0.0.1";PORT=8765;DASHBOARD_DIR=Path(__file__).resolve().parent;REPO_ROOT=DASHBOARD_DIR.parent
PHASES=[(1,"Linux Fundamentals","01-linux-fundamentals"),(2,"Networking Fundamentals","02-network-fundamentals"),(3,"Python Network Programming","03-python-networking"),(4,"Reconnaissance & Enumeration","04-reconnaissance"),(5,"Web Application Security","05-web-security"),(6,"Authentication & Cryptography","07-cryptography"),(7,"Wireless / IEEE 802.11","06-wireless-security"),(8,"CTF & Controlled Exploitation","09-ctf"),(9,"Forensics","08-forensics"),(10,"Detection & Defensive Security","10-defensive-security")]
LAB_RE=re.compile(r"^lab-(\d+)(?:-(.*))?$",re.I);VERIFIED_RE=re.compile(r"\bVERIFIED\b",re.I)
def git(*args):
    try:return subprocess.run(["git","-C",str(REPO_ROOT),*args],capture_output=True,text=True,timeout=3,check=False).stdout.strip()
    except (OSError,subprocess.SubprocessError):return ""
def read(path):
    try:return path.read_text(encoding="utf-8",errors="replace")
    except OSError:return ""
def verified(path):return len(VERIFIED_RE.findall(read(path))) if path.exists() else 0
def lab_title(readme,fallback):
    for line in read(readme).splitlines():
        if line.startswith("# "):
            title=re.sub(r"^LAB[- ]?\d+\s*[:—-]?\s*","",line[2:].strip(),flags=re.I);return title or fallback
    return fallback
def lab_summary(readme):
    for line in read(readme).splitlines():
        s=line.strip()
        if s and not s.startswith(("#","```","|")) and len(s)>=35:return s[:220]
    return "CyberLab eğitim laboratuvarı."
def discover_labs():
    labs=[]
    for phase,phase_name,folder in PHASES:
        d=REPO_ROOT/folder
        if not d.is_dir():continue
        for c in sorted(d.iterdir()):
            if not c.is_dir():continue
            m=LAB_RE.match(c.name)
            if not m:continue
            n=int(m.group(1));fallback=(m.group(2) or "laboratory").replace("-"," ").title();obs=c/"observations.md";vc=verified(obs);rd=c/"README.md"
            labs.append({"id":f"LAB-{n:03d}","number":n,"title":lab_title(rd,fallback),"summary":lab_summary(rd),"phase":phase,"phase_name":phase_name,"path":str(c.relative_to(REPO_ROOT)),"complete":rd.exists() and obs.exists() and vc>0,"verified_count":vc})
    return sorted(labs,key=lambda x:(x["number"],x["phase"]))
def phase_status(labs):
    used=[l["phase"] for l in labs];highest=max(used,default=0);all_through_highest=all(l["complete"] for l in labs) if labs else False;rows=[]
    active_set=False
    for number,name,folder in PHASES:
        pl=[l for l in labs if l["phase"]==number]
        if pl:
            done=sum(1 for l in pl if l["complete"])
            if done==len(pl):status="done";progress=100
            else:status="active";progress=round(done/len(pl)*100);active_set=True
        elif number<highest:
            status="done";progress=100
        elif not active_set and all_through_highest and number==highest+1:
            status="active";progress=0;active_set=True
        elif not active_set and highest==0 and number==1:
            status="active";progress=0;active_set=True
        else:status="pending";progress=0
        rows.append({"number":number,"name":name,"folder":folder,"status":status,"progress":progress,"labs":len(pl)})
    return rows
def git_status():
    branch=git("branch","--show-current") or "unknown";porcelain=git("status","--porcelain");head=git("rev-parse","HEAD");log=git("log","-8","--date=short","--pretty=format:%h%x09%ad%x09%s");commits=[]
    for line in log.splitlines():
        p=line.split("\t",2)
        if len(p)==3:commits.append({"sha":p[0],"date":p[1],"message":p[2]})
    return {"branch":branch,"dirty":bool(porcelain),"changes":len(porcelain.splitlines()) if porcelain else 0,"head":head,"head_short":head[:7] if head else "","commits":commits}
def status():
    labs=discover_labs();return {"generated_at":datetime.now(timezone.utc).isoformat(),"server":{"host":HOST,"port":PORT,"mode":"local-only"},"git":git_status(),"labs":labs,"phases":phase_status(labs)}
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw):super().__init__(*a,directory=str(DASHBOARD_DIR),**kw)
    def log_message(self,fmt,*a):print(f"[dashboard] {self.address_string()} - {fmt%a}")
    def do_GET(self):
        if urlparse(self.path).path=="/api/status":
            body=json.dumps(status(),ensure_ascii=False,indent=2).encode();self.send_response(200);self.send_header("Content-Type","application/json; charset=utf-8");self.send_header("Cache-Control","no-store");self.send_header("Content-Length",str(len(body)));self.end_headers();self.wfile.write(body);return
        super().do_GET()
def main():
    server=ThreadingHTTPServer((HOST,PORT),Handler);print("CyberLab Command Center");print(f"Local dashboard: http://{HOST}:{PORT}");print("Read-only • localhost only • Ctrl+C to stop")
    try:server.serve_forever()
    except KeyboardInterrupt:print("\nStopping dashboard…")
    finally:server.server_close()
if __name__=="__main__":main()
