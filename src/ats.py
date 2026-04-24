"""
ATS (Applicant Tracking System) API clients.

Most corporate careers pages are front-ends for standardized ATS platforms.
These platforms expose public JSON APIs that return clean, structured job data —
zero HTML scraping, zero Claude tokens needed to extract structure.

Returns a list of dicts: [{title, location, department, url, posted_at}]
"""
import requests
import urllib3
import logging

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

def fetch_greenhouse(slug):
    """Greenhouse public API — returns all jobs for a company."""
    url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, verify=False)
        r.raise_for_status()
        jobs = r.json().get("jobs", [])
        return [{
            "title": j.get("title", ""),
            "location": j.get("location", {}).get("name", ""),
            "department": (j.get("departments") or [{}])[0].get("name", ""),
            "url": j.get("absolute_url", ""),
            "posted_at": j.get("updated_at", ""),
            "description": (j.get("content") or "")[:1500],
        } for j in jobs]
    except Exception as e:
        log.warning(f"  [Greenhouse/{slug}] failed: {str(e)[:80]}")
        return []

def fetch_lever(slug):
    """Lever public API."""
    url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, verify=False)
        r.raise_for_status()
        jobs = r.json()
        return [{
            "title": j.get("text", ""),
            "location": (j.get("categories") or {}).get("location", ""),
            "department": (j.get("categories") or {}).get("department", ""),
            "url": j.get("hostedUrl", ""),
            "posted_at": j.get("createdAt", ""),
            "description": (j.get("descriptionPlain") or "")[:1500],
        } for j in jobs]
    except Exception as e:
        log.warning(f"  [Lever/{slug}] failed: {str(e)[:80]}")
        return []

def fetch_workday(slug):
    """Workday exposes a JSON search endpoint on each careers page.
    slug format: 'tenant.wdN.myworkdayjobs.com/SiteName'
    """
    try:
        host_and_site = slug.split("/", 1)
        if len(host_and_site) != 2:
            return []
        host, site = host_and_site
        url = f"https://{host}/wday/cxs/{host.split('.')[0]}/{site}/jobs"
        payload = {"appliedFacets": {}, "limit": 50, "offset": 0, "searchText": ""}
        r = requests.post(url, json=payload, headers={**HEADERS, "Content-Type": "application/json"},
                          timeout=20, verify=False)
        r.raise_for_status()
        data = r.json()
        jobs = data.get("jobPostings", [])
        base = f"https://{host}/{site}"
        return [{
            "title": j.get("title", ""),
            "location": j.get("locationsText", ""),
            "department": j.get("bulletFields", [""])[0] if j.get("bulletFields") else "",
            "url": base + j.get("externalPath", ""),
            "posted_at": j.get("postedOn", ""),
            "description": "",  # Workday requires a second call per job for description
        } for j in jobs]
    except Exception as e:
        log.warning(f"  [Workday/{slug}] failed: {str(e)[:80]}")
        return []

def fetch_smartrecruiters(slug):
    """SmartRecruiters public API."""
    url = f"https://api.smartrecruiters.com/v1/companies/{slug}/postings"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, verify=False)
        r.raise_for_status()
        jobs = r.json().get("content", [])
        return [{
            "title": j.get("name", ""),
            "location": j.get("location", {}).get("city", ""),
            "department": j.get("department", {}).get("label", ""),
            "url": j.get("ref", ""),
            "posted_at": j.get("releasedDate", ""),
            "description": "",
        } for j in jobs]
    except Exception as e:
        log.warning(f"  [SmartRecruiters/{slug}] failed: {str(e)[:80]}")
        return []

def fetch_ashby(slug):
    """Ashby public API."""
    url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, verify=False)
        r.raise_for_status()
        jobs = r.json().get("jobs", [])
        return [{
            "title": j.get("title", ""),
            "location": j.get("locationName", ""),
            "department": j.get("teamName", ""),
            "url": j.get("jobUrl", ""),
            "posted_at": j.get("publishedDate", ""),
            "description": (j.get("descriptionPlain") or "")[:1500],
        } for j in jobs]
    except Exception as e:
        log.warning(f"  [Ashby/{slug}] failed: {str(e)[:80]}")
        return []

DISPATCH = {
    "greenhouse":      fetch_greenhouse,
    "lever":           fetch_lever,
    "workday":         fetch_workday,
    "smartrecruiters": fetch_smartrecruiters,
    "ashby":           fetch_ashby,
}

def fetch_ats_jobs(ats_type, slug):
    """Main entry: dispatches to the right ATS client."""
    if ats_type not in DISPATCH or not slug:
        return []
    jobs = DISPATCH[ats_type](slug)
    log.info(f"  ✓ [{ats_type}/{slug}] {len(jobs)} jobs")
    return jobs