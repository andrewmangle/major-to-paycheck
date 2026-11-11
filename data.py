"""Content and data for the Major to Paycheck prototype.

Wages: BLS Occupational Employment and Wage Statistics (OEWS), May 2025, metro area estimates.
  BAL = Baltimore-Columbia-Towson, MD; DCM = Washington-Arlington-Alexandria, DC-VA-MD-WV
  (DC and Northern Virginia share the DC metro wage data).
  median = annual median wage for the metro.
  p25 = annual 25th percentile. Filled from the official BLS file when available (load_bls.py);
        until then the page estimates it as P25_RATIO x median and marks it as an estimate.
Rent: HUD Fair Market Rent, one-bedroom, FY2027 (effective Oct 1, 2026).
Taxes: 2026 rules, single filer, standard deduction, no retirement contributions.
"""

DATA_AS_OF = "November 2026"
P25_RATIO = 0.77  # provisional estimate of 25th percentile / median for professional occupations

PLACES = {
    "baltimore": {"name": "Baltimore", "long": "Baltimore City, MD", "metro": "BAL", "rent": 1625,
                  "tax": "MD", "local_rate": 0.032, "local_name": "Baltimore City tax",
                  "linkedin": "Baltimore, Maryland", "usajobs": "Baltimore, Maryland"},
    "dc": {"name": "Washington, DC", "long": "Washington, DC", "metro": "DCM", "rent": 2204,
           "tax": "DC", "local_rate": 0.0, "local_name": "",
           "linkedin": "Washington, District of Columbia", "usajobs": "Washington, District of Columbia"},
    "nova": {"name": "Northern Virginia", "long": "Arlington, Alexandria, Fairfax", "metro": "DCM", "rent": 2204,
             "tax": "VA", "local_rate": 0.0, "local_name": "",
             "linkedin": "Arlington, Virginia", "usajobs": "Arlington, Virginia"},
}

# median annual wage, May 2025 (BLS OEWS via metro tables); p25 None until the BLS file is loaded
WAGES = {
    "13-2011": {"title": "Accountants and Auditors", "BAL": 85160, "DCM": 102140, "p25": {"DCM": 79990}},
    "13-2031": {"title": "Budget Analysts", "BAL": 96150, "DCM": 125050},
    "13-2081": {"title": "Tax Examiners and Collectors, and Revenue Agents", "BAL": 65140, "DCM": 81320},
    "13-1031": {"title": "Claims Adjusters, Examiners, and Investigators", "BAL": 98700, "DCM": 84590},
    "13-2053": {"title": "Insurance Underwriters", "BAL": 93510, "DCM": 90990},
    "41-3021": {"title": "Insurance Sales Agents", "BAL": 58300, "DCM": 65260},
    "13-2054": {"title": "Financial Risk Specialists", "BAL": 119720, "DCM": 126510},
    "13-2051": {"title": "Financial and Investment Analysts", "BAL": 98880, "DCM": 108330},
    "13-2072": {"title": "Loan Officers", "BAL": 68470, "DCM": 97800},
    "13-2052": {"title": "Personal Financial Advisors", "BAL": 98970, "DCM": 106230},
    "41-3031": {"title": "Securities, Commodities, and Financial Services Sales Agents", "BAL": 62080, "DCM": 64300},
    "19-3011": {"title": "Economists", "BAL": 152730, "DCM": 156750},
    "13-1161": {"title": "Market Research Analysts and Marketing Specialists", "BAL": 74620, "DCM": 87160},
    "13-1111": {"title": "Management Analysts", "BAL": 117750, "DCM": 126830},
    "15-1211": {"title": "Computer Systems Analysts", "BAL": 108980, "DCM": 127040},
    "15-1212": {"title": "Information Security Analysts", "BAL": 138170, "DCM": 148950},
    "15-1232": {"title": "Computer User Support Specialists", "BAL": 62950, "DCM": 77860},
    "13-1082": {"title": "Project Management Specialists", "BAL": 103720, "DCM": 127030},
    "15-2051": {"title": "Data Scientists", "BAL": 134320, "DCM": 132200, "p25": {"DCM": 105700}},
    "15-1242": {"title": "Database Administrators", "BAL": 123730, "DCM": 108750},
    "13-1199": {"title": "Business Operations Specialists, All Other", "BAL": 98060, "DCM": 104770},
    "41-3091": {"title": "Sales Representatives of Services", "BAL": 61840, "DCM": 78110},
    "13-1081": {"title": "Logisticians", "BAL": 102700, "DCM": 104330},
    "13-1071": {"title": "Human Resources Specialists", "BAL": 82380, "DCM": 100830},
    "13-1020": {"title": "Buyers and Purchasing Agents", "BAL": 84590, "DCM": 104880},
    "27-3031": {"title": "Public Relations Specialists", "BAL": 77570, "DCM": 101680},
    "41-4012": {"title": "Sales Representatives, Wholesale and Manufacturing", "BAL": 73080, "DCM": 74730},
    "13-1151": {"title": "Training and Development Specialists", "BAL": 78220, "DCM": 82400},
}

GS_2026_DCB = {"GS-5": 46610, "GS-7": 57736, "GS-9": 70623}  # OPM 2026, Washington-Baltimore-Arlington locality, step 1

# Each role: what students would call it, the BLS occupation behind it, and what gets you hired.
# first_job (optional): for roles new grads rarely land first. via lists the stepping-stone roles
# whose BLS 25th percentile is shown as "Where most people start" (a range when there are two).
ROLES = {
    "staff-accountant": dict(
        title="Staff Accountant / Audit Associate", soc="13-2011",
        does="Prepare and check financial statements, reconcile accounts, test a client's records.",
        screens=["An accounting internship, or tax season experience", "A plan to reach 150 credit hours for the CPA"],
        close=["Volunteer with VITA, the IRS free tax-prep program, for one tax season",
               "Get fast in Excel: pivot tables, XLOOKUP, and clean formatting"],
        search="staff accountant"),
    "budget-analyst": dict(
        title="Budget Analyst", soc="13-2031",
        does="Build and track budgets, explain where money went, and flag overspending.",
        screens=["Spreadsheet modeling", "Comfort explaining numbers to non-finance people"],
        close=["Build a budget-versus-actual analysis of a public agency budget and put it in a portfolio",
               "Apply for federal Pathways internships, a common way into government budget work"],
        search="budget analyst"),
    "revenue-agent": dict(
        title="Revenue Agent / Tax Examiner", soc="13-2081",
        does="Review tax returns, examine business records, and resolve what is owed.",
        screens=["Enough accounting credit hours (IRS revenue agent jobs set a minimum)", "Tax knowledge"],
        close=["VITA tax-prep volunteering is direct, relevant experience",
               "Take individual and business tax electives before you graduate"],
        search="tax examiner"),
    "claims-adjuster": dict(
        title="Claims Adjuster", soc="13-1031",
        does="Investigate insurance claims, estimate damage, and decide what gets paid.",
        screens=["A state adjuster license (many employers pay for it)", "Clear writing and customer communication"],
        close=["Study for the adjuster license exam before you apply",
               "Customer-facing work (retail, call center) counts as experience here"],
        search="claims adjuster trainee"),
    "underwriter": dict(
        title="Insurance Underwriter", soc="13-2053",
        does="Decide whether to insure a person or business, and at what price.",
        screens=["Analytical and Excel skills", "Interest in insurance as a career, not a stopgap"],
        close=["Start the Associate in General Insurance (AINS) designation from The Institutes",
               "Apply to underwriting trainee programs, which large insurers run every year"],
        search="underwriter trainee"),
    "insurance-agent": dict(
        title="Insurance Sales Agent", soc="41-3021",
        does="Help people and businesses choose insurance coverage. Pay often includes commission.",
        screens=["A state insurance producer license", "Sales or customer service experience"],
        close=["Take the pre-licensing course and pass your state producer exam",
               "Any sales job, even part time, shows you can handle a quota"],
        search="insurance agent"),
    "risk-analyst": dict(
        title="Risk Analyst", soc="13-2054",
        does="Measure financial risks such as credit, market and operational risk, and model what could go wrong.",
        screens=["Quantitative skills: Excel modeling, Python or R", "Statistics coursework"],
        close=["Complete a risk modeling project with public data, such as loan default rates",
               "Look at FRM Part I from GARP if you want a finance risk career"],
        note="Many risk analysts start in a related analyst job and move into risk.",
        search="risk analyst"),
    "financial-analyst": dict(
        title="Financial Analyst", soc="13-2051",
        does="Analyze company finances, build forecasts, and support investment decisions.",
        screens=["Financial modeling in Excel", "A finance internship"],
        close=["Build a three-statement model of a public company and walk through it in interviews",
               "Join or start an investment club and present stock pitches"],
        search="financial analyst"),
    "loan-officer": dict(
        title="Credit Analyst / Loan Officer", soc="13-2072",
        does="Review applicants' finances and recommend whether to lend, and on what terms.",
        screens=["Credit analysis skills", "An NMLS license for mortgage loan officers"],
        close=["Apply to bank credit analyst training programs, the usual first step into commercial lending",
               "For mortgage roles, take the NMLS pre-licensing course"],
        search="credit analyst"),
    "financial-advisor": dict(
        title="Financial Advisor", soc="13-2052",
        does="Help clients plan for goals like retirement and college. Pay often includes fees or commission.",
        screens=["FINRA exams (usually sponsored by the employer)", "Comfort building client relationships"],
        close=["Take the SIE exam now. Anyone 18 or older can take it without an employer sponsor",
               "Look for advisor associate programs at large firms"],
        search="financial advisor associate"),
    "economist": dict(
        title="Economist (federal entry)", soc="19-3011", start_override="GS-7",
        does="Analyze economic data and policy questions for an agency.",
        screens=["Federal economist jobs require at least 21 credit hours of economics plus statistics, accounting or calculus",
                 "Data skills: Excel, Stata or R"],
        close=["Write a short research paper using FRED or Census data",
               "Apply for federal Pathways internships in economics"],
        note="Most economist titles need a master's degree. With a bachelor's, federal trainee jobs at GS-5 or GS-7 are the main way in, so early-career pay here is the 2026 GS-7 rate.",
        search="economist"),
    "market-research": dict(
        title="Market Research Analyst", soc="13-1161",
        does="Study customers and competitors with surveys and data, then recommend what to do.",
        screens=["Data analysis with Excel, SQL or Tableau", "Clear presentation of findings"],
        close=["Analyze a public dataset and publish a dashboard on Tableau Public",
               "Earn the free Google Analytics certification"],
        search="market research analyst"),
    "management-analyst": dict(
        title="Management Analyst", soc="13-1111",
        does="Find ways to make an organization run better: processes, costs and structure.",
        screens=["Structured problem solving", "Strong Excel and PowerPoint"],
        close=["Compete in a case competition and put the deck in a portfolio",
               "Federal agencies and DC-area contractors hire many entry analysts. Search for 'junior analyst'"],
        note="Many new grads start with titles like junior analyst or associate consultant.",
        search="junior analyst"),
    "systems-analyst": dict(
        title="Systems Analyst", soc="15-1211",
        does="Translate business needs into requirements and help design the systems that meet them.",
        screens=["SQL and requirements writing", "Process modeling"],
        close=["Build a small database app and document the requirements behind it",
               "Show one end-to-end project: problem, requirements, solution"],
        search="systems analyst"),
    "security-analyst": dict(
        title="Cybersecurity Analyst", soc="15-1212",
        does="Monitor systems for threats, investigate alerts, and harden defenses.",
        screens=["CompTIA Security+ (a baseline for many DC-area defense jobs)", "Hands-on lab experience"],
        close=["Earn Security+ before you graduate",
               "Build a home lab and practice in capture-the-flag events"],
        note="Many jobs near DC need a security clearance, which usually requires US citizenship.",
        first_job=dict(label="IT support", via=["it-support"]),
        search="SOC analyst"),
    "it-support": dict(
        title="IT Support Specialist", soc="15-1232",
        does="Fix user and device problems. A common first job on the way to systems or security roles.",
        screens=["Troubleshooting experience", "A certification such as CompTIA A+"],
        close=["Earn CompTIA A+ or the Google IT Support certificate",
               "Work at the campus help desk"],
        search="IT support specialist"),
    "project-specialist": dict(
        title="Project Coordinator", soc="13-1082",
        does="Keep projects on schedule: plans, status reports, risks and follow-ups.",
        screens=["Organization and communication", "Project management basics"],
        close=["Earn the CAPM, PMI's entry-level certification (needs 23 hours of project management education)",
               "Lead a team project and keep the plan, schedule and status reports as proof"],
        search="project coordinator"),
    "data-analyst": dict(
        title="Data Analyst / Data Scientist", soc="15-2051",
        does="Clean data, analyze it, and turn it into answers and dashboards.",
        screens=["SQL plus Python or R", "A portfolio of real projects"],
        close=["Publish two portfolio projects on GitHub or Tableau Public",
               "Practice SQL interview questions until they feel routine"],
        note="BLS has no separate data analyst category, so first-job pay uses market research analysts.",
        first_job=dict(label="a data or market research analyst", via=["market-research"]),
        search="data analyst"),
    "database-admin": dict(
        title="Database Administrator", soc="15-1242",
        does="Keep databases fast, backed up and secure.",
        screens=["Strong SQL", "Cloud basics"],
        close=["Earn AWS Cloud Practitioner or Azure Fundamentals",
               "Build and maintain a database for a real club or small business"],
        first_job=dict(label="IT support or a junior analyst", via=["it-support", "market-research"]),
        search="junior database administrator"),
    "ops-specialist": dict(
        title="Business Operations Specialist", soc="13-1199",
        does="Keep a team or business running: processes, vendors, reports and coordination.",
        screens=["Organization and Excel", "Internship or work experience in any office setting"],
        close=["Document one process you improved at a job or club, with before and after numbers",
               "Get fast in Excel and one tool like Smartsheet or Airtable"],
        search="operations analyst"),
    "sales-rep": dict(
        title="Sales Representative", soc="41-3091",
        does="Find and win customers for a company's services. Pay often includes commission.",
        screens=["Communication and persistence", "Any sales or customer-facing experience"],
        close=["A part-time sales job or campus fundraising role shows you can hit targets",
               "Learn a CRM such as HubSpot (HubSpot's courses are free)"],
        search="sales development representative"),
    "hr-specialist": dict(
        title="Human Resources Specialist", soc="13-1071",
        does="Recruit, onboard and support employees, and keep HR records accurate.",
        screens=["An HR internship", "Discretion and organization"],
        close=["Earn the aPHR from HRCI, which requires no HR experience",
               "Help with hiring for a campus organization and track it like a real pipeline"],
        search="HR coordinator"),
    "logistician": dict(
        title="Logistics Analyst", soc="13-1081",
        does="Plan how goods move: suppliers, inventory, shipping and delivery.",
        screens=["Excel and data skills", "Supply chain coursework or experience"],
        close=["Analyze a supply chain case and present cost savings",
               "Defense contractors and federal agencies near DC hire many logistics analysts"],
        search="logistics analyst"),
    "buyer": dict(
        title="Buyer / Contract Specialist", soc="13-1020",
        does="Purchase goods and services, compare suppliers, and negotiate terms.",
        screens=["Negotiation and analysis", "Federal contract specialist jobs require 24 credit hours of business courses"],
        close=["Most business majors meet the federal 24-hour rule. Apply for contracting Pathways internships",
               "Learn the basics of how government buying works"],
        search="contract specialist"),
    "training-specialist": dict(
        title="Training and Development Specialist", soc="13-1151",
        does="Design and deliver training that helps employees learn new skills.",
        screens=["Presentation and writing", "Experience teaching, tutoring or leading workshops"],
        close=["Tutor or lead workshops on campus and keep your materials as samples",
               "Learn one e-learning tool such as Articulate Rise"],
        search="training coordinator"),
    "pr-specialist": dict(
        title="Public Relations Specialist", soc="27-3031",
        does="Shape how an organization is seen: press releases, media, social and events.",
        screens=["Strong writing samples", "Social media experience"],
        close=["Build a portfolio of press releases, social posts and a short campaign plan",
               "Run social media for a campus organization and track the results"],
        search="public relations coordinator"),
    "wholesale-rep": dict(
        title="Account Representative (B2B)", soc="41-4012",
        does="Sell products to businesses and manage those accounts. Pay often includes commission.",
        screens=["Communication and follow-through", "Sales experience"],
        close=["Apply to sales training programs that large distributors run for new grads",
               "Any job with targets shows you can sell"],
        search="account representative"),
}

PROGRAMS = [
    dict(id="accounting", name="Accounting", dept="Accounting, Finance & Economics",
         kind="Major (BS) and concentration",
         roles=["staff-accountant", "budget-analyst", "revenue-agent"]),
    dict(id="risk-management", name="Risk Management & Insurance", dept="Accounting, Finance & Economics",
         kind="Major", roles=["claims-adjuster", "underwriter", "insurance-agent", "risk-analyst"]),
    dict(id="finance", name="Banking & Finance", dept="Accounting, Finance & Economics",
         kind="Concentration", roles=["financial-analyst", "loan-officer", "financial-advisor"]),
    dict(id="economics", name="Economics", dept="Accounting, Finance & Economics",
         kind="Concentration", roles=["economist", "market-research", "financial-analyst", "management-analyst"]),
    dict(id="business-information-systems", name="Business Information Systems", dept="Management Information Systems",
         kind="Concentration", roles=["systems-analyst", "security-analyst", "it-support", "project-specialist"]),
    dict(id="data-analytics", name="Data Analytics", dept="Management Information Systems",
         kind="Concentration", roles=["data-analyst", "database-admin", "market-research", "management-analyst"]),
    dict(id="entrepreneurship", name="Entrepreneurship & Small Business", dept="Management, Marketing & Public Administration",
         kind="Major", roles=["ops-specialist", "sales-rep", "management-analyst"], founder=True),
    dict(id="general-business", name="General Business", dept="Management, Marketing & Public Administration",
         kind="Concentration", roles=["ops-specialist", "hr-specialist", "logistician", "buyer"]),
    dict(id="management", name="Management", dept="Management, Marketing & Public Administration",
         kind="Concentration", roles=["hr-specialist", "management-analyst", "project-specialist", "training-specialist"]),
    dict(id="marketing", name="Marketing", dept="Management, Marketing & Public Administration",
         kind="Concentration", roles=["market-research", "pr-specialist", "sales-rep", "wholesale-rep"]),
]

TAX = {
    "fed": {"std": 16100, "brackets": [[12400, .10], [50400, .12], [105700, .22], [201775, .24],
                                         [256225, .32], [640600, .35], [None, .37]]},
    "fica": .0765,
    "MD": {"std": 3350, "exemption": [[100000, 3200], [125000, 1600], [150000, 800], [None, 0]],
           "brackets": [[1000, .02], [2000, .03], [3000, .04], [100000, .0475], [125000, .05],
                        [150000, .0525], [250000, .055], [500000, .0575], [1000000, .0625], [None, .065]]},
    "DC": {"std": 16100, "brackets": [[10000, .04], [40000, .06], [60000, .065], [250000, .085],
                                        [500000, .0925], [1000000, .0975], [None, .1075]]},
    "VA": {"std": 8750, "exemption": [[None, 930]],
           "brackets": [[3000, .02], [5000, .03], [17000, .05], [None, .0575]]},
}

SOURCES = [
    ("Wages", "U.S. Bureau of Labor Statistics, Occupational Employment and Wage Statistics, May 2025, "
              "Baltimore-Columbia-Towson and Washington-Arlington-Alexandria metro areas",
     "https://www.bls.gov/oes/"),
    ("Federal entry pay", "OPM 2026 General Schedule, Washington-Baltimore-Arlington locality",
     "https://www.opm.gov/policy-data-oversight/pay-leave/salaries-wages/salary-tables/26Tables/html/DCB.aspx"),
    ("Rent", "HUD Fair Market Rents, FY2027, one-bedroom", "https://www.huduser.gov/portal/datasets/fmr.html"),
    ("Federal tax", "IRS 2026 inflation adjustments (single filer)", "https://www.irs.gov/node/151941"),
    ("State tax", "Tax Foundation, State Individual Income Tax Rates 2026; Comptroller of Maryland",
     "https://taxfoundation.org/data/all/state/state-income-tax-rates-2026/"),
    ("Programs", "Bowie State University College of Business",
     "https://bowiestate.edu/academics/colleges/college-of-business/"),
]
