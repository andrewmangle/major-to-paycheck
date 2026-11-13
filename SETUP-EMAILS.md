# Career Route sign-ups and emails: setup

How it fits together:

1. **Daily, on your computer (Docker):** `usajobs` pulls open federal internships, then `feed` writes
   `openings.json`, matched to Career Route jobs and places. Copy it to `site/openings.json` and push to
   GitHub Pages. It contains only public listing data.
2. **In Google (Apps Script):** your form's response Sheet runs `Code.gs`. Each new sign-up gets a welcome
   email right away with current matches. Every Monday, each subscriber gets new matches. Students who chose
   Instagram DM or Text also get a ready-to-paste message in the "DM queue" tab.

Student information never leaves your Google account.

## One-time setup (about 10 minutes)

1. Open your form > Responses tab > **Link to Sheets** > create a new spreadsheet.
2. In that spreadsheet: **Extensions > Apps Script**. Delete the starter code, paste all of
   `apps-script/Code.gs`, and click Save.
3. Choose **setupForm** in the function menu and click **Run**. Approve the permissions (it is your own
   script). It adds 12 questions to your blank form and writes the pre-fill numbers to a "Setup" tab.
4. Copy the pre-fill numbers from the Setup tab into `data.py` (`SIGNUP["entries"]`) and run
   `python3 build.py`. Now the "Get openings" buttons arrive with program, job, place and source filled in.
5. Once Career Route is on GitHub Pages, set `SITE_URL` and `FEED_URL` at the top of Code.gs.
   Until then, emails still send LinkedIn and USAJOBS search links, just no listings.
6. Run **installTriggers** once.
7. Submit the form yourself, then run **sendTestDigestToMe**. Check both emails. When they look right,
   set `TEST_MODE: false` and save.

## Daily feed (Docker, from the internfeed-shorts folder)

```powershell
docker run --rm --env-file .env -v "${PWD}/data:/app/data" internfeed-shorts usajobs --close-missing
docker run --rm -v "${PWD}/data:/app/data" -v "${PWD}/output:/app/output" internfeed-shorts feed
copy output\feed\openings.json D:\internfeed\major-to-paycheck\site\openings.json
```

Then commit and push the site. Claude Code can run these and the push for you on a schedule.
Refresh `data/careerroute.json` from `major-to-paycheck/site/careerroute.json` whenever you change jobs in data.py.

## Limits and upkeep

- A personal Gmail account can send about 100 script emails a day. The digest stops at the limit and the
  rest go next run. A Google Workspace account allows more.
- Someone replies "unsubscribe": add their email to column A of the "Unsubscribed" tab (create it once).
- The "Sent log" tab keeps each student from getting the same listing twice.
- The DM queue is for you to copy and send by hand. Mark Done when sent.
