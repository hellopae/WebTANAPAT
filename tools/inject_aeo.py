#!/usr/bin/env python3
"""ฉีด answer box / สารบัญ / FAQ + FAQPage & HowTo schema เข้าไปในหน้าบทความ (idempotent)"""
import re, json, glob, os, sys, html

SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SCRATCH = os.path.dirname(os.path.abspath(__file__))
BASE = "https://tanapat.co.th/"

data = {}
for f in sorted(glob.glob(os.path.join(SCRATCH, "aeo*.json"))):
    data.update(json.load(open(f, encoding="utf-8")))

REL_SPLIT = '<h2 style="font-size:24px">บทความ'

def strip_markers(s, name):
    return re.sub(r'<!--AEO:%s-->.*?<!--/AEO:%s-->' % (name, name), '', s, flags=re.S)

def esc(t):
    return html.escape(t, quote=False)

def build_answer(ans):
    return ('<!--AEO:ANSWER--><div class="answer-box"><span class="ab-label">คำตอบสั้น ๆ</span>'
            '<p>%s</p></div><!--/AEO:ANSWER-->' % esc(ans))

def build_toc(heads):
    li = "".join('<li><a href="#%s">%s</a></li>' % (i, esc(t)) for i, t in heads)
    return ('<!--AEO:TOC--><nav class="toc" aria-label="สารบัญ"><b>ในบทความนี้</b>'
            '<ol>%s</ol></nav><!--/AEO:TOC-->' % li)

def build_faq(faq):
    qa = "".join(
        '<div class="qa"><button>%s</button><div class="ans"><div>%s</div></div></div>'
        % (esc(q["q"]), esc(q["a"]))
        for q in faq)
    return ('<!--AEO:FAQ--><section class="art-faq"><b>คำถามที่พบบ่อย</b>'
            '<div class="faq">%s</div></section><!--/AEO:FAQ-->' % qa)

def build_ld(fname, entry):
    blocks = []
    blocks.append({
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q["q"],
                        "acceptedAnswer": {"@type": "Answer", "text": q["a"]}}
                       for q in entry["faq"]]})
    ht = entry.get("howto")
    if ht:
        blocks.append({
            "@context": "https://schema.org", "@type": "HowTo",
            "name": ht["name"],
            "step": [{"@type": "HowToStep", "position": i, "name": s["name"], "text": s["text"]}
                     for i, s in enumerate(ht["steps"], 1)],
            "mainEntityOfPage": BASE + fname})
    out = "".join('<script type="application/ld+json">%s</script>'
                  % json.dumps(b, ensure_ascii=False, separators=(", ", ": "))
                  for b in blocks)
    return "<!--AEO:LD-->" + out + "<!--/AEO:LD-->"

changed = []
for fname, entry in sorted(data.items(), key=lambda kv: int(re.search(r'\d+', kv[0]).group())):
    path = os.path.join(SITE, fname)
    s = open(path, encoding="utf-8").read()
    orig = s

    # ล้างของเดิมก่อน (รันซ้ำได้)
    for m in ("ANSWER", "TOC", "FAQ", "LD"):
        s = strip_markers(s, m)

    head, sep, rest = s.partition('<article class="art-body">')
    if not sep:
        print("!! ไม่เจอ art-body:", fname); continue
    body, endsep, tail = rest.partition('</article>')

    # แยกส่วนเนื้อหาจริง ออกจากบล็อกบทความที่เกี่ยวข้องท้ายหน้า
    idx = body.find(REL_SPLIT)
    content, related = (body[:idx], body[idx:]) if idx != -1 else (body, "")

    # ใส่ id ให้ h2 ในเนื้อหา
    heads = []
    def add_id(m):
        attrs = re.sub(r'\s+id="[^"]*"', '', m.group(1))
        sid = "sec-%d" % (len(heads) + 1)
        heads.append((sid, re.sub(r'<[^>]+>', '', m.group(2)).strip()))
        return '<h2%s id="%s">%s</h2>' % (attrs, sid, m.group(2))
    content = re.sub(r'<h2([^>]*?)>(.*?)</h2>', add_id, content, flags=re.S)

    # ตำแหน่งแทรก: หลังรูปเปิดบทความ (ถ้ามี)
    m = re.match(r'\s*<img[^>]*>', content)
    pos = m.end() if m else 0

    blocks = build_answer(entry["answer"])
    if len(heads) >= 3:
        blocks += build_toc(heads)
    content = content[:pos] + blocks + content[pos:]
    content += build_faq(entry["faq"])

    body = content + related
    s = head + sep + body + endsep + tail
    s = s.replace("</head>", build_ld(fname, entry) + "</head>", 1)

    if s != orig:
        open(path, "w", encoding="utf-8").write(s)
        changed.append("%s (h2:%d, faq:%d%s)" % (fname, len(heads), len(entry["faq"]),
                                                 ", howto" if entry.get("howto") else ""))

print("อัปเดต %d ไฟล์" % len(changed))
for c in changed:
    print(" ", c)
