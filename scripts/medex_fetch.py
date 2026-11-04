#!/usr/bin/env python3
"""
medex_fetch.py  -  polite index / resolve / fetch / parse tool for the BanglaMed MedEx pilot (P2).

Stages (run all, or one with --stage):
  index    Read the public A-Z generics listing (https://medex.com.bd/generics?page=1..N, ~84 pages)
           and write out/index/generics_index.csv   (id, slug, name, brand_count, url)
  resolve  Match the names in the search list to index entries by NAME (never by remembered ID).
           Writes out/resolve_log.csv. Anything ambiguous or missing is NOT guessed: you decide it in
           overrides.csv (columns: query,id) and re-run.
  fetch    Save the raw English and Bangla page for every resolved drug:
           out/raw/{id}_{slug}_{en|bn}.html, plus out/manifest.jsonl (url, time, status, sha256).
  parse    Turn the saved pages into out/sections.jsonl and out/parse_qc.csv.

Politeness: reads robots.txt first and stops if it forbids the pages; one request every --delay
seconds (default 2.5 plus a small random jitter); identifying User-Agent; backs off on 429/5xx;
never re-downloads a page that is already saved (use --force to override).

Typical use
  pip install requests beautifulsoup4
  python medex_fetch.py --contact you@example.com --tier 1 --limit 20
  # look at out/resolve_log.csv, fix anything ambiguous in overrides.csv, run again

Parse saved pages only (no network):
  python medex_fetch.py --parse-only path/to/folder_with_saved_html
"""
import argparse, csv, hashlib, importlib.util, json, random, re, sys, time, unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib import robotparser

BASE = "https://medex.com.bd"

# canonical section key  ->  (English heading, Bangla heading). Compared after NFC normalisation.
SECTION_MAP = {
    "indications": ("Indications", "নির্দেশনা"),
    "description": ("Description", "বিবরণ"),
    "pharmacology": ("Pharmacology", "ফার্মাকোলজি"),
    "dosage_administration": ("Dosage & Administration", "মাত্রা ও সেবনবিধি"),
    "dosage": ("Dosage", "ঔষধের মাত্রা"),            # some pages split the section in two
    "administration": ("Administration", "সেবনবিধি"),
    "interaction": ("Interaction", "ঔষধের মিথষ্ক্রিয়া"),
    "contraindications": ("Contraindications", "প্রতিনির্দেশনা"),
    "side_effects": ("Side Effects", "পার্শ্ব প্রতিক্রিয়া"),
    "pregnancy_lactation": ("Pregnancy & Lactation", "গর্ভাবস্থায় ও স্তন্যদানকালে"),
    "precautions": ("Precautions & Warnings", "সতর্কতা"),
    "special_populations": ("Use in Special Populations", "বিশেষ ক্ষেত্রে ব্যবহার"),
    "overdose": ("Overdose Effects", "মাত্রাধিক্যতা"),
    "therapeutic_class": ("Therapeutic Class", "থেরাপিউটিক ক্লাস"),
    "reconstitution": ("Reconstitution", "পুনর্গঠন প্রণালী"),
    "storage": ("Storage Conditions", "সংরক্ষণ"),
    "composition": ("Composition", "উপাদান"),
    "chemical_structure": ("Chemical Structure", "রাসায়নিক গঠন"),
}
# headings that start with these prefixes are page furniture, not drug-label sections
PREFIX_MAP = {"Common Questions about": "faq"}


def nfc(s):
    return unicodedata.normalize("NFC", re.sub(r"\s+", " ", s or "")).strip()


_HEAD_LOOKUP = {}
for _k, (_en, _bn) in SECTION_MAP.items():
    _HEAD_LOOKUP[nfc(_en)] = _k
    if _bn:
        _HEAD_LOOKUP[nfc(_bn)] = _k


def count_scripts(t):
    bn = sum("ঀ" <= c <= "৿" for c in t)
    en = sum(c.isascii() and c.isalpha() for c in t)
    return bn, en


# ------------------------------------------------------------------ parsing (offline-testable)
def parse_listing(html):
    """Return (entries, last_page). entries: list of dict(id, slug, name, brands, url)."""
    from bs4 import BeautifulSoup
    s = BeautifulSoup(html, "html.parser")
    entries = []
    for a in s.select("a.hoverable-block"):
        m = re.search(r"/generics/(\d+)/([^/?#]+)", a.get("href", ""))
        if not m:
            continue
        t = a.select_one(".dcind-title")
        name = nfc(t.get_text(" ", strip=True)) if t else m.group(2)
        b = a.select_one(".dcind")
        mb = re.search(r"(\d+)", b.get_text(" ", strip=True)) if b else None
        entries.append(dict(id=m.group(1), slug=m.group(2), name=name,
                            brands=int(mb.group(1)) if mb else 0,
                            url=f"{BASE}/generics/{m.group(1)}/{m.group(2)}"))
    pages = [int(x) for x in re.findall(r"[?&]page=(\d+)", html)]
    return entries, (max(pages) if pages else 1)


def clean_body(text):
    # some English bodies hold a truncated copy, then "... Read more", then the full text
    if "... Read more" in text:
        text = text.split("... Read more", 1)[1]
    return nfc_keep_lines(text)


def nfc_keep_lines(text):
    lines = [x for x in (nfc(x) for x in text.split("\n")) if x]
    # a few pages wrap every word in its own element, which gives one word per line;
    # real list items are longer, so rejoin only when nearly every line is a single short token
    if len(lines) >= 15:
        lens = sorted(len(x) for x in lines)
        if lens[len(lens) // 2] <= 6:
            return " ".join(lines)
    return "\n".join(lines)


def page_language(url, html):
    m = re.search(r"/(en|bn)(?:[/?#]|$)", url or "")
    if m:
        return m.group(1)
    # default MedEx page is English
    return "en"


def parse_page(html, source_name=""):
    """Parse one saved generic page. Returns (meta, sections, qc_flags)."""
    from bs4 import BeautifulSoup
    s = BeautifulSoup(html, "html.parser")
    mu = re.search(r'og:url" content="([^"]+)"', html)
    url = mu.group(1) if mu else ""
    mid = re.search(r"/generics/(\d+)/([^/?#]+)", url)
    meta = dict(url=url, id=mid.group(1) if mid else "", slug=mid.group(2) if mid else "",
                lang=page_language(url, html), source=source_name)
    t = s.find("title")
    meta["title"] = nfc(t.get_text()) if t else ""
    sections, qc = [], []
    heads, bodies = s.select(".ac-header"), s.select(".ac-body")
    if len(heads) != len(bodies):
        qc.append("header_body_count_mismatch")
    for i, (h, b) in enumerate(zip(heads, bodies), 1):
        ht = nfc(h.get_text(" ", strip=True))
        raw_text = b.get_text("\n", strip=True)
        bt = clean_body(raw_text)
        key = _HEAD_LOOKUP.get(ht)
        if key is None:
            key = next((v for p, v in PREFIX_MAP.items() if ht.startswith(p)), "unmapped")
        if key == "unmapped":
            qc.append(f"unmapped_heading:{ht}")
        lb, le = count_scripts(ht)
        bb, be = count_scripts(bt)
        if bb == 0 and be == 0:
            status = "empty"
        elif bb >= be:
            status = "bangla_body"
        else:
            status = "bangla_label_only" if lb > le else "english_only"
        sections.append(dict(id=meta["id"], slug=meta["slug"], lang=meta["lang"], idx=i, key=key,
                             heading=ht, status=status, chars=len(bt), text=bt))
    if not sections:
        qc.append("no_sections_found")
    elif meta["lang"] == "bn":
        # a /bn URL does not guarantee Bangla text: some drugs fall back to the English page
        tb = sum(x["chars"] for x in sections if x["status"] == "bangla_body")
        tt = sum(x["chars"] for x in sections) or 1
        if tb / tt < 0.2:
            qc.append("bn_page_has_no_bangla_body")
    return meta, sections, qc


# ------------------------------------------------------------------ name resolution
def tokens(s):
    return re.findall(r"[a-z0-9]+", unicodedata.normalize("NFKC", s).lower())


def score_candidate(query_tokens, query_is_combo, name):
    nt = tokens(name)
    n_combo = "+" in name
    if nt == query_tokens:
        return 100
    if n_combo and not query_is_combo:
        base = 40 if all(t in nt for t in query_tokens) else 0
        return base - 10 if base else 0
    if nt[: len(query_tokens)] == query_tokens:
        return 80 - min(len(nt) - len(query_tokens), 15)
    if all(t in nt for t in query_tokens):
        return 55 - min(len(nt) - len(query_tokens), 15)
    return 0


def resolve_one(query, index):
    qt = tokens(query)
    combo = "+" in query
    scored = []
    for e in index:
        sc = score_candidate(qt, combo, e["name"])
        if sc > 0:
            scored.append((sc, e))
    scored.sort(key=lambda x: (-x[0], -x[1]["brands"], x[1]["name"]))
    if not scored:
        return "none", None, scored
    top = scored[0]
    second = scored[1][0] if len(scored) > 1 else 0
    if top[0] >= 70 and top[0] - second >= 10:
        return "resolved", top[1], scored
    return "ambiguous", top[1], scored


# ------------------------------------------------------------------ networking
class Fetcher:
    def __init__(self, contact, delay, ignore_robots=False):
        import requests
        self.requests = requests
        self.delay = delay
        self.ua = f"BanglaMedResearch/0.1 (academic research, MBSTU; contact: {contact})"
        self.sess = requests.Session()
        self.sess.headers.update({"User-Agent": self.ua, "Accept-Language": "en,bn;q=0.8"})
        self.rp = None
        self.ignore_robots = ignore_robots
        self._last = 0.0

    def load_robots(self, outdir):
        r = self.sess.get(BASE + "/robots.txt", timeout=30)
        (outdir / "robots.txt").write_text(r.text, encoding="utf-8")
        if r.status_code == 404:
            self.rp = None
            print("robots.txt: none found (404) - nothing is disallowed.")
            return
        if r.status_code != 200:
            sys.exit(f"robots.txt returned HTTP {r.status_code}; stopping. Check it in a browser first.")
        self.rp = robotparser.RobotFileParser()
        self.rp.parse(r.text.splitlines())
        print("robots.txt saved to", outdir / "robots.txt")

    def allowed(self, url):
        return self.ignore_robots or self.rp is None or self.rp.can_fetch(self.ua, url)

    def get(self, url, tries=4):
        if not self.allowed(url):
            return None, f"blocked_by_robots"
        for k in range(tries):
            wait = self.delay + random.uniform(0, 0.5) - (time.time() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.time()
            try:
                r = self.sess.get(url, timeout=40)
            except self.requests.RequestException as ex:
                time.sleep(5 * (k + 1))
                last = f"error:{type(ex).__name__}"
                continue
            if r.status_code == 200:
                return r, "ok"
            if r.status_code in (404, 410):
                return r, f"http_{r.status_code}"
            if r.status_code in (429, 500, 502, 503, 504):
                ra = r.headers.get("Retry-After")
                time.sleep(int(ra) if ra and ra.isdigit() else 15 * (k + 1))
                last = f"http_{r.status_code}"
                continue
            return r, f"http_{r.status_code}"
        return None, last


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ------------------------------------------------------------------ stages
def stage_index(f, out, refresh, max_pages):
    idxdir = out / "index"
    idxdir.mkdir(parents=True, exist_ok=True)
    rows, seen = [], set()
    p1 = idxdir / "generics_page_001.html"
    if refresh or not p1.exists():
        r, st = f.get(f"{BASE}/generics?page=1")
        if r is None or st != "ok":
            sys.exit(f"Could not read listing page 1: {st}")
        p1.write_bytes(r.content)
    entries, last = parse_listing(p1.read_text(encoding="utf-8", errors="replace"))
    last = min(last, max_pages) if max_pages else last
    print(f"listing: {last} pages")
    allentries = list(entries)
    for n in range(2, last + 1):
        p = idxdir / f"generics_page_{n:03d}.html"
        if refresh or not p.exists():
            r, st = f.get(f"{BASE}/generics?page={n}")
            if r is None or st != "ok":
                print(f"  page {n}: {st} (skipped)")
                continue
            p.write_bytes(r.content)
        es, _ = parse_listing(p.read_text(encoding="utf-8", errors="replace"))
        allentries += es
        if n % 10 == 0:
            print(f"  page {n}/{last}")
    for e in allentries:
        if e["id"] not in seen:
            seen.add(e["id"])
            rows.append(e)
    with open(idxdir / "generics_index.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=["id", "slug", "name", "brands", "url"])
        w.writeheader()
        w.writerows(rows)
    print(f"index: {len(rows)} generics -> {idxdir/'generics_index.csv'}")
    return rows


def load_index(out):
    p = out / "index" / "generics_index.csv"
    if not p.exists():
        sys.exit("No index yet. Run: --stage index")
    rows = list(csv.DictReader(open(p, encoding="utf-8-sig")))
    for r in rows:
        r["brands"] = int(r.get("brands") or 0)
    return rows


def load_targets(args):
    if args.names:
        return [dict(query=x.strip(), tier=1, role="", scope="") for x in args.names.split(",") if x.strip()]
    spec = importlib.util.spec_from_file_location("searchlist", args.targets)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    t = [d for d in mod.MCH_SEARCH_LIST if (args.tier == 0 or d["tier"] <= args.tier)]
    return t[: args.limit] if args.limit else t


def stage_resolve(args, out, targets):
    index = load_index(out)
    over = {}
    if args.overrides and Path(args.overrides).exists():
        for r in csv.DictReader(open(args.overrides, encoding="utf-8-sig")):
            over[r["query"].strip().lower()] = r["id"].strip()
    by_id = {e["id"]: e for e in index}
    rows = []
    for d in targets:
        q = d["query"]
        if q.lower() in over:
            e = by_id.get(over[q.lower()])
            status = "override" if e else "override_id_not_in_index"
            scored = []
        else:
            status, e, scored = resolve_one(q, index)
            if status == "none":
                e = None
        cands = " | ".join(f"{x[1]['id']}:{x[1]['name']}({x[0]})" for x in scored[:4])
        rows.append(dict(query=q, status=status, id=e["id"] if e and status in ("resolved", "override") else "",
                         slug=e["slug"] if e and status in ("resolved", "override") else "",
                         matched_name=e["name"] if e else "", tier=d.get("tier", ""),
                         role=d.get("role", ""), candidates=cands,
                         list_id_unverified=d.get("medex_id_unverified", "") or ""))
    with open(out / "resolve_log.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    c = {}
    for r in rows:
        c[r["status"]] = c.get(r["status"], 0) + 1
    print("resolve:", c, "->", out / "resolve_log.csv")
    mism = [r for r in rows if r["status"] == "resolved" and r["list_id_unverified"] and r["id"] != str(r["list_id_unverified"])]
    if mism:
        print("ID differs from the remembered list ID for:", ", ".join(f"{r['query']} ({r['list_id_unverified']}->{r['id']})" for r in mism))
    return rows


def stage_fetch(f, out, rows, force, with_brands):
    raw = out / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    man = open(out / "manifest.jsonl", "a", encoding="utf-8")
    todo = [r for r in rows if r["status"] in ("resolved", "override") and r["id"]]
    langs = ["en", "bn"] + (["brand-names"] if with_brands else [])
    for i, r in enumerate(todo, 1):
        for lang in langs:
            path = raw / f"{r['id']}_{r['slug']}_{lang}.html"
            if path.exists() and not force:
                continue
            url = f"{BASE}/generics/{r['id']}/{r['slug']}/{lang}"
            resp, st = f.get(url)
            if resp is not None and st == "http_404" and lang == "en":
                resp, st = f.get(f"{BASE}/generics/{r['id']}/{r['slug']}")
            if resp is not None and st == "ok":
                path.write_bytes(resp.content)
            man.write(json.dumps(dict(query=r["query"], id=r["id"], lang=lang, url=url, status=st,
                                      fetched_at=now(), sha256=sha256(resp.content) if resp is not None and st == "ok" else "",
                                      bytes=len(resp.content) if resp is not None and st == "ok" else 0,
                                      path=str(path) if st == "ok" else ""), ensure_ascii=False) + "\n")
            man.flush()
            print(f"[{i}/{len(todo)}] {r['query']} /{lang}: {st}")
    man.close()


def stage_parse(folder, out):
    files = sorted(Path(folder).glob("*.html"))
    all_sections, qcrows = [], []
    for p in files:
        html = p.read_text(encoding="utf-8", errors="replace")
        if "brand-names" in p.name:
            continue
        meta, secs, qc = parse_page(html, p.name)
        all_sections += secs
        qcrows.append(dict(file=p.name, id=meta["id"], slug=meta["slug"], lang=meta["lang"],
                           n_sections=len(secs), flags=";".join(qc)))
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "sections.jsonl", "w", encoding="utf-8") as fh:
        for s in all_sections:
            fh.write(json.dumps(s, ensure_ascii=False) + "\n")
    with open(out / "parse_qc.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=["file", "id", "slug", "lang", "n_sections", "flags"])
        w.writeheader()
        w.writerows(qcrows)
    print(f"parsed {len(files)} files, {len(all_sections)} sections -> {out/'sections.jsonl'}")
    bad = [r for r in qcrows if r["flags"]]
    if bad:
        print("files with parse flags (see parse_qc.csv):", len(bad))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", choices=["index", "resolve", "fetch", "parse", "all"], default="all")
    ap.add_argument("--out", default="medex_out")
    ap.add_argument("--targets", default=str(Path(__file__).with_name("medex_mch_search_list.py")))
    ap.add_argument("--names", help="comma-separated names instead of the search list")
    ap.add_argument("--tier", type=int, default=1, help="1 = tier-1 only, 2 = tiers 1+2, 0 = all")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--overrides", default="overrides.csv", help="csv with columns query,id")
    ap.add_argument("--contact", help="your email, put in the User-Agent (required for network stages)")
    ap.add_argument("--delay", type=float, default=2.5)
    ap.add_argument("--max-pages", type=int, default=0, help="debug: stop the index after N pages")
    ap.add_argument("--refresh-index", action="store_true")
    ap.add_argument("--force", action="store_true", help="re-download pages already saved")
    ap.add_argument("--with-brands", action="store_true", help="also save each generic's brand-names page")
    ap.add_argument("--ignore-robots", action="store_true", help="NOT recommended")
    ap.add_argument("--parse-only", metavar="FOLDER", help="parse saved .html files in FOLDER, no network")
    args = ap.parse_args()
    out = Path(args.out)
    if args.parse_only:
        stage_parse(args.parse_only, out)
        return
    out.mkdir(parents=True, exist_ok=True)
    need_net = args.stage in ("index", "fetch", "all")
    f = None
    if need_net:
        if not args.contact:
            sys.exit("Please pass --contact your@email (it goes in the User-Agent so the site can reach you).")
        f = Fetcher(args.contact, args.delay, args.ignore_robots)
        f.load_robots(out)
    if args.stage in ("index", "all"):
        stage_index(f, out, args.refresh_index, args.max_pages)
    rows = None
    if args.stage in ("resolve", "fetch", "all"):
        rows = stage_resolve(args, out, load_targets(args))
    if args.stage in ("fetch", "all"):
        stage_fetch(f, out, rows, args.force, args.with_brands)
    if args.stage in ("parse", "all"):
        stage_parse(out / "raw", out)


if __name__ == "__main__":
    main()
