import os, json, time, sqlite3, logging, urllib.parse, re
import urllib3
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import anthropic
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ── PROFILE ───────────────────────────────────────────────────────────────────

PROFILE = """
David DiFrancescoMarino — Canadian-Italian dual citizen (unrestricted Canada + EU work rights).
Currently Ottawa-based, willing to relocate to Paris immediately.

Education:
- INSEAD MBA, January 2027 promotion (Private Equity specialization). Open to Aug 2026 intake if funded.
- BSc Translational Molecular Medicine, University of Ottawa (Summa Cum Laude, Dean's merit scholarship x4).

Experience:
- Founder, Quiver (2025–): techno-economic modeling for LNG/hydrogen/e-fuels investors; €50B+ pipeline screened.
- Senior Consultant, Guidehouse (2022–2025): led commercial DD for EQT biomethane acquisition; DOE $1.25B filing; launched Guidehouse Canada hydrogen practice.
- Independent consultant for InvestChile and Embassy of Japan to Canada — clean energy G2B facilitation.

Specialization: infrastructure PE, clean energy, hydrogen, e-fuels, biomethane, energy transition finance.
Languages: English (native), French (C1-C2), Italian (B1), Japanese (basics).

TARGET ROLES: MBA-level internships (summer associate, MBA intern, pre-MBA internship, stage, stagiaire).
Seniority tier: Associate / Summer Associate / MBA Intern — NOT entry-level analyst, NOT Director+.
Start window: August 2026 onwards (any duration, including multi-month stages common in France).
Sectors (in priority order): Infrastructure PE, Clean energy / hydrogen / e-fuels, Climate & Impact VC,
  Policy / public finance (EDC, CIB, SDTC, BDC, BPI).
Geographic preference: Paris, Ottawa, Toronto, Montreal, Singapore, remote-EU.
"""

# ── SCHOLARSHIP SOURCES (verified working URLs) ───────────────────────────────

SCHOLARSHIP_SOURCES = [
    {"name": "EduCanada",              "url": "https://www.educanada.ca/scholarships-bourses/index.aspx"},
    {"name": "Canada.ca Scholarships", "url": "https://www.canada.ca/en/services/benefits/education/scholarships.html"},
    {"name": "Vanier Canada",          "url": "https://vanier.gc.ca/en/home-accueil.html"},
    {"name": "Erasmus Mundus",         "url": "https://www.eacea.ec.europa.eu/scholarships/erasmus-mundus-catalogue_en"},
    {"name": "Eiffel Excellence",      "url": "https://www.campusfrance.org/en/eiffel-scholarship-program-of-excellence"},
]

# ── FIRMS ─────────────────────────────────────────────────────────────────────

FIRMS = [
    # Paris — Infrastructure PE / Energy Transition
    {"name": "Meridiam",                     "careers": "https://meridiam.com/careers/",                                     "news": None},
    {"name": "Ardian",                       "careers": "https://ardian.wd103.myworkdayjobs.com/ArdianCareers",              "news": "https://www.ardian.com/newsroom"},
    {"name": "Antin Infrastructure",         "careers": "https://www.antin-ip.com/careers/",                                 "news": "https://www.antin-ip.com/media/"},
    {"name": "InfraVia Capital Partners",    "careers": "https://www.infraviacapital.com/careers",                           "news": "https://www.infraviacapital.com/media"},
    {"name": "Tikehau Capital",              "careers": "https://www.tikehaucapital.com/en/careers",                         "news": "https://www.tikehaucapital.com/en/newsroom"},
    {"name": "Mirova",                       "careers": "https://www.mirova.com/en/career",                                  "news": "https://www.mirova.com/en/news-and-publications"},
    {"name": "Eiffel Investment Group",      "careers": "https://eiffel-ig.com/en/join-us-2/",                               "news": "https://eiffel-ig.com/en/news/"},
    {"name": "Omnes Capital",                "careers": "https://www.omnescapital.com/en/join-us",                           "news": "https://www.omnescapital.com/en/news"},
    {"name": "Asterion Industrial Partners", "careers": "https://www.asterionindustrial.com/join-us/",                       "news": "https://www.asterionindustrial.com/news-and-insights/"},
    {"name": "Energy Impact Partners",       "careers": "https://www.energyimpactpartners.com/join-our-team/",               "news": "https://www.energyimpactpartners.com/news-insights/"},
    {"name": "Vauban Infrastructure",        "careers": "https://www.vauban-ip.com/careers/",                                "news": "https://www.vauban-ip.com/news/"},
    {"name": "Hy24 Partners",                "careers": "https://www.hy24partners.com/join-us/",                             "news": "https://www.hy24partners.com/news-and-insights/"},
    {"name": "Demeter Partners",             "careers": "https://demeter-im.com/en/careers-3/",                              "news": "https://demeter-im.com/en/news/"},
    # Copenhagen / Nordic
    {"name": "Copenhagen Infrastructure Partners", "careers": "https://cipartners.dk/careers/",                              "news": "https://cipartners.dk/news/"},
    # Stockholm
    {"name": "EQT",                          "careers": "https://eqtgroup.com/careers",                                      "news": "https://eqtgroup.com/news"},
    # Singapore / APAC
    {"name": "Actis",                        "careers": "https://www.act.is/careers/",                                       "news": "https://www.act.is/news-and-insights/"},
    {"name": "Pentagreen Capital",           "careers": "https://www.pentagreencapital.com/careers",                         "news": "https://www.pentagreencapital.com/news"},
    {"name": "Clifford Capital",             "careers": "https://www.cliffordcapital.sg/careers",                            "news": None},
    {"name": "Equis",                        "careers": "https://equis.com/careers/",                                        "news": "https://equis.com/news/"},
    {"name": "Temasek",                      "careers": "https://www.temasek.com.sg/en/careers",                             "news": None},
    # Toronto
    {"name": "Brookfield",                   "careers": "https://careers.brookfield.com/jobs",                               "news": "https://bam.brookfield.com/press-releases"},
    {"name": "Northleaf",                    "careers": "https://www.northleafcapital.com/careers/",                         "news": "https://www.northleafcapital.com/news/"},
    {"name": "Fiera Infrastructure",         "careers": "https://fierainfrastructure.com/careers/",                          "news": "https://fierainfrastructure.com/news/"},
    {"name": "ArcTern Ventures",             "careers": "https://arcternventures.com/careers/",                              "news": "https://arcternventures.com/news/"},
    {"name": "BDC Capital",                  "careers": "https://www.bdc.ca/en/bdc-capital/about/careers",                   "news": "https://www.bdc.ca/en/bdc-capital/blog"},
    # Ottawa / Canadian public finance
    {"name": "EDC",                          "careers": "https://www.edc.ca/en/about-us/careers.html",                       "news": "https://www.edc.ca/en/about-us/newsroom.html"},
    {"name": "SDTC",                         "careers": "https://www.sdtc.ca/en/careers/",                                   "news": "https://www.sdtc.ca/en/news/"},
    {"name": "Canada Infrastructure Bank",   "careers": "https://cib-bic.ca/en/careers/",                                    "news": "https://cib-bic.ca/en/media/news-releases/"},
    # Global cleantech VC
    {"name": "Breakthrough Energy Ventures", "careers": "https://breakthroughenergy.org/work-with-us/",                      "news": "https://breakthroughenergy.org/articles/"},
]

# ── KEYWORDS (EN + FR) ────────────────────────────────────────────────────────

KEYWORDS = [
    # Role seniority (EN)
    "mba intern","mba internship","summer associate","pre-mba","associate intern",
    "investment associate","investment intern","internship","fellow","fellowship",
    # Role seniority (FR)
    "stage","stagiaire","alternance","vie","volontariat international","apprenti",
    "stage de fin d'études","césure","stage mba","stagiaire mba","stage associé",
    # Sectors (EN)
    "infrastructure","private equity","clean energy","energy transition",
    "renewables","hydrogen","e-fuels","biomethane","biogas","sustainability",
    "climate","impact","decarbonization","venture capital",
    # Sectors (FR)
    "infrastructure","capital-investissement","énergie propre","transition énergétique",
    "énergies renouvelables","hydrogène","e-carburants","biométhane","durabilité",
    "climat","décarbonation","capital-risque","investissement à impact",
    # Scholarship terms
    "scholarship","bourse","bourses","mba scholarship","merit scholarship",
    "fellowship","grant","financement","aide financière",
]

EXCLUSIONS = [
    # Wrong seniority
    "phd only","undergraduate only","senior director","managing director",
    "vp of","chief ","15+ years","20+ years","head of ","partner, ",
    # Wrong citizenship
    "us citizen only","us citizenship required","uk nationals only",
    "green card required","security clearance required",
    # Wrong role type
    "software engineer","data engineer","devops","full stack","backend developer",
    "développeur","ingénieur logiciel",
]

# ── DATABASE ──────────────────────────────────────────────────────────────────

def init_db(path="data/seen.db"):
    os.makedirs("data", exist_ok=True)
    con = sqlite3.connect(path)
    con.execute("""CREATE TABLE IF NOT EXISTS seen (
        url  TEXT PRIMARY KEY,
        kind TEXT,
        seen_at TEXT
    )""")
    con.commit()
    return con

def filter_unseen(con, items, kind):
    urls = {r[0] for r in con.execute("SELECT url FROM seen WHERE kind=?", (kind,))}
    new  = [i for i in items if i.get("url","") not in urls]
    if new:
        con.executemany(
            "INSERT OR IGNORE INTO seen VALUES (?,?,datetime('now'))",
            [(i["url"], kind) for i in new]
        )
        con.commit()
    return new

# ── SCRAPING ──────────────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9,fr;q=0.8,it;q=0.7",
}

def scrape(url, name):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20, verify=False,
                         allow_redirects=True)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script","style","nav","footer"]):
            tag.decompose()
        text = " ".join(soup.get_text(" ", strip=True).split())
        log.info(f"  ✓ {name} ({len(text)} chars)")
        return text[:6000]
    except Exception as e:
        log.warning(f"  ✗ {name}: {str(e)[:100]}")
        return ""

def google_linkedin_search(firm_name):
    """Finds recent LinkedIn job postings via Google. Biases toward internships/stages."""
    query = f'site:linkedin.com/jobs "{firm_name}" (intern OR stage OR stagiaire OR associate)'
    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&tbs=qdr:w"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, verify=False)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        results = []
        for g in soup.select("div.g, div.tF2Cxc")[:3]:
            link = g.find("a", href=True)
            title = g.find("h3")
            snippet_tag = g.find("div", {"class": ["VwiC3b", "s3v9rd"]})
            if link and title:
                results.append({
                    "title": title.get_text(strip=True),
                    "url": link["href"],
                    "snippet": snippet_tag.get_text(" ", strip=True) if snippet_tag else ""
                })
        log.info(f"  🔍 LinkedIn via Google for {firm_name}: {len(results)} hits")
        return results
    except Exception as e:
        log.warning(f"  🔍 LinkedIn search failed for {firm_name}: {str(e)[:80]}")
        return []

def keyword_prefilter(text):
    t = text.lower()
    if any(ex in t for ex in EXCLUSIONS):
        return False
    return any(kw in t for kw in KEYWORDS)

# ── CLAUDE FILTER ─────────────────────────────────────────────────────────────

def claude_filter(items, kind):
    if not items:
        return []
    slim = [{"name": i["name"], "snippet": i.get("text","")[:500] or i.get("snippet",""), "url": i["url"]}
            for i in items]
    prompt = f"""You are filtering {kind} for this person. Be strict — only flag items
that are concretely a match for the target role tier and sectors.

PROFILE:
{PROFILE}

ITEMS (JSON):
{json.dumps(slim, indent=2, ensure_ascii=False)}

RULES for {kind}:
- For jobs: only MBA-tier internships / stages / summer associate / pre-MBA roles.
  Reject analyst-level roles, senior director+, or unrelated tech roles.
  Items in French (stage, stagiaire, alternance) are equally valid.
- For scholarships: only MBA or graduate-level awards, open to Canadian or EU citizens,
  with deadlines or intakes compatible with Aug 2026 or Jan 2027 start.
- Reject generic "join our team" pages with no specific opening.

Return ONLY a valid JSON array. Each object must have:
- name, url, reason (1 sentence, in English), deadline (if visible, else null),
  sector (for jobs) or intake_year (for scholarships).

If nothing qualifies, return []. Output raw JSON only — no preamble, no markdown fences."""
    try:
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1200,
            messages=[{"role": "user", "content": prompt}]
        )
        text = msg.content[0].text.strip()
        log.info(f"Claude raw ({kind}): {text[:200]}")
        # Robustly extract JSON array regardless of markdown fences or preamble
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            text = match.group(0)
        if not text:
            return []
        return json.loads(text)
    except Exception as e:
        log.warning(f"Claude filter error ({kind}): {e}")
        return []

# ── MAIN ──────────────────────────────────────────────────────────────────────

def run():
    con = init_db()
    results = {"scholarships": [], "jobs": []}

    # --- Scholarships ---
    log.info("=== Scholarships ===")
    raw_schol = []
    for src in SCHOLARSHIP_SOURCES:
        text = scrape(src["url"], src["name"])
        if text and keyword_prefilter(text):
            raw_schol.append({"name": src["name"], "url": src["url"], "text": text})
        time.sleep(1.5)
    new_schol = filter_unseen(con, raw_schol, "scholarship")
    log.info(f"{len(new_schol)} new scholarship sources to filter")
    results["scholarships"] = claude_filter(new_schol, "scholarships")

    # --- Jobs / Internships ---
    log.info("=== Jobs / Internships ===")
    raw_jobs = []
    for firm in FIRMS:
        # Careers page
        text = scrape(firm["careers"], f"{firm['name']} [careers]")
        if text and keyword_prefilter(text):
            raw_jobs.append({"name": f"{firm['name']} — Careers", "url": firm["careers"], "text": text})
        time.sleep(1.2)

        # News/insights page
        if firm.get("news"):
            news_text = scrape(firm["news"], f"{firm['name']} [news]")
            if news_text and keyword_prefilter(news_text):
                raw_jobs.append({"name": f"{firm['name']} — News", "url": firm["news"], "text": news_text})
            time.sleep(1.2)

        # LinkedIn via Google (past week, internships/stages/associates)
        for hit in google_linkedin_search(firm["name"]):
            raw_jobs.append({"name": f"{firm['name']} — LinkedIn", "url": hit["url"],
                             "text": hit["title"] + " " + hit["snippet"]})
        time.sleep(2.0)

    new_jobs = filter_unseen(con, raw_jobs, "job")
    log.info(f"{len(new_jobs)} new job items to filter")
    results["jobs"] = claude_filter(new_jobs, "jobs / internships")

    # --- Output ---
    out_path = "data/latest_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    log.info(f"\n✅ Done — {len(results['scholarships'])} scholarships, "
             f"{len(results['jobs'])} jobs → {out_path}")
    return results

if __name__ == "__main__":
    run()