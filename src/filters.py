"""
Deterministic Python filters.

These run BEFORE Claude — they cut obvious mismatches at zero cost.
Only genuinely ambiguous items reach Claude for final judgment.
"""
import re

# Role tier patterns — MBA-level internships and stages only
ROLE_TIER_POSITIVE = [
    r"\bintern(ship)?\b", r"\bstage\b", r"\bstagiaire\b", r"\balternance\b",
    r"\bapprenti(e|ssage)?\b", r"\bvie\b", r"\bv\.i\.e\.\b",
    r"\bsummer associate\b", r"\bpre[- ]?mba\b", r"\bmba\b", r"\bfellow(ship)?\b",
    r"\bcésure\b", r"\bassociate\b",
]

ROLE_TIER_NEGATIVE = [
    r"\bsenior director\b", r"\bmanaging director\b", r"\bhead of\b",
    r"\bvp of\b", r"\bchief \b", r"\bpartner,\b",
    r"\b15\+? years?\b", r"\b20\+? years?\b", r"\b10\+? years?\b",
    r"\bphd\b", r"\bpost[- ]?doc\b",
    r"\bsoftware engineer\b", r"\bdata engineer\b", r"\bdevops\b",
    r"\bfull[- ]?stack\b", r"\bbackend\b", r"\bfrontend\b",
    r"\bdéveloppeur\b", r"\bingénieur logiciel\b",
    r"\bus citizen(ship)? (only|required)\b",
]

SECTOR_POSITIVE = [
    r"\binfrastructure\b", r"\bprivate equity\b", r"\bcapital[- ]investissement\b",
    r"\bclean energy\b", r"\bénergie propre\b",
    r"\benergy transition\b", r"\btransition énergétique\b",
    r"\brenewables?\b", r"\bénergies renouvelables\b",
    r"\bhydrogen\b", r"\bhydrogène\b",
    r"\be[- ]fuels?\b", r"\be[- ]carburants?\b",
    r"\bbiomethane\b", r"\bbiométhane\b", r"\bbiogas\b",
    r"\bsustainability\b", r"\bdurabilité\b",
    r"\bclimate\b", r"\bclimat\b",
    r"\bimpact\b", r"\bdecarbonization\b", r"\bdécarbonation\b",
    r"\bventure capital\b", r"\bcapital[- ]risque\b",
    r"\binvestment\b", r"\binvestissement\b",
]

def matches_any(text, patterns):
    t = text.lower()
    return any(re.search(p, t, re.IGNORECASE) for p in patterns)

def is_target_role_tier(job):
    """True if the job title matches MBA-tier patterns and doesn't match negatives."""
    title = job.get("title", "")
    dept = job.get("department", "")
    blob = f"{title} {dept}"
    if matches_any(blob, ROLE_TIER_NEGATIVE):
        return False
    return matches_any(blob, ROLE_TIER_POSITIVE)

def is_target_sector(job):
    """True if title/dept/description touches priority sectors."""
    blob = f"{job.get('title','')} {job.get('department','')} {job.get('description','')}"
    return matches_any(blob, SECTOR_POSITIVE)

def is_target_geography(job):
    """Prefers Paris, Canada, Singapore, remote-EU. Rejects US-only roles
    unless they look remote-friendly or global."""
    loc = (job.get("location") or "").lower()
    if not loc:
        return True  # ambiguous — let Claude decide
    priority = ["paris","france","london","ottawa","toronto","montreal",
                "montréal","singapore","remote","europe","emea","global"]
    rejected = ["new york","san francisco","boston","chicago","los angeles",
                "nyc","texas","houston","denver","dubai","tokyo only"]
    if any(r in loc for r in rejected) and not any(p in loc for p in priority):
        return False
    return True

def apply_filters(jobs):
    """Apply all deterministic filters. Returns only jobs worth sending to Claude."""
    out = []
    for j in jobs:
        if not j.get("title"):
            continue
        if not is_target_role_tier(j):
            continue
        if not is_target_geography(j):
            continue
        # Don't require sector match here — Claude judges nuance
        out.append(j)
    return out