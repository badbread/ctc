#!/usr/bin/env python3
# Generate a faithful asciinema v2 cast of the ctc TUI.
# Frames are hand-built from the REAL bin/ctc rendering (same glyphs, same
# 256-color palette, same footer text) so the demo matches the tool exactly.
import json, sys

COLS, ROWS = 74, 22
E = "\x1b"
RST=f"{E}[0m"; B=f"{E}[1m"; D=f"{E}[2m"
C1=f"{E}[38;5;51m"; C2=f"{E}[38;5;45m"; C3=f"{E}[38;5;39m"
MAG=f"{E}[38;5;201m"; GRN=f"{E}[38;5;46m"; YEL=f"{E}[38;5;226m"
ORG=f"{E}[38;5;208m"; GRY=f"{E}[38;5;244m"; RED=f"{E}[38;5;196m"
CLR=f"{E}[2J{E}[H"   # clear + home, like banner()'s `clear`

events=[]; t=[0.0]
def emit(s, dt=0.0):
    t[0]+=dt
    events.append([round(t[0],3),"o",s])
def line(s="", dt=0.0): emit(s+"\r\n", dt)
def pause(dt): t[0]+=dt

IW = COLS-2  # interior width
def top(col=C3): return f"{col}╭"+"─"*IW+f"╮{RST}"
def bot(col=C3): return f"{col}╰"+"─"*IW+f"╯{RST}"
def boxline(text, plainlen, col=C3):
    pad = IW-1-plainlen
    return f"{col}│{RST} {text}"+" "*max(pad,0)+f"{col}│{RST}"

def banner(host,model,mode,rc,launch):
    l1p="ctc · claude terminal connect"
    l1=f"{B}{MAG}ctc{RST}{D} · claude terminal connect{RST}"
    rcw="rc:on" if rc else "rc:off"
    rtag=f"{GRN}rc:on{RST}" if rc else f"{GRY}rc:off{RST}"
    l2p=f"{host} · {model} · {mode} · {rcw} · {launch}"
    l2=f"{C2}{host}{RST} · {C1}{model}{RST} · {YEL}{mode}{RST} · {rtag} · {C2}{launch}{RST}"
    out=[top(),boxline(l1,len(l1p)),boxline(l2,len(l2p)),bot()]
    return "\r\n".join(out)+"\r\n"

def sep(): return f"{C3}"+"┄"*20+f"{RST}"
def liverow(name,sel=False):
    body=f"{GRN}●{RST} {name:<20}{D}live · connect from app{RST}"
    if sel: return f"{MAG}{B} ▎{RST} {B}{body}{RST}"
    return f"   {body}"
def idlerow(name,sel=False):
    body=f"{GRY}◌{RST} {name:<20}{D}idle · claude exited{RST}"
    if sel: return f"{MAG}{B} ▎{RST} {B}{body}{RST}"
    return f"   {body}"
def menurow(text,sel=False):
    if sel: return f"{MAG}{B} ▎{RST} {B}{text}{RST}"
    return f"   {text}"
NAVF=f"{D}   ↑↓ move · ⏎ select · ⇧⇥ cycle mode · q quit{RST}"
NAVB=f"{D}   ↑↓ move · ⏎ select · q back{RST}"

def menu(host,model,mode,rc,launch,rows,nav=NAVF,title=None):
    s=CLR+banner(host,model,mode,rc,launch)+"\r\n"
    if title: s+=title+"\r\n"
    s+="\r\n".join(rows)+"\r\n\r\n"+nav+"\r\n"
    return s

# ---- scene timing helpers ----
def screen(s, hold=1.4, dt=0.25): emit(s,dt); pause(hold)

# ===========================================================================
# SCENE 1 — open ctc, one project already running
host="dev"
S1_rows=[
  f"{D} 1 running · select to manage{RST}",
  liverow("my-api", sel=True),
  sep(),
  menurow(f"{C1}[n]{RST} launch new session…"),
  menurow(f"{C1}[o]{RST} options"),
  menurow(f"{C1}[q]{RST} quit"),
]
screen(menu(host,"opus","acceptEdits",True,"detached",S1_rows), hold=2.0)

# move down to "launch new"
S1b=[
  f"{D} 1 running · select to manage{RST}",
  liverow("my-api"),
  sep(),
  menurow(f"{C1}[n]{RST} launch new session…", sel=True),
  menurow(f"{C1}[o]{RST} options"),
  menurow(f"{C1}[q]{RST} quit"),
]
screen(menu(host,"opus","acceptEdits",True,"detached",S1b), hold=0.9, dt=0.5)

# ===========================================================================
# SCENE 2 — launch_new: pick a project to start a backend
S2_rows=[
  menurow(f"{C2}dotfiles{RST}", sel=True),
  menurow(f"{C2}ctc{RST}"),
  menurow(f"{C2}homelab-infra{RST}"),
  menurow(f"{C2}notes-api{RST}"),
  sep(),
  menurow(f"{GRY}[/]{RST} type a path…"),
]
screen(menu(host,"opus","acceptEdits",True,"detached",S2_rows,nav=NAVB,
      title=f"{B}{C3} LAUNCH NEW {RST} {GRY}detached backend · connect from the app{RST}"), hold=1.2)
# move to homelab-infra
S2b=[
  menurow(f"{C2}dotfiles{RST}"),
  menurow(f"{C2}ctc{RST}"),
  menurow(f"{C2}homelab-infra{RST}", sel=True),
  menurow(f"{C2}notes-api{RST}"),
  sep(),
  menurow(f"{GRY}[/]{RST} type a path…"),
]
screen(menu(host,"opus","acceptEdits",True,"detached",S2b,nav=NAVB,
      title=f"{B}{C3} LAUNCH NEW {RST} {GRY}detached backend · connect from the app{RST}"), hold=1.0, dt=0.45)

# ===========================================================================
# SCENE 3 — trust prompt (the real first-launch gate) then launched
s=CLR+banner(host,"opus","acceptEdits",True,"detached")
s+="\r\n"
s+=f" {YEL}⚠ first launch{RST}  {B}/home/you/homelab-infra{RST}\r\n"
s+=f" {GRY}Claude shows a \"trust this folder?\" prompt the detached backend{RST}\r\n"
s+=f" {GRY}can't answer. Trust it now so launches work without attaching?{RST} [y/N]: "
emit(s,0.3); pause(0.9)
emit("y",0.4); pause(0.5)
emit("\r\n",0.2)
emit(f" {GRN}✓ trusted{RST}\r\n",0.3); pause(0.5)
emit(f"\r\n {GRN}▸ launched{RST}  {B}claude-homelab-infra{RST}  {D}(claude --remote-control --permission-mode acceptEdits){RST}\r\n",0.3)
emit(f" {GRY}connect from the Claude app · session: {C2}claude-homelab-infra{RST}\r\n",0.2)
pause(1.4)

# SCENE 3b — the whole point: it now shows up in the NATIVE Claude app on your
# phone. Your local claude, driven remotely from the app you already use.
s=CLR+banner(host,"opus","acceptEdits",True,"detached")+"\r\n"
s+=f"   {D}same session, now live in the Claude app on your phone{RST}\r\n\r\n"
PW=30  # interior width of the phone card
def pcard(colored, plainlen):
    pad=PW-plainlen
    return f"   {GRY}│{RST}{colored}"+" "*max(pad,0)+f"{GRY}│{RST}"
s+=f"   {GRY}┌"+"─"*PW+f"┐{RST}\r\n"
s+=pcard(f" {MAG}{B}✻ Claude{RST}          {GRN}● Remote{RST} ", len(" ✻ Claude          ● Remote "))+"\r\n"
s+=pcard(f" {D}homelab-infra · dev{RST}", len(" homelab-infra · dev"))+"\r\n"
s+=f"   {GRY}├"+"─"*PW+f"┤{RST}\r\n"
s+=pcard(f" {GRN}>{RST} {D}add healthcheck endpoint{RST}", len(" > add healthcheck endpoint"))+"\r\n"
s+=pcard(f" {GRN}●{RST} {D}Editing Caddyfile {GRN}+6 -0{RST}", len(" ● Editing Caddyfile +6 -0"))+"\r\n"
s+=pcard("", 0)+"\r\n"
s+=pcard(f" {D}type a message…{RST}", len(" type a message…"))+"\r\n"
s+=f"   {GRY}└"+"─"*PW+f"┘{RST}\r\n\r\n"
s+=f"   {C2}your local claude — driven from the native app{RST}\r\n"
emit(s,0.3); pause(2.6)

# ===========================================================================
# SCENE 4 — back at menu, now TWO live; select a running one to manage
S4_rows=[
  f"{D} 2 running · select to manage{RST}",
  liverow("my-api"),
  liverow("homelab-infra", sel=True),
  sep(),
  menurow(f"{C1}[n]{RST} launch new session…"),
  menurow(f"{C1}[o]{RST} options"),
  menurow(f"{C1}[q]{RST} quit"),
]
screen(menu(host,"opus","acceptEdits",True,"detached",S4_rows), hold=1.6)

# ===========================================================================
# SCENE 5 — per-session actions: attach / kill / back
s=CLR+banner(host,"opus","acceptEdits",True,"detached")+"\r\n"
s+=f"{B}homelab-infra{RST}  {GRY}claude-homelab-infra{RST}\r\n\r\n"
s+=menurow(f"{GRN}[a]{RST} attach here {D}(ssh/tmux){RST}", sel=True)+"\r\n"
s+=menurow(f"{RED}[k]{RST} kill this session")+"\r\n"
s+=menurow(f"{GRY}[b]{RST} back")+"\r\n\r\n"+NAVB+"\r\n"
screen(s, hold=1.8, dt=0.3)

# ===========================================================================
# SCENE 6 — attach: drop into the live claude session (tmux)
s=CLR
s+=f"{D}[attached to claude-homelab-infra — Ctrl-b d to detach]{RST}\r\n\r\n"
s+=f"{MAG}{B}✻ Claude Code{RST} {D}· homelab-infra · --remote-control{RST}\r\n"
s+=f"{D}─────────────────────────────────────────────{RST}\r\n"
s+=f"{GRN}>{RST} add a healthcheck endpoint to the proxy\r\n\r\n"
s+=f"{D}● Reading{RST} caddy/Caddyfile\r\n"
s+=f"{D}● Editing{RST} caddy/Caddyfile {GRN}+6 -0{RST}\r\n"
emit(s,0.3); pause(2.2)
# detach
emit(f"\r\n{YEL}[detached]{RST} session keeps running.\r\n",0.3); pause(1.2)

# ===========================================================================
# SCENE 7 — OPTIONS screen: set default launch mode + flags (the nerdy part)
def options(launch_lbl, mode_lbl, model_lbl, rc_lbl, cont_lbl, selidx):
    rows=[
      f"launch mode       → {launch_lbl}",
      f"permission mode   → {mode_lbl}   {D}--permission-mode{RST}",
      f"model             → {model_lbl}   {D}--model{RST}",
      f"remote control    → {rc_lbl}   {D}--remote-control{RST}",
      f"continue last     → {cont_lbl}   {D}--continue{RST}",
      f"{GRY}back to menu{RST}",
    ]
    out=[]
    for i,r in enumerate(rows):
        out.append(menurow(r, sel=(i==selidx)))
    s=CLR+banner(host,"opus","acceptEdits",True,"detached")+"\r\n"
    s+=f"{B}{C3} OPTIONS {RST} {GRY}apply to NEW sessions{RST}\r\n\r\n"
    s+="\r\n".join(out)+"\r\n\r\n"+NAVF+"\r\n"
    return s

det=f"{C2}detached{RST} {D}(backend / connect from app){RST}"
att=f"{GRN}attach{RST} {D}(open here over ssh){RST}"
acc=f"{YEL}acceptEdits{RST}"; planm=f"{C1}plan{RST}"
screen(options(det, acc, f"{C1}opus{RST}", f"{GRN}on{RST}", f"{GRY}off{RST}", 0), hold=1.6)
# toggle launch mode -> attach
screen(options(att, acc, f"{C1}opus{RST}", f"{GRN}on{RST}", f"{GRY}off{RST}", 0), hold=1.3, dt=0.4)
# move to permission mode
screen(options(att, acc, f"{C1}opus{RST}", f"{GRN}on{RST}", f"{GRY}off{RST}", 1), hold=0.9, dt=0.4)
# Shift+Tab cycles permission mode acceptEdits -> plan  (Claude Code feel)
screen(options(att, planm, f"{C1}opus{RST}", f"{GRN}on{RST}", f"{GRY}off{RST}", 1), hold=1.6, dt=0.4)

# ===========================================================================
# SCENE 8 — kill flow (multi-select manage), then closing card
S8=[
  f"{D} 2 running · Space to mark, Enter to kill{RST}",
  f" {YEL}✓{RST} {GRN}●{RST} my-api               {D}live{RST}",
  f"   {GRN}●{RST} homelab-infra        {D}live{RST}",
]
s=CLR+banner(host,"opus","acceptEdits",True,"attach")+"\r\n"
s+=f"{B}{RED} KILL SESSIONS {RST}  {GRY}Space to mark, Enter to kill{RST}\r\n\r\n"
s+="\r\n".join(S8)+"\r\n\r\n"
s+=f"{D} ↑/↓ j/k move   Space mark   a all   Enter confirm   q/Esc cancel{RST}\r\n"
screen(s, hold=1.8, dt=0.3)
emit(f"\r\n {RED}kill 1 session?{RST} [y/N]: ",0.3); pause(0.7)
emit("y",0.4); emit("\r\n",0.2)
emit(f" {RED}✗ killed{RST} claude-my-api\r\n",0.3); pause(1.4)

# closing card
s=CLR+"\r\n"
s+=banner(host,"opus","acceptEdits",True,"detached")+"\r\n"
s+=f"   {B}{MAG}ctc{RST} {D}— claude terminal connect{RST}\r\n\r\n"
s+=f"   {GRN}●{RST} launch detached backends from your phone\r\n"
s+=f"   {GRN}●{RST} attach / detach over ssh, sessions survive\r\n"
s+=f"   {GRN}●{RST} manage instances · set launch+permission modes\r\n"
s+=f"   {GRN}●{RST} one bash file · no server · drive from the Claude app\r\n\r\n"
s+=f"   {C2}github.com/badbread/ctc{RST}\r\n"
emit(s,0.3); pause(3.0)

cast={"version":2,"width":COLS,"height":ROWS,
      "theme":{"fg":"#c8d3f5","bg":"#10131c"}}
with open(sys.argv[1],"w") as f:
    f.write(json.dumps(cast)+"\n")
    for ev in events:
        f.write(json.dumps(ev)+"\n")
print(f"wrote {sys.argv[1]} · {len(events)} events · {t[0]:.1f}s")
