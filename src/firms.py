"""
Firm list with ATS (Applicant Tracking System) mappings.

ATS endpoints are structurally stable and return clean JSON — much more
reliable than scraping marketing sites. We try ATS first, then fall back
to the firm's careers page, then LinkedIn via Google.

ats_type: one of "greenhouse", "lever", "workday", "smartrecruiters", "ashby", None
ats_slug: the firm's identifier on that platform
"""

SCHOLARSHIP_SOURCES = [
    {"name": "EduCanada",              "url": "https://www.educanada.ca/scholarships-bourses/index.aspx"},
    {"name": "Canada.ca Scholarships", "url": "https://www.canada.ca/en/services/benefits/education/scholarships.html"},
    {"name": "Vanier Canada",          "url": "https://vanier.gc.ca/en/home-accueil.html"},
    {"name": "Erasmus Mundus",         "url": "https://www.eacea.ec.europa.eu/scholarships/erasmus-mundus-catalogue_en"},
    {"name": "Eiffel Excellence",      "url": "https://www.campusfrance.org/en/eiffel-scholarship-program-of-excellence"},
]

FIRMS = [
    # --- Paris ---
    {"name": "Meridiam",                     "ats_type": None,            "ats_slug": None,                   "fallback_url": "https://meridiam.com/careers/"},
    {"name": "Ardian",                       "ats_type": "workday",       "ats_slug": "ardian.wd103.myworkdayjobs.com/ArdianCareers", "fallback_url": "https://www.ardian.com/join-us"},
    {"name": "Antin Infrastructure",         "ats_type": None,            "ats_slug": None,                   "fallback_url": "https://www.antin-ip.com/careers/"},
    {"name": "InfraVia Capital Partners",    "ats_type": None,            "ats_slug": None,                   "fallback_url": "https://www.infraviacapital.com/careers"},
    {"name": "Tikehau Capital",              "ats_type": None,            "ats_slug": None,                   "fallback_url": "https://www.tikehaucapital.com/en/careers"},
    {"name": "Mirova",                       "ats_type": None,            "ats_slug": None,                   "fallback_url": "https://www.mirova.com/en/career"},
    {"name": "Eiffel Investment Group",      "ats_type": None,            "ats_slug": None,                   "fallback_url": "https://eiffel-ig.com/en/join-us-2/"},
    {"name": "Omnes Capital",                "ats_type": None,            "ats_slug": None,                   "fallback_url": "https://www.omnescapital.com/en/join-us"},
    {"name": "Asterion Industrial Partners", "ats_type": None,            "ats_slug": None,                   "fallback_url": "https://www.asterionindustrial.com/join-us/"},
    {"name": "Energy Impact Partners",       "ats_type": "greenhouse",    "ats_slug": "energyimpactpartners", "fallback_url": "https://www.energyimpactpartners.com/join-our-team/"},
    {"name": "Vauban Infrastructure",        "ats_type": None,            "ats_slug": None,                   "fallback_url": "https://www.vauban-ip.com/careers/"},
    {"name": "Hy24 Partners",                "ats_type": None,            "ats_slug": None,                   "fallback_url": "https://www.hy24partners.com/join-us/"},
    {"name": "Demeter Partners",             "ats_type": None,            "ats_slug": None,                   "fallback_url": "https://demeter-im.com/en/careers-3/"},

    # --- Copenhagen / Nordic ---
    {"name": "Copenhagen Infrastructure Partners", "ats_type": None,      "ats_slug": None,                   "fallback_url": "https://cipartners.dk/careers/"},

    # --- Stockholm ---
    {"name": "EQT",                          "ats_type": None,            "ats_slug": None,                   "fallback_url": "https://eqtgroup.com/careers"},

    # --- Singapore / APAC ---
    {"name": "Actis",                        "ats_type": None,            "ats_slug": None,                   "fallback_url": "https://www.act.is/careers/"},
    {"name": "Pentagreen Capital",           "ats_type": None,            "ats_slug": None,                   "fallback_url": "https://www.pentagreencapital.com/careers"},
    {"name": "Clifford Capital",             "ats_type": None,            "ats_slug": None,                   "fallback_url": "https://www.cliffordcapital.sg/careers"},
    {"name": "Equis",                        "ats_type": None,            "ats_slug": None,                   "fallback_url": "https://equis.com/careers/"},
    {"name": "Temasek",                      "ats_type": "workday",       "ats_slug": "temasek.wd3.myworkdayjobs.com/Temasek", "fallback_url": "https://www.temasek.com.sg/en/careers"},

    # --- Toronto ---
    {"name": "Brookfield",                   "ats_type": "workday",       "ats_slug": "bn.wd3.myworkdayjobs.com/Brookfield_Careers", "fallback_url": "https://careers.brookfield.com/jobs"},
    {"name": "Northleaf",                    "ats_type": None,            "ats_slug": None,                   "fallback_url": "https://www.northleafcapital.com/careers/"},
    {"name": "Fiera Infrastructure",         "ats_type": None,            "ats_slug": None,                   "fallback_url": "https://fierainfrastructure.com/careers/"},
    {"name": "ArcTern Ventures",             "ats_type": None,            "ats_slug": None,                   "fallback_url": "https://arcternventures.com/careers/"},
    {"name": "BDC Capital",                  "ats_type": None,            "ats_slug": None,                   "fallback_url": "https://www.bdc.ca/en/bdc-capital/about/careers"},

    # --- Ottawa / Canadian public finance ---
    {"name": "EDC",                          "ats_type": None,            "ats_slug": None,                   "fallback_url": "https://www.edc.ca/en/about-us/careers.html"},
    {"name": "SDTC",                         "ats_type": None,            "ats_slug": None,                   "fallback_url": "https://www.sdtc.ca/en/careers/"},
    {"name": "Canada Infrastructure Bank",   "ats_type": None,            "ats_slug": None,                   "fallback_url": "https://cib-bic.ca/en/careers/"},

    # --- Global cleantech VC ---
    {"name": "Breakthrough Energy Ventures", "ats_type": "greenhouse",    "ats_slug": "breakthroughenergyventures", "fallback_url": "https://breakthroughenergy.org/work-with-us/"},
]