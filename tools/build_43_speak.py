"""Builds 4.3 Speaking practice (student page) for Kate + B1 template, and the Teacher's Book page (UA)."""
import re, json, html, sys

E = html.escape
SRC = "/home/claude/bp-kate/lessons/4-3/all/lesson.html"
src = open(SRC, encoding="utf-8").read()
css = src[src.index("<style>"):src.index("</style>") + 8]
script = re.findall(r"<script>(.*?)</script>", src, re.S)[-1]

EXTRA_CSS = """<style>
.card{border:2px solid #e8894a;border-radius:10px;padding:18px 20px;margin:10px 0;background:#fff}
.card .ctx{font-size:14px;color:#8a8b8d;text-transform:uppercase;letter-spacing:.4px;font-weight:500}
.card .line{font-size:22px;font-weight:400;margin:8px 0 6px;color:#231f20}
.card .goal{font-size:15px;color:#c4642a;font-weight:500}
.timer{font-size:28px;font-weight:600;color:#c4642a;min-width:50px;display:inline-block;text-align:center}
.rp{border:1.5px solid #c8c9cb;border-radius:8px;padding:12px 18px;margin:10px 0;background:#fffaf6}
.rp .rh{font-weight:600;color:#c4642a;margin-bottom:4px}.rp ul{margin:6px 0;padding-left:22px}.rp li{margin:3px 0}
.secret{background:#f3f3f4;border:1.5px dashed #8a8b8d;border-radius:8px;padding:10px 16px;margin:10px 0;font-size:15px;color:#4d4d4f}
.ck label{display:block;padding:5px 0;cursor:pointer}.ck input{transform:scale(1.25);margin-right:10px;accent-color:#e8894a}
.tally{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0}.tally button{font:inherit;font-size:14.5px;border:1.5px solid #c8c9cb;background:#fff;border-radius:16px;padding:4px 12px;cursor:pointer}
.tally button.c{border-color:#e8894a}.tally button.s{border-color:#3a7bd5}.tally button b{margin-left:6px;color:#c4642a}
.tally button.used{background:#fbeadb}
.dl p{margin:6px 0;line-height:2.1}.dl .sp{display:inline-block;min-width:26px;font-weight:600;color:#c4642a}
.cue{display:none;font-weight:500;color:#c4642a;letter-spacing:1px}.hidecues .g{display:none}.hidecues .cue{display:inline}
.style{display:none;font-size:20px;font-weight:600;padding:10px 16px;border-radius:8px;margin:8px 0}
.style.a{background:#e3eef8;color:#1f4f6b}.style.b{background:#eef6d3;color:#3e6b1f}
.legend{font-size:14px;color:#4d4d4f;margin:4px 0}.legend span{display:inline-block;width:12px;height:12px;border-radius:6px;margin:0 4px 0 10px;vertical-align:-1px}
.hint2{font-size:14.5px;color:#8a8b8d;margin:4px 0 10px}
</style>"""

# ---------------- vocabulary ----------------
C = ["Can we move to …?", "Is this a good moment to start talking about …?", "I really think we should get to …",
     "That reminds me, …", "Before I forget, …"]
S = ["We’ll come to that later.", "We’ll get to … in a moment.", "There will be plenty of time for that later."]
B = ["Anyway, as I was saying, …", "Sorry, can I just finish this point?", "Let’s get back to …"]

def vg(title, items, extra=False):
    t = title + (' <span style="text-transform:none;font-weight:400;color:#8a8b8d">(extra)</span>' if extra else "")
    return f'<div class="vg"><h4>{t}</h4>' + "".join(f"<span>{E(x)}</span>" for x in items) + "</div>"

VOCAB = ('<details class="voc" open><summary>📖 Vocabulary of this lesson — click to hide / show</summary><div class="vgs">'
         + vg("Changing the subject", C) + vg("Staying on track", S) + vg("Getting back on track", B, True) + "</div></details>")

# ---------------- sections ----------------
secs = []
KEY = {}

def ins(num, text, letter=""):
    l = f"<b>{letter}</b> " if letter else ""
    return f'<p class="ins"><b class="x">{num}</b>{l}{text}</p>'

# 1 recall
gaps = [("Can we m", "ove", " to the budget?", ["move"]),
        ("Is this a good m", "oment", " to start talking about the demo?", ["moment"]),
        ("I really think we should g", "et", " to the deadline.", ["get"]),
        ("That r", "eminds", " me — the client called yesterday.", ["reminds"]),
        ("B", "efore", " I forget, HR needs your holiday dates.", ["before"]),
        ("We’ll c", "ome", " to that later.", ["come"]),
        ("We’ll get to the design in a m", "oment", ".", ["moment"]),
        ("There will be p", "lenty", " of time for that later.", ["plenty"]),
        ("Anyway, as I was s", "aying", ", the demo is on Thursday.", ["saying"]),
        ("Sorry, can I just f", "inish", " this point?", ["finish"]),
        ("Let’s get b", "ack", " to the bug fix.", ["back"])]
rows = ""
for i, (a, _, b, ans) in enumerate(gaps, 1):
    k = f"r1_{i}"; KEY[k] = ans
    rows += (f'<div class="row"><span class="w">{i}</span>{E(a)}<input class="g" data-k="{k}" size="8" autocomplete="off">{E(b)}'
             f'<div class="fb" id="fb_{k}"><span class="h"></span></div></div>')
secs.append(("Warm-up", "Remember the phrases",
    ins(1, "Close the vocabulary box. Complete the phrases from memory. The first letter is there to help you.") + rows +
    '<div class="ctl"><button class="btn" onclick="chkSet(\'r1\')">Check</button><span class="res" id="r_r1"></span></div>'
    '<p class="hint2">Then say each phrase aloud twice: first slowly, then fast and friendly. Smile — these phrases need a polite tone.</p>'))

# 2 quick reactions
QR = [
 ("Meeting about the release date", "Oh, by the way — have you tried the new coffee machine on the third floor?", "the release date",
  "Not yet! We’ll come to that later 😊 So, the release date…"),
 ("Bug-fix call", "Before we start — what are you doing this weekend?", "the bug",
  "Nothing special. There will be plenty of time for that later. Can we look at the bug first?"),
 ("Budget meeting", "Sorry, Slack ping… One second… OK, where were we?", "the budget",
  "We were talking about the budget. Anyway, as I was saying, we need €2,000 more."),
 ("Deadline talk", "That reminds me — did you see the Reddit thread about our app?", "the deadline",
  "Ha, I did! Let’s get back to the deadline, though."),
 ("Sprint planning", "Wait — should we also redesign the logo?", "the timeline",
  "Good question. We’ll get to the design in a moment. First, the timeline."),
 ("Sprint planning", "You know, I think AI will replace all designers in two years.", "the sprint plan",
  "Interesting! There will be plenty of time for that later. Can we finish the sprint plan?"),
 ("You are explaining the new feature", "Yes, yes, but the price —", "your explanation",
  "Sorry, can I just finish this point? Then we’ll talk about the price."),
 ("Contract call", "Oh, I must tell you about my trip to Lisbon!", "the contract",
  "I’d love to hear about it — maybe at lunch? I really think we should get to the contract now."),
 ("Demo planning", "Hmm, sorry, I was reading an email. What did you say?", "the demo",
  "No problem. Anyway, as I was saying, the demo is on Thursday at 11."),
 ("Weekly 1:1", "Let’s talk about the team party first!", "your training course",
  "Sure, we’ll come to that later. Is this a good moment to start talking about my course?"),
 ("Client update", "Before I forget — HR needs your holiday dates.", "the client",
  "OK, I’ll send them today. Let’s get back to the client."),
 ("Onboarding meeting", "Do you think we need a new CRM?", "the onboarding screen",
  "Maybe! We’ll get to that in a moment. First, the onboarding screen."),
]
secs.append(("Speaking", "Quick reactions",
    ins(2, "Your teacher reads the line on the card and interrupts you. React in <b>5 seconds</b>: answer politely and bring the conversation back to your topic.") +
    '<div class="card"><div class="ctx" id="qctx"></div><div class="line" id="qline"></div><div class="goal" id="qgoal"></div>'
    '<div class="model" id="qmodel"></div></div>'
    '<div class="ctl"><button class="btn" id="qnext">Next card ▶</button><button class="btn l" id="qtime">⏱ 5 seconds</button>'
    '<span class="timer" id="qt"></span><button class="btn l" id="qshow">Show a model answer</button><span class="res" id="qn"></span></div>'
    '<p class="hint2">Round 1: any phrase is OK. Round 2: use a <b>different</b> phrase every time. Round 3: your teacher interrupts in the middle of your sentence.</p>'))

# 3 mini-dialogues
DLG = [
 ("A Slack huddle about the release", [
   ("A", "OK, let’s start. The release is on Friday, right?", None),
   ("B", "Yes. Oh, {}, the client wants a new logo too!", ("d1_1", ["That reminds me", "We’ll come to that later", "Sorry, can I just finish this point"])),
   ("A", "{}. First — is the build ready?", ("d1_2", ["We’ll come to that later", "Before I forget", "Is this a good moment to start talking about"])),
   ("B", "Almost. QA found two small bugs.", None),
   ("A", "OK, and {}, who’s on call this weekend?", ("d1_3", ["before I forget", "there will be plenty of time for that later", "as I was saying"])),
 ]),
 ("A 1:1 with your manager", [
   ("You", "{} my training course?", ("d2_1", ["Is this a good moment to start talking about", "We’ll get to", "There will be plenty of time for"])),
   ("Manager", "Sure, but first — did you see the photos from the team party?", None),
   ("You", "Yes, they’re great! {}, though. The course costs €300.", ("d2_2", ["There will be plenty of time for that later", "That reminds me", "Can we move to"])),
   ("Manager", "Hmm. And what about the new project?", None),
   ("You", "{} the project in a moment. Can we agree on the course first?", ("d2_3", ["We’ll get to", "Before I forget", "I really think we should get to"])),
 ]),
 ("A video call with a client", [
   ("You", "So, the new design. What do you think of version 2?", None),
   ("Client", "Sorry, one second, another call… OK, sorry. Where were we?", None),
   ("You", "{}, version 2 has a simpler menu.", ("d3_1", ["Anyway, as I was saying", "That reminds me", "We’ll come to that later"])),
   ("Client", "Right. But what about the price —", None),
   ("You", "{} Then we’ll talk about the price.", ("d3_2", ["Sorry, can I just finish this point?", "Before I forget,", "Can we move to"])),
   ("Client", "Of course, go on.", None),
   ("You", "Thanks. {} a decision today.", ("d3_3", ["I really think we should get to", "We’ll get to", "That reminds me,"])),
 ]),
]
def cue(s):
    return " ".join(w[0] + "_" * min(len(w) - 1, 4) if w[0].isalpha() else w for w in s.split())
body = ins(3, "Choose the best phrase. Check. Then read each dialogue with your teacher.", "A")
import random
rnd = random.Random(43)
for t, lines in DLG:
    body += f'<p class="oh"><b>{E(t)}</b></p><div class="dl">'
    for sp, txt, g in lines:
        if g:
            k, opts = g; KEY[k] = [opts[0]]
            o = opts[:]; rnd.shuffle(o)
            sel = f'<select class="g" data-k="{k}"><option value=""></option>' + "".join(f'<option>{E(x)}</option>' for x in o) + "</select>"
            sel += f'<span class="cue">{E(cue(opts[0]))}</span>'
            a, b = txt.split("{}")
            txt_h = E(a) + sel + E(b) + f'<span class="fb" id="fb_{k}" style="display:inline;margin-left:6px"><span class="h"></span></span>'
        else:
            txt_h = E(txt)
        body += f'<p><span class="sp">{E(sp)}:</span> {txt_h}</p>'
    body += "</div>"
body += ('<div class="ctl"><button class="btn" onclick="chkSet(\'d1\');chkSet(\'d2\');chkSet(\'d3\')">Check</button>'
         '<span class="res" id="r_d1"></span><span class="res" id="r_d2"></span><span class="res" id="r_d3"></span></div>'
         + ins(3, "Now hide the phrases. Read the dialogues again with your teacher — only the first letters will help you. Then swap roles.", "B") +
         '<div class="ctl"><button class="btn l" id="hidec">🙈 Hide the phrases</button></div>')
secs.append(("Functional language", "Mini-dialogues", body))

# helpers for situations
PH_C = ["Can we move to …?", "Is this a good moment…?", "I really think we should get to…", "That reminds me", "Before I forget"]
PH_S = ["We’ll come to that later", "We’ll get to … in a moment", "Plenty of time for that later"]
PH_B = ["Anyway, as I was saying", "Can I just finish this point?", "Let’s get back to…"]
def tally(k, groups):
    btns = ""
    for cls, items in groups:
        for i, p in enumerate(items):
            btns += f'<button class="{cls}" data-t="{k}" data-p="{E(p)}">{E(p)}<b></b></button>'
    return (f'<p class="oh">Phrase tracker — click a phrase every time you use it.</p><div class="tally" data-k="{k}">{btns}</div>'
            f'<input class="g" type="hidden" data-k="{k}">')
def checks(k, items):
    return (f'<div class="ck" data-k="{k}">' + "".join(f'<label><input type="checkbox" data-i="{i}"> {E(x)}</label>' for i, x in enumerate(items))
            + f'</div><input class="g" type="hidden" data-k="{k}">')
def reflect(k, q):
    return f'<p class="ins"><b>C</b> {q}</p><textarea class="g" data-k="{k}" style="min-height:70px" placeholder="I managed to … It was difficult to …"></textarea>'

SIT = [
 ("s1", "Situation 1", "Sprint planning",
  "You are a team member. Your project manager (your teacher) runs the sprint planning call on Zoom. You have <b>5 minutes</b> before your next meeting.",
  ["Agree who fixes the login bug — and by when.", "Agree who designs the new onboarding screen.", "Agree the date of the next demo."],
  "Your teacher is a very friendly PM who likes to talk about everything except the sprint."),
 ("s2", "Situation 2", "Client call",
  "You work for a design studio. You are on a video call with a client (your teacher). The client is busy and multitasks. You have <b>5 minutes</b>.",
  ["Get approval for design version 2.", "Explain: two extra weeks of work will cost €3,000.", "Book the next call (day and time)."],
  "Your teacher is a client who answers calls and messages during the meeting — like Mateo."),
 ("s3", "Situation 3", "1:1 with your manager",
  "It is your weekly 1:1 with your manager (your teacher). You want to ask for a training course. You have <b>10 minutes</b>.",
  ["Ask for €300 for an online course (UX writing / AI tools / English — you choose).", "Ask for two hours a week to study during work time.", "Agree when you will get an answer."],
  "Your manager is in a good mood and loves to chat about the team, the office and holidays."),
]
for sid, lab, title, intro, pts, secret in SIT:
    b = ins(4 + SIT.index(next(x for x in SIT if x[0] == sid)), f"<b>{E(title)}.</b> {intro}", "A")
    b += '<div class="rp"><div class="rh">🎯 Your task — cover all three points</div>' + checks(f"{sid}p", pts) + "</div>"
    b += f'<div class="secret">🔒 {E(secret)} Your teacher has a secret card. Stay polite and keep the relationship good — but get your three points.</div>'
    if sid == "s3":
        b += ('<p class="ins"><b>B</b> Before you start, draw your style card. It tells you <b>how</b> to manage the meeting.</p>'
              '<div class="ctl"><button class="btn l" id="draw">🎴 Draw a style card</button></div>'
              '<div class="style a" id="stA">Option A — Stay on track: politely bring the talk back every time.</div>'
              '<div class="style b" id="stB">Option B — Go with the flow: chat first, wait for a good moment, then ask.</div>'
              '<input class="g" type="hidden" data-k="s3style">')
    else:
        b += '<p class="ins"><b>B</b> Hold the meeting. When it’s finished, tick the points you got.</p>'
    b += tally(f"{sid}t", [("c", PH_C), ("s", PH_S), ("s", PH_B)])
    b += reflect(f"{sid}r", "How did it go? Did you get all three points? How did your teacher feel at the end — happy, neutral or annoyed?")
    secs.append((lab, title, b))

# 7 role swap
b = ins(7, "<b>Swap roles.</b> Now <b>you</b> are the one who changes the subject. Your teacher has an agenda. Change the subject at least <b>four times</b> — but politely, like a nice colleague.", "A")
b += ('<div class="rp"><div class="rh">💬 Your topics — use them to change the subject</div><ul>'
      '<li>a funny Reddit thread you read about remote work</li><li>a new AI tool everybody in your team is talking about</li>'
      '<li>a conference next month — are you both going?</li><li>your laptop is very slow and you need a new one</li>'
      '<li>your holiday plans</li></ul></div>')
b += '<p class="legend">Use phrases for <b>changing the subject</b>:</p>'
b += tally("s7t", [("c", PH_C)])
b += reflect("s7r", "Was it easier to change the subject or to stay on track? Why?")
secs.append(("Role swap", "You change the subject", b))

# 8 write + self
b = ins(8, "Write a short dialogue (6–8 lines) from one of today’s situations. Use at least <b>two</b> phrases for changing the subject and <b>two</b> for staying on track.", "A")
b += '<textarea class="g" data-k="w8" style="min-height:180px" placeholder="A: …&#10;B: …"></textarea>'
b += ins(8, "Think about your real job. Who is your ‘Mateo’? Which phrase from today will you really use this week?", "B")
b += '<textarea class="g" data-k="w8b" style="min-height:70px"></textarea>'
b += ('<div style="margin-top:20px"><div class="selfa"><div class="l">Self-assessment</div><div class="r">How well can you change the subject and stay on track now? 0 = I need more practice, 5 = I can do it easily.'
      '<div class="score" id="score">' + "".join(f'<button data-v="{i}">{i}</button>' for i in range(6)) +
      '</div><textarea class="g" data-k="q" style="min-height:60px;margin-top:8px" placeholder="Questions for your teacher (optional)"></textarea></div></div></div>')
secs.append(("Writing", "Your dialogue", b))

# ---------------- assemble ----------------
ON = ' class="on"'
nav = "".join(f'<button data-s="s{i}"{ON if i == 1 else ""}>{i}</button>' for i in range(1, len(secs) + 1))
main = ""
for i, (lab, sub, b) in enumerate(secs, 1):
    main += f'<section id="s{i}" class="sec{" on" if i == 1 else ""}"><div class="bsec wr">{E(lab)}<span class="sub" style="color:#fff">· {E(sub)}</span></div>{b}</section>'

EXTRA_JS = """
const QR=%s;let qo=[],qi=-1,qint=null;
function qshuffle(){qo=QR.map((_,i)=>i).sort(()=>Math.random()-.5);qi=-1}
function qnext(){if(qi>=qo.length-1)qshuffle();qi++;const c=QR[qo[qi]];$("qctx").textContent=c[0];$("qline").textContent="“"+c[1]+"”";
 $("qgoal").textContent="Your goal: get back to "+c[2]+".";$("qmodel").textContent="Model: "+c[3];$("qmodel").classList.remove("show");$("qn").textContent=(qi+1)+" / "+qo.length;clearInterval(qint);$("qt").textContent=""}
qshuffle();qnext();$("qnext").onclick=qnext;$("qshow").onclick=()=>$("qmodel").classList.toggle("show");
$("qtime").onclick=()=>{let t=5;$("qt").textContent=t;clearInterval(qint);qint=setInterval(()=>{t--;$("qt").textContent=t>0?t:"⏰";if(t<=0)clearInterval(qint)},1000)};
$("hidec").onclick=()=>{const d=$("s3");d.classList.toggle("hidecues");$("hidec").textContent=d.classList.contains("hidecues")?"👀 Show the phrases":"🙈 Hide the phrases"};
const hid=k=>document.querySelector(`input.g[type=hidden][data-k="${k}"]`);
function syncCk(box){const k=box.dataset.k;hid(k).value=[...box.querySelectorAll("input:checked")].map(x=>x.dataset.i).join(",");later()}
document.querySelectorAll(".ck").forEach(box=>box.addEventListener("change",()=>syncCk(box)));
function tget(k){try{return JSON.parse(hid(k).value||"{}")}catch(e){return {}}}
function tdraw(box){const k=box.dataset.k,v=tget(k);box.querySelectorAll("button").forEach(b=>{const n=v[b.dataset.p]||0;b.querySelector("b").textContent=n?"×"+n:"";b.classList.toggle("used",n>0)})}
document.querySelectorAll(".tally").forEach(box=>box.querySelectorAll("button").forEach(b=>b.onclick=()=>{const k=box.dataset.k,v=tget(k);v[b.dataset.p]=(v[b.dataset.p]||0)+1;hid(k).value=JSON.stringify(v);tdraw(box);later()}));
document.querySelectorAll(".tally").forEach(box=>box.querySelectorAll("button").forEach(b=>b.oncontextmenu=e=>{e.preventDefault();const k=box.dataset.k,v=tget(k);if(v[b.dataset.p])v[b.dataset.p]--;hid(k).value=JSON.stringify(v);tdraw(box);later()}));
function showStyle(){const s=hid("s3style").value;$("stA").style.display=s==="A"?"block":"none";$("stB").style.display=s==="B"?"block":"none"}
$("draw").onclick=()=>{hid("s3style").value=Math.random()<.5?"A":"B";showStyle();later()};
window.afterFill=()=>{document.querySelectorAll(".ck").forEach(box=>{const v=(hid(box.dataset.k).value||"").split(",");box.querySelectorAll("input").forEach(x=>x.checked=v.includes(x.dataset.i))});document.querySelectorAll(".tally").forEach(tdraw);showStyle()};
""" % json.dumps(QR, ensure_ascii=False)

def page(lesson_name, code, foot):
    sc = script
    sc = re.sub(r'const LESSON="[^"]*";', lambda m: 'const LESSON=' + json.dumps(lesson_name) + ';', sc)
    sc = re.sub(r'const STUDENT_CODE="[^"]*";', lambda m: 'const STUDENT_CODE=' + json.dumps(code) + ';', sc)
    sc = re.sub(r'const KEY=\{.*?\};', lambda m: 'const KEY=' + json.dumps(KEY, ensure_ascii=False) + ';', sc, flags=re.S)
    sc = sc.replace("start();", EXTRA_JS + "\nstart();")
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>4.3 Managing conversations — SPEAKING PRACTICE</title><link href="https://fonts.googleapis.com/css2?family=Fira+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&display=swap" rel="stylesheet">
{css}{EXTRA_CSS}</head><body>
<header><div class="n">4.3</div><h1>Managing conversations</h1><div class="tag">SPEAKING PRACTICE</div></header>
<div class="out1"><b>Lesson outcome</b><span>Stay on track politely when someone keeps changing the subject — and change the subject when you need to.</span></div>
<div class="wrap">{VOCAB}
<div class="top"><a href="../../../index.html">← Contents</a><div class="bar"><span class="st" id="st">Loading…</span></div></div>
<div class="tcom" id="tcom"><b>💬 Teacher’s comment</b><div id="tcomt"></div></div>
<nav>{nav}</nav><main>{main}
<div class="ctl" style="margin-top:26px"><button class="btn" id="submit">Send to my teacher</button><span class="st" id="st2"></span></div>
<div class="done" id="done">✓ Sent to your teacher. You can still change your answers — they save automatically.</div></main></div>
<footer>{foot}Valentyna Hordiienko · Middle Learning Architect</footer>
<script>{sc}</script></body></html>"""

code = re.search(r'const STUDENT_CODE="([^"]*)"', src).group(1)
name = "BP B1 4.3 Managing conversations · Speaking"
import os
os.makedirs("/home/claude/bp-kate/lessons/4-3/all", exist_ok=True)
open("/home/claude/bp-kate/lessons/4-3/all/speak.html", "w", encoding="utf-8").write(page(name, code, ""))
os.makedirs("/home/claude/bp-b1/lessons/4-3/all", exist_ok=True)
open("/home/claude/bp-b1/lessons/4-3/all/speak.html", "w", encoding="utf-8").write(page(name, "", ""))
print("ok", len(KEY), "keys")
