# Career Route sign-ups and emails: setup

How it fits together:

1. **Daily, on your computer (automatic):** Windows Task Scheduler runs `scripts/daily_feed.sh` at 7:00 AM.
   It pulls open federal student listings from USAJOBS, writes `openings.json` matched to Career Route jobs and
   places, and pushes it to GitHub Pages. It contains only public listing data.
2. **In Google (Apps Script):** your form's response Sheet runs `Code.gs`. Each new sign-up gets a welcome
   email right away with current matches. Every Monday, each subscriber gets new matches. Students who chose
   Instagram DM or Text also get a ready-to-paste message in the "DM queue" tab.

Student information never leaves your Google account.

## One-time setup (about 10 minutes)

1. Open your form > Responses tab > **Link to Sheets** > create a new spreadsheet.
2. In that spreadsheet: **Extensions > Apps Script**. Delete the starter code, paste all of
   `apps-script/Code.gs`, and click Save. (Pasting it into the form's own Apps Script
   project also works: the script finds the linked response Sheet.)
3. Choose **setupForm** in the function menu and click **Run**. Approve the permissions (it is your own
   script). Your form already has its questions, so setupForm only checks that every question the emails
   read is there (by exact title) and writes the result to a "Setup" tab. It changes nothing on the form.
   If it stops with "missing questions", a question title was edited on the form; put the title back.
4. Nothing to do here: the pre-fill numbers are already in `data.py`, and `SITE_URL` and `FEED_URL` are
   already set in Code.gs. Until the first openings feed is published, emails send LinkedIn and USAJOBS
   search links instead of listings.
5. Run **installTriggers** once.
6. Submit the form yourself, then run **sendTestDigestToMe**. Check both emails. When they look right,
   set `TEST_MODE: false` and save.

## Daily feed (automatic)

Windows Task Scheduler task **Career Route daily feed** runs at 7:00 AM. If the computer is off then, it runs
as soon as you turn it on and log in. It runs `scripts/daily_feed.sh` in WSL (Ubuntu), which:

1. pulls open listings on the USAJOBS Students hiring path (key and email from internfeed-shorts `.env`)
   into `internfeed-shorts/data/careerroute_usajobs.xlsx` (separate from the Fed Intern Drop video sheet),
2. runs internfeed-shorts `feed` against this repo's `careerroute.json`,
3. copies `openings.json` into the repo root, commits it and pushes.

It publishes at most once a day, never publishes an empty feed, and stops without changing the live feed if
USAJOBS fails. Log: `~/.local/state/careerroute-feed/feed.log` in WSL. Run it by hand with
`bash scripts/daily_feed.sh --force`. It uses the Python environment in `~/.venvs/careerroute-feed`
(pandas, openpyxl, numpy, scipy, pillow), not Docker.

## Limits and upkeep

- A personal Gmail account can send about 100 script emails a day. The digest stops at the limit and the
  rest go next run. A Google Workspace account allows more.
- Someone replies "unsubscribe": add their email to column A of the "Unsubscribed" tab (create it once).
- The "Sent log" tab keeps each student from getting the same listing twice.
- The DM queue is for you to copy and send by hand. Mark Done when sent.
