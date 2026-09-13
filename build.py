#!/usr/bin/env python3
"""Render a skill-tracker HTML from a discipline's skills.json.

usage: python3 build.py acro
Writes <discipline>/<discipline>_skills.html and mirrors it to Windows Downloads.
"""
import json, re, sys, html, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOWNLOADS = Path("/mnt/c/Users/olga.p/Downloads")
WIKI = "https://commons.wikimedia.org/wiki/Special:FilePath/{}?width=520"

TITLES = {"acro": ("Acro Yoga Skill Map", "🤸"), "pole": ("Pole Skill Map", "🪩"), "stretch": ("Stretching Map", "🧘"), "mobility": ("Hip Mobility Plan", "🦵"), "speaking": ("Speaking Skills Map", "🎤"), "pilates": ("Pilates Mat Map", "🌀"), "spanish": ("Spanish · Ten Lessons", "🇪🇸")}
SOURCES = {
 "pole": """<p>Level bands follow <a href="https://polemovebook.com/">PoleMovebook</a>'s ladder (Intro → solid invert → solid Ayesha → Iron X/Phoenix) cross-checked with <a href="https://polepedia.com/move-dictionary/">PolePedia</a> and <a href="https://louspolewearstudios.com/en/blogs/blog/pole-dance-figuren">Lou's level overview</a>. Sport reference: the <a href="https://ipsfsports.org/downloads/Uncategorised/ipsf_pole_sports_code_of_points_2025-2027_final_070120240.pdf">IPSF Pole Sports Code of Points 2025–27</a> — compulsory elements are grouped strength / flexibility / spins / deadlifts with technical values 0.1–1.0; this board's L4–L5 shapes are the ones that appear there. Tutorials picked 2026-09-12 from ElizabethBfit, PolePedia, PoleFreaks (Holly Munson), Pole with Steph, Polesthenics and the "3 Essential Tips" series.</p>""",
 "mobility": """<p>Built for very tight hips as therapeutic mobility, not performance flexibility. Structure borrows the Bodyweight Warrior "Basics" tier (resting squat, hinge, cross-legged sit) as the goals, and drills from Squat University, Ask Doctor Jo, Antranik and physio channels. The daily 10 minutes matters more than any single drill; test the goals monthly, photograph them, and expect 3–6 months for real change. Not medical advice — a physio should see anything that pinches, clicks or radiates.</p>""",
 "pilates": """<p>Exercise list and order are Joseph Pilates' 34 from <em>Return to Life Through Contrology</em> (<a href="https://www.pilatesanytime.com/blog/mat/the-34-pilates-mat-exercises-">Pilates Anytime's list</a>, <a href="https://onlinepilatesclasses.com/blog/pilates-mat-exercise-order/">OPC on the order</a>), with the pre-Pilates fundamentals studios teach first. Level bands are how the sequence is usually staged, not an official grading. Tutorials from Pilates Anytime, Online Pilates Classes, Pilates Encyclopedia and physio-led channels. Anything with a history of back or neck trouble: Roll Over, Jackknife, Neck Pull and the rolling exercises want a teacher's eyes first.</p>""",
 "speaking": """<p>Skill list draws on Toastmasters' <a href="https://www.toastmasters.org/pathways-overview/pathways-presentation-mastery-path">Presentation Mastery</a> competencies, Matt Abrahams (Stanford GSB) and Julian Treasure's TED talk. The order is deliberate: voice, then everyday habits, then prepared talks, then improvisation, then presence. The two habits that compound are recording yourself weekly and practising out loud — a Toastmasters club or a weekly 2-minute recorded 'table topic' gives both.</p>""",
 "spanish": """<p>Ten story lessons written at the <b>2k frequency band</b> for a reader with several years of school Spanish whose gap is abstract, functional vocabulary rather than grammar — the same profile and method as Olga's own tutor (<a href="https://github.com/olga-pyatokha/spanish-learning">spanish-learning</a>): frequency bands instead of CEFR, targets only from the working band, cognates flagged not drilled, form-confusable words taught as contrast sets, at most one support word per cloze sentence, and <b>no yes/no self-report</b> — recognition counts only when the English is produced. Companion listening at this band: <a href="https://www.hoyhablamos.com/">Hoy Hablamos</a>, <a href="https://www.1001reasonstolearnspanish.com/">Español con Juan</a>; reading: <a href="https://www.bbc.com/mundo">BBC Mundo</a>.</p>""",
 "stretch": """<p>Bands follow <a href="https://www.bodyweightwarrior.co.uk/blog/how-flexible-are-you/">Bodyweight Warrior's flexibility levels</a>; progressions and drills draw on <a href="https://www.daniwinksflexibility.com/bendy-blog">Dani Winks Flexibility</a>, <a href="https://gmb.io/splits/">GMB</a> and <a href="https://antranik.org/">Antranik</a>. Dose lines are starting points, not prescriptions — deep stretching 3–4× a week beats daily grinding, and nothing here should hurt in a joint.</p>""",
}
USERS = {"acro": ["olga", "reza"], "pole": ["olga"], "stretch": ["olga"], "mobility": ["sid"], "speaking": ["tanya"], "pilates": ["tanya"], "spanish": ["tanya"]}  # who has a board where
# hashtag pages deep-link into the Instagram app; only for names that are acro-specific
# enough that the tag is not swamped by unrelated posts. Everything else gets a site: search.
IG_TAGS = {
 "front-plank":"frontplank","front-bird":"frontbird","bow":"acrobow","throne":"acrothrone",
 "straddle-throne":"straddlethrone","f2s":"foottoshin","reverse-throne":"reversethrone",
 "back-bird":"backbird","whale":"highflyingwhale","reverse-bird":"reversebird","back-plank":"backplank",
 "floating-paschi":"floatingpaschi","straddle-bat":"straddlebat","bat":"acrobat","boat":"acroboat",
 "mermaid":"acromermaid","koala":"acrokoala","vishnu":"vishnuscouch","camel":"acrocamel",
 "backfly-dancer":"backflydancer","dragonfly":"acrodragonfly",
 "folded-leaf":"foldedleaf","hangle-dangle":"hangledangle","hammock":"acrohammock","super-yogi":"superyogi",
 "forward-flying":"therapeuticflying","backward-flying":"therapeuticflying",
 "candlestick":"acrocandlestick","shoulderstand":"acroshoulderstand","star":"acrostar","inside-star-mount":"acrostar",
 "free-star":"freestar","reverse-star":"reversestar","side-star":"sidestar","tick-tock":"ticktock",
 "f2h":"foottohand","reverse-f2h":"reversefoottohand","f2f":"foottofoot","h2h":"handtohand",
 "bicep-stand":"bicepstand","forearm-star":"scorpionstar","needle-lotus":"freeshoulderstand",
 "thighstand":"thighstand","two-high":"twohigh","standing-f2h":"standingacro","flag":"acroflag",
 "standing-h2h":"standinghandtohand","dance-acro":"danceacro","bird-on-shoulders":"standingacro",
 "ninja-star":"ninjastar","barrel-roll":"barrelroll","nunchuck":"nunchuck","four-step":"fourstep",
 "trapdoor":"trapdoor","tumbleweed":"tumbleweed","spider-roll":"spiderroll","swimming-mermaid":"swimmingmermaid",
 "koala-wm":"acrokoala","monkey-frog":"monkeyfrog","rotisserie":"rotisserie","catherines-wheel":"catherineswheel",
 "whirly-gig":"whirlygig","vertical-spins":"washingmachine","free-machines":"washingmachine",
 "pops-intro":"acropops","whips":"acrowhips","icarian":"icarian","icarian-expert":"icariangames",
 "pass-the-flyer":"acrotrio","stacking":"acrotrio","group-dynamics":"banquine",
}

def esc(s): return html.escape(str(s), quote=True)

def render_lessons():
    import html as H
    L = json.loads((ROOT / "spanish/lessons.json").read_text())
    tpl = (ROOT / "lesson_template.html").read_text()
    out_dir = ROOT / "spanish/lessons"; out_dir.mkdir(exist_ok=True)
    n_all = len(L)
    for l in L:
        n = l["n"]; nn = f"{n:02d}"
        es = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", H.escape(l["es"]))
        targets = "".join(f"<div><b>{H.escape(a)}</b> <span>— {H.escape(bb)}</span></div>" for a, bb in l["targets"])
        glosses = " · ".join(f"<b>{H.escape(a)}</b> {H.escape(bb)}" for a, bb in l["glosses"])
        cloze = "".join(f"<li>{H.escape(s)}</li>" for s, _ in l["cloze"])
        answers = "".join(f"<li>{H.escape(a)}</li>" for _, a in l["cloze"])
        speak = "".join(f"<li>{s}</li>" for s in l["speak"])  # prompts carry light HTML
        prev_ = f'<a href="{n-1:02d}.html">← {n-1}</a>' if n > 1 else ""
        next_ = f'<a href="{n+1:02d}.html">{n+1} →</a>' if n < n_all else ""
        prevf = f'<a href="{n-1:02d}.html">← Lección {n-1}</a>' if n > 1 else ""
        nextf = f'<a href="{n+1:02d}.html">Lección {n+1} →</a>' if n < n_all else ""
        page = (tpl.replace("__N__", str(n)).replace("__TITLE__", H.escape(l["title"])).replace("__THEME__", H.escape(l["theme"]))
                   .replace("__GRAMMAR__", l["grammar"]).replace("__ES__", es).replace("__TARGETS__", targets)
                   .replace("__GLOSSES__", glosses).replace("__EN__", H.escape(l["en"])).replace("__CLOZE__", cloze)
                   .replace("__ANSWERS__", answers).replace("__SPEAK__", speak)
                   .replace("__PREV__", prev_).replace("__NEXT__", next_).replace("__PREVF__", prevf).replace("__NEXTF__", nextf))
        (out_dir / f"{nn}.html").write_text(page, encoding="utf-8")
    print(f"wrote {n_all} lesson pages")

def build(disc: str):
    if disc == "spanish":
        render_lessons()
    d = json.loads((ROOT / disc / "skills.json").read_text())
    title, emoji = TITLES.get(disc, (f"{disc} skills", "✅"))
    for s in d["skills"]:
        if s.get("img"):
            s["img_url"] = WIKI.format(s["img"])
            s["img_page"] = "https://commons.wikimedia.org/wiki/File:" + s["img"]
        q = s["name"].split("(")[0].split("/")[0].strip()
        tag = s.get("tag") or (IG_TAGS.get(s["id"]) if disc == "acro" else None)
        s["ig"] = (f"https://www.instagram.com/explore/tags/{tag}/" if tag
                   else "https://www.google.com/search?q=" + ("site:instagram.com acroyoga " + q).replace(" ", "+"))
        s["ig_label"] = f"#{tag}" if tag else "instagram via google"
        REF = {"acro": ("https://www.acropedia.org/?s=", "📖 acropedia"),
               "pole": ("https://polepedia.com/?s=", "📖 polepedia"),
               "stretch": ("https://www.daniwinksflexibility.com/search?q=", "📖 dani winks"),
               "mobility": ("https://www.google.com/search?q=site:squatuniversity.com+", "📖 squat university"),
               "pilates": ("https://www.google.com/search?q=site:pilatesanytime.com+", "📖 pilates anytime"),
               "speaking": ("https://www.google.com/search?q=site:toastmasters.org+", "📖 toastmasters"),
               "spanish": ("https://www.spanishdict.com/translate/", "📖 spanishdict")}
        base, label = REF.get(disc, REF["acro"])
        s["ref"] = base + q.replace(" ", "+"); s["ref_label"] = label
    for s in d["skills"]:
        if s.get("link") and s["id"].startswith("l"):
            s["tile"] = s["id"][1:].lstrip("0") or "0"
    # tutorial video id -> thumbnail
    for s in d["skills"]:
        m = re.search(r"(?:v=|youtu\.be/)([\w-]{11})", s.get("yt", ""))
        if m: s["yt_id"] = m.group(1)
    data = json.dumps(d, ensure_ascii=False)
    tpl = (ROOT / "template.html").read_text()
    if disc != "acro":
        tpl = re.sub(r'<p>Skill list and level bands assembled.*?</p>\s*<p><a href="https://www.acropedia.org.*?</p>\s*<p>Named channels.*?</p>', "", tpl, flags=re.S)
    links = []
    for user in USERS.get(disc, ["olga"]):
        prog = {}
        for p in (DOWNLOADS / f"{disc}_progress_{user}.json", ROOT / disc / f"progress_{user}.json"):
            if p.exists():
                prog = json.loads(p.read_text()); print(f"progress[{user}] from", p, len(prog), "skills")
                (ROOT / disc / f"progress_{user}.json").write_text(json.dumps(prog, indent=1)); break
        out = (tpl.replace("__TITLE__", esc(title)).replace("__EMOJI__", emoji).replace("__DATA__", data)
                  .replace("__LEVELNOTES__", esc(d.get("level_notes", "")) + (" —" if d.get("level_notes") else ""))
                  .replace("__SOURCES__", SOURCES.get(disc, ""))
                  .replace("__DISC__", disc).replace("__USER__", user).replace("__USERNAME__", user.capitalize())
                  .replace("__PROGRESS__", json.dumps(prog)))
        out_path = ROOT / disc / f"{user}.html"
        out_path.write_text(out, encoding="utf-8")
        print("wrote", out_path, f"{out_path.stat().st_size//1024} KB")
        links.append((user, f"{disc}/{user}.html"))
        if user == "olga" and DOWNLOADS.exists():
            dst = DOWNLOADS / f"{disc}yoga_skills.html"; shutil.copy(out_path, dst); print("mirrored", dst)
    # landing page: every discipline that has a data file, every user
    discs = [p.parent.name for p in sorted(ROOT.glob("*/skills.json"))]
    sections = ""
    for dd in discs:
        tt, ee = TITLES.get(dd, (dd, "✅"))
        items = "".join(f'<li><a href="{dd}/{u}.html">{u.capitalize()}</a></li>' for u in USERS.get(dd, ["olga"]))
        sections += f"<h2>{ee} {esc(tt)}</h2><ul>{items}</ul>"
    (ROOT / "index.html").write_text(f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Skill Tracker</title><style>body{{font:17px/1.5 -apple-system,"Segoe UI",sans-serif;background:#faf8f4;color:#1f2328;max-width:640px;margin:40px auto;padding:0 20px}}
h2{{margin:26px 0 6px;font-size:20px}} ul{{margin:0;padding-left:22px}} li{{margin:6px 0}} a{{color:#0f766e;font-weight:600;text-decoration:none}} a:hover{{text-decoration:underline}} p{{color:#6b7280}}</style></head>
<body><h1>Skill Tracker</h1><p>One board per person per discipline. Progress saves in your own browser; use <em>Save progress to file</em> in the footer to back it up.</p>{sections}</body></html>""", encoding="utf-8")
    print("wrote index.html")

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    for disc in ([p.parent.name for p in sorted(ROOT.glob("*/skills.json"))] if arg == "all" else [arg]):
        build(disc)
