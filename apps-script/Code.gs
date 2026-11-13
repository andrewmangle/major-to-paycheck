/**
 * Career Route sign-ups: form setup, instant welcome email, weekly matched openings, DM queue.
 *
 * Where it runs: Google Apps Script, under your Google account. Student information stays in your
 * Google Sheet. The only thing it reads from outside is openings.json, which holds public listings.
 *
 * Setup (one time, about 10 minutes): see SETUP-EMAILS.md. In short:
 *   1. Open the form, Responses tab, "Link to Sheets", create a new sheet. In that sheet open
 *      Extensions > Apps Script, paste this whole file, save.
 *   2. Run setupForm once (approve the permissions). On a form that already has its questions it only
 *      checks them and writes the Setup tab. On a blank form it adds the questions.
 *   3. Run installTriggers once. Welcome emails start on the next sign-up; digests go out weekly.
 *   4. Leave TEST_MODE true until a test digest to yourself looks right (run sendTestDigestToMe).
 */

const CONFIG = {
  FORM_ID: '1iULh9xo4Mdg42vcvy0nBgVo9N4xvB6u-SmagbndvgYo',
  SITE_URL: 'https://andrewmangle.github.io/major-to-paycheck/',   // Career Route on GitHub Pages, ending in a slash
  FEED_URL: 'https://andrewmangle.github.io/major-to-paycheck/openings.json',   // missing: emails send search links only
  MANGLE_URL: 'https://andrewmangle.com/?utm_source=career-route&utm_medium=email&utm_campaign=bsu-cob',
  FROM_NAME: 'Career Route',
  REPLY_TO: '',   // optional address replies go to
  DIGEST_DAY: 'MONDAY',
  DIGEST_HOUR: 9, // in the script's time zone (File > Project settings)
  MAX_PER_EMAIL: 5,
  TEST_MODE: true // true: the weekly digest goes only to you, labeled with who it was for
};

const ROUTE = {"programs":[{"id":"accounting","name":"Accounting","roles":["staff-accountant","budget-analyst","revenue-agent"]},{"id":"risk-management","name":"Risk Management & Insurance","roles":["claims-adjuster","underwriter","insurance-agent","risk-analyst"]},{"id":"finance","name":"Banking & Finance","roles":["financial-analyst","loan-officer","financial-advisor"]},{"id":"economics","name":"Economics","roles":["economist","market-research","financial-analyst","management-analyst"]},{"id":"business-information-systems","name":"Business Information Systems","roles":["systems-analyst","security-analyst","it-support","project-specialist"]},{"id":"data-analytics","name":"Data Analytics","roles":["data-analyst","database-admin","market-research","management-analyst"]},{"id":"entrepreneurship","name":"Entrepreneurship & Small Business","roles":["ops-specialist","sales-rep","management-analyst"]},{"id":"general-business","name":"General Business","roles":["ops-specialist","hr-specialist","logistician","buyer"]},{"id":"management","name":"Management","roles":["hr-specialist","management-analyst","project-specialist","training-specialist"]},{"id":"marketing","name":"Marketing","roles":["market-research","pr-specialist","sales-rep","wholesale-rep"]}],"roles":{"staff-accountant":{"title":"Staff Accountant / Audit Associate","search":"staff accountant","series":["0510","0511","0599"]},"budget-analyst":{"title":"Budget Analyst","search":"budget analyst","series":["0560","0501","0599"]},"revenue-agent":{"title":"Revenue Agent / Tax Examiner","search":"tax examiner","series":["0512","0526","0592","0599"]},"claims-adjuster":{"title":"Claims Adjuster","search":"claims adjuster trainee","series":["0991","0993"]},"underwriter":{"title":"Insurance Underwriter","search":"underwriter trainee","series":[]},"insurance-agent":{"title":"Insurance Sales Agent","search":"insurance agent","series":[]},"risk-analyst":{"title":"Risk Analyst","search":"risk analyst","series":["1160","0501"]},"financial-analyst":{"title":"Financial Analyst","search":"financial analyst","series":["1160","0501","0599","1199"]},"loan-officer":{"title":"Credit Analyst / Loan Officer","search":"credit analyst","series":["1165","0570"]},"financial-advisor":{"title":"Financial Advisor","search":"financial advisor associate","series":[]},"economist":{"title":"Economist (federal entry)","search":"economist","series":["0110","0199"]},"market-research":{"title":"Market Research Analyst","search":"market research analyst","series":["1101","0343","1199"]},"management-analyst":{"title":"Management Analyst","search":"junior analyst","series":["0343","0301","0399"]},"systems-analyst":{"title":"Systems Analyst","search":"systems analyst","series":["2210","2299"]},"security-analyst":{"title":"Cybersecurity Analyst","search":"SOC analyst","series":["2210","2299"]},"it-support":{"title":"IT Support Specialist","search":"IT support specialist","series":["2210","2299"]},"project-specialist":{"title":"Project Coordinator","search":"project coordinator","series":["0343","0301","1101","0399"]},"data-analyst":{"title":"Data Analyst / Data Scientist","search":"data analyst","series":["1530","1560","1515","1599","0343"]},"database-admin":{"title":"Database Administrator","search":"junior database administrator","series":["2210","2299"]},"ops-specialist":{"title":"Business Operations Specialist","search":"operations analyst","series":["0301","0399","0303"]},"sales-rep":{"title":"Sales Representative","search":"sales development representative","series":[]},"hr-specialist":{"title":"Human Resources Specialist","search":"HR coordinator","series":["0201","0299"]},"logistician":{"title":"Logistics Analyst","search":"logistics analyst","series":["0346","2003","2010","2099"]},"buyer":{"title":"Buyer / Contract Specialist","search":"contract specialist","series":["1102","1105","1199"]},"training-specialist":{"title":"Training and Development Specialist","search":"training coordinator","series":["1712","0201","1799"]},"pr-specialist":{"title":"Public Relations Specialist","search":"public relations coordinator","series":["1035","1099"]},"wholesale-rep":{"title":"Account Representative (B2B)","search":"account representative","series":[]}},"places":{"baltimore":{"name":"Baltimore","form":"Baltimore","states":["MD"],"linkedin":"Baltimore, Maryland","usajobs":"Baltimore, Maryland"},"dc":{"name":"Washington, DC","form":"Washington DC","states":["DC","MD","VA"],"linkedin":"Washington, District of Columbia","usajobs":"Washington, District of Columbia"},"nova":{"name":"Northern Virginia","form":"Northern Virginia","states":["VA","DC"],"linkedin":"Arlington, Virginia","usajobs":"Arlington, Virginia"}}};

// Question titles. Everything finds answers by these exact titles, so they match the live form
// (built by form/setup_signup_form.gs). The job title uses a curly apostrophe, as on the form.
// The live form has no source question; answers to it read as blank.
const Q = {
  name: 'Name',
  email: 'Email',
  program: 'Program',
  job: 'Job you’re interested in',
  places: 'Where you want to live',
  standing: 'Class standing',
  grad: 'Expected graduation (month and year)',
  wants: 'What should we send you?',
  channel: 'Best way to reach you',
  handle: 'Instagram handle or phone number',
  share: 'Can we share your profile with employers hiring for this job?',
  source: 'How did you find us?'
};
// Questions the emails read. setupForm checks that an existing form has all of them.
const NEEDED = ['name', 'email', 'program', 'job', 'places', 'wants', 'channel', 'handle', 'share'];

/** The checkbox label for a place on the form (e.g. "Washington DC"), which can differ from its display name. */
function placeLabel_(id) { return ROUTE.places[id].form || ROUTE.places[id].name; }
const ANYWHERE = 'Open to anywhere';
const SHEETS = { sent: 'Sent log', dm: 'DM queue', unsub: 'Unsubscribed', setup: 'Setup' };

// ------------------------------------------------------------------ setup
function setupForm() {
  const form = FormApp.openById(CONFIG.FORM_ID);
  if (form.getItems().length > 0) return checkForm_(form);
  form.setTitle('Career Route: get openings for your target job');
  form.setDescription('Tell us the job and city you picked in Major to Paycheck. We will email you matching ' +
    'internships and entry-level openings. We share your profile with an employer only if you say yes below. ' +
    'Reply "unsubscribe" to any email to stop.');
  form.setCollectEmail(false);

  form.addTextItem().setTitle(Q.name).setRequired(true);
  form.addTextItem().setTitle(Q.email).setRequired(true)
    .setValidation(FormApp.createTextValidation().requireTextIsEmail().build());
  form.addListItem().setTitle(Q.program).setRequired(true)
    .setChoiceValues(ROUTE.programs.map(function (p) { return p.name; }).concat(['Other']));
  form.addTextItem().setTitle(Q.job)
    .setHelpText('Copy the job title from Major to Paycheck, e.g. Staff Accountant / Audit Associate.');
  form.addCheckboxItem().setTitle(Q.places).setRequired(true)
    .setChoiceValues(Object.keys(ROUTE.places).map(placeLabel_).concat([ANYWHERE]));
  form.addMultipleChoiceItem().setTitle(Q.standing)
    .setChoiceValues(['Freshman', 'Sophomore', 'Junior', 'Senior', 'Graduate student', 'Recent graduate']);
  form.addTextItem().setTitle(Q.grad);
  form.addCheckboxItem().setTitle(Q.wants)
    .setChoiceValues(['Internships for this job', 'Entry-level openings', 'Case challenges and events', 'Tips to close the gap']);
  form.addMultipleChoiceItem().setTitle(Q.channel).setRequired(true).setChoiceValues(['Email', 'Instagram DM', 'Text']);
  form.addTextItem().setTitle(Q.handle);
  form.addMultipleChoiceItem().setTitle(Q.share).setRequired(true)
    .setHelpText('Optional to say yes. If yes, employers hiring for your target job may see your name, program, ' +
      'class standing and target job. You can change your answer any time by replying to an email.')
    .setChoiceValues(['Yes', 'No']);
  form.addMultipleChoiceItem().setTitle(Q.source).showOtherOption(true)
    .setChoiceValues(['Career Route', 'Major to Paycheck', 'Fed Intern Drop', 'Mangle Metric', 'A class or professor', 'A friend']);
  form.setConfirmationMessage('You are in. Check your email for your first openings. New matches arrive every week.');

  const ss = SpreadsheetApp.getActive() || SpreadsheetApp.create('Career Route sign-ups');
  try { form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId()); } catch (err) { /* already linked */ }

  // Pre-fill numbers for the Major to Paycheck buttons
  const byTitle = {};
  form.getItems().forEach(function (it) { byTitle[it.getTitle()] = it; });
  const firstPlace = placeLabel_(Object.keys(ROUTE.places)[0]);
  const samples = [
    ['program', byTitle[Q.program].asListItem().createResponse(ROUTE.programs[0].name)],
    ['job', byTitle[Q.job].asTextItem().createResponse('JOB')],
    ['place', byTitle[Q.places].asCheckboxItem().createResponse([firstPlace])],
    ['source', byTitle[Q.source].asMultipleChoiceItem().createResponse('Major to Paycheck')]
  ];
  const entries = {};
  samples.forEach(function (pair) {
    const url = form.createResponse().withItemResponse(pair[1]).toPrefilledUrl();
    const m = url.match(/(entry\.\d+)=/);
    entries[pair[0]] = m ? m[1] : '';
  });
  const sheet = getSheet_(ss, SHEETS.setup);
  sheet.clear();
  sheet.appendRow(['Form link', form.getPublishedUrl()]);
  sheet.appendRow(['Pre-fill numbers for data.py SIGNUP["entries"]', JSON.stringify(entries)]);
  Logger.log('Form link: ' + form.getPublishedUrl());
  Logger.log('Pre-fill numbers: ' + JSON.stringify(entries));
}

/**
 * For a form that already has its questions: confirm every question the emails read is there, and that the
 * place checkboxes match. Changes nothing on the form. Writes the result to the Setup tab.
 */
function checkForm_(form) {
  const items = form.getItems();
  const titles = items.map(function (it) { return it.getTitle(); });
  const missing = NEEDED.filter(function (k) { return titles.indexOf(Q[k]) < 0; })
    .map(function (k) { return '"' + Q[k] + '"'; });
  if (missing.length) {
    throw new Error('The form is missing questions the emails need: ' + missing.join(', ') +
      '. Add them with these exact titles, or update Q at the top of this script. Nothing was changed.');
  }
  const placeItem = items.filter(function (it) { return it.getTitle() === Q.places; })[0];
  const choices = placeItem.asCheckboxItem().getChoices().map(function (c) { return c.getValue(); });
  const missingPlaces = Object.keys(ROUTE.places).map(placeLabel_).concat([ANYWHERE])
    .filter(function (label) { return choices.indexOf(label) < 0; });
  if (missingPlaces.length) {
    throw new Error('"' + Q.places + '" is missing these choices: ' + missingPlaces.join(', ') + '. Nothing was changed.');
  }
  const ss = SpreadsheetApp.getActive();
  if (ss) {
    const sheet = getSheet_(ss, SHEETS.setup);
    sheet.clear();
    sheet.appendRow(['Form link', form.getPublishedUrl()]);
    sheet.appendRow(['Form check', 'Every question the emails need is on the form. Nothing was changed.']);
    sheet.appendRow(['Source question', titles.indexOf(Q.source) >= 0 ? 'Present' : 'Not on the form (optional)']);
  }
  Logger.log('Form check passed. Every question the emails need is on the form. Nothing was changed.');
}

function installTriggers() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (['onSignup', 'sendWeeklyDigest'].indexOf(t.getHandlerFunction()) >= 0) ScriptApp.deleteTrigger(t);
  });
  const ss = SpreadsheetApp.getActive();
  ScriptApp.newTrigger('onSignup').forSpreadsheet(ss).onFormSubmit().create();
  ScriptApp.newTrigger('sendWeeklyDigest').timeBased()
    .onWeekDay(ScriptApp.WeekDay[CONFIG.DIGEST_DAY]).atHour(CONFIG.DIGEST_HOUR).create();
  Logger.log('Triggers installed: welcome on each sign-up, digest every ' + CONFIG.DIGEST_DAY + ' at ' + CONFIG.DIGEST_HOUR + ':00.');
}

// ------------------------------------------------------------- triggers
function onSignup(e) {
  const sub = subscriberFromNamed_(e.namedValues);
  if (!sub.email) return;
  const ss = SpreadsheetApp.getActive();
  const feed = fetchFeed_();
  const plan = planFor(sub, feed.openings, []);
  deliver_(ss, sub, plan, { welcome: true, test: false });
}

function sendWeeklyDigest() { runDigest_(CONFIG.TEST_MODE); }

function sendTestDigestToMe() { runDigest_(true, 3); }

function runDigest_(test, limit) {
  const ss = SpreadsheetApp.getActive();
  const feed = fetchFeed_();
  const subs = readSubscribers_(ss);
  const sent = readSent_(ss);
  let count = 0;
  for (let i = 0; i < subs.length; i++) {
    if (limit && count >= limit) break;
    if (MailApp.getRemainingDailyQuota() < 2) { Logger.log('Daily email limit reached. The rest go next run.'); break; }
    const sub = subs[i];
    const plan = planFor(sub, feed.openings, sent[sub.email.toLowerCase()] || []);
    deliver_(ss, sub, plan, { welcome: false, test: test });
    count++;
  }
  Logger.log((test ? 'TEST: ' : '') + count + ' digests handled from ' + feed.openings.length + ' open listings.');
}

// ------------------------------------------------------- pure logic (tested)
function placeIdsFor(sub) {
  const ids = Object.keys(ROUTE.places);
  if (!sub.places.length || sub.places.indexOf(ANYWHERE) >= 0) return ids;
  const out = ids.filter(function (id) { return sub.places.indexOf(placeLabel_(id)) >= 0; });
  return out.length ? out : ids;
}

function programFor(sub) {
  return ROUTE.programs.filter(function (p) { return p.name === sub.program; })[0] || null;
}

function roleIdsFor(sub) {
  const want = (sub.job || '').trim().toLowerCase();
  const ids = Object.keys(ROUTE.roles);
  if (want) {
    const exact = ids.filter(function (id) { return ROUTE.roles[id].title.toLowerCase() === want; });
    if (exact.length) return exact;
    const loose = ids.filter(function (id) {
      const t = ROUTE.roles[id].title.toLowerCase();
      return t.indexOf(want) >= 0 || want.indexOf(ROUTE.roles[id].search.toLowerCase()) >= 0;
    });
    if (loose.length) return loose;
  }
  const prog = programFor(sub);
  return prog ? prog.roles.slice() : [];
}

function planFor(sub, openings, alreadySent) {
  const roleIds = roleIdsFor(sub);
  const placeIds = placeIdsFor(sub);
  const matched = (openings || []).filter(function (o) {
    const roleHit = o.roles.some(function (r) { return roleIds.indexOf(r) >= 0; });
    const placeHit = o.remote || o.places.some(function (p) { return placeIds.indexOf(p) >= 0; });
    return roleHit && placeHit;
  }).sort(function (a, b) { return (a.deadline || '9999').localeCompare(b.deadline || '9999'); });
  const fresh = matched.filter(function (o) { return alreadySent.indexOf(o.id) < 0; }).slice(0, CONFIG.MAX_PER_EMAIL);
  const stillOpen = fresh.length ? [] : matched.slice(0, 3);
  const role = ROUTE.roles[roleIds[0]] || null;
  const place = ROUTE.places[placeIds[0]];
  const prog = programFor(sub);
  return { sub: sub, roleIds: roleIds, placeIds: placeIds, fresh: fresh, stillOpen: stillOpen,
           role: role, place: place, programId: prog ? prog.id : '', placeId: placeIds[0] };
}

function links(plan) {
  const q = plan.role ? plan.role.search : (plan.sub.job || 'internship');
  const enc = encodeURIComponent;
  const out = {
    linkedin: 'https://www.linkedin.com/jobs/search/?keywords=' + enc(q) + '&location=' + enc(plan.place.linkedin) + '&f_E=1%2C2',
    usajobs: 'https://www.usajobs.gov/search/results/?k=' + enc(q) + '&l=' + enc(plan.place.usajobs) + '&hp=student',
    mangle: CONFIG.MANGLE_URL,
    paycheck: ''
  };
  if (CONFIG.SITE_URL) {
    out.paycheck = CONFIG.SITE_URL + 'paycheck.html' + (plan.programId ? '#' + plan.programId + '-' + plan.placeId : '');
  }
  return out;
}

function esc_(s) {
  return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
  });
}

function firstName_(name) { return String(name || '').trim().split(/\s+/)[0] || 'there'; }

function fmtDate_(iso) {
  if (!iso) return 'open until filled';
  const p = iso.split('-');
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  return months[Number(p[1]) - 1] + ' ' + Number(p[2]);
}

function buildEmail(plan, opts) {
  const sub = plan.sub;
  const L = links(plan);
  const target = plan.role ? plan.role.title : (sub.job || sub.program || 'your target job');
  const where = sub.places.indexOf(ANYWHERE) >= 0 || !sub.places.length ? 'anywhere' : plan.place.name;
  const list = plan.fresh.length ? plan.fresh : plan.stillOpen;
  const heading = plan.fresh.length ? 'New openings that match' :
    (plan.stillOpen.length ? 'No new matches this week. These are still open' : 'No federal matches this week');
  const subject = (opts.welcome ? 'Welcome to Career Route: ' : 'This week: ') + target + ' openings, ' + where;

  const rows = list.map(function (o) {
    return '<tr><td style="padding:10px 0;border-bottom:1px solid #e3e6e5">' +
      '<a href="' + esc_(o.apply_url) + '" style="font-weight:600;color:#1f47b8;text-decoration:none">' + esc_(o.title) + '</a><br>' +
      '<span style="color:#56636e">' + esc_(o.company) + ' · ' + esc_(o.location) + (o.pay ? ' · ' + esc_(o.pay) : '') +
      ' · Apply by ' + esc_(fmtDate_(o.deadline)) + '</span></td></tr>';
  }).join('');
  const none = list.length ? '' : '<p style="color:#56636e">Federal listings for this job are seasonal. The searches below cover every employer, updated daily.</p>';

  const html =
    '<div style="font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.5;color:#15202b;max-width:560px">' +
    '<p>Hi ' + esc_(firstName_(sub.name)) + ',</p>' +
    (opts.welcome ? '<p>You are signed up for <b>' + esc_(target) + '</b> openings, ' + esc_(where) + '. Here is what is open right now. New matches arrive every week.</p>'
                  : '<p>Your weekly openings for <b>' + esc_(target) + '</b>, ' + esc_(where) + '.</p>') +
    '<h3 style="font-size:16px;margin:18px 0 4px">' + esc_(heading) + '</h3>' +
    (rows ? '<table style="width:100%;border-collapse:collapse">' + rows + '</table>' : '') + none +
    '<h3 style="font-size:16px;margin:18px 0 4px">Search every employer</h3>' +
    '<p style="margin:0"><a href="' + L.linkedin + '">Entry-level and intern jobs on LinkedIn</a><br>' +
    '<a href="' + L.usajobs + '">Federal internships on USAJOBS</a></p>' +
    '<h3 style="font-size:16px;margin:18px 0 4px">Your route</h3>' +
    '<p style="margin:0">' + (L.paycheck ? '<a href="' + L.paycheck + '">Your Major to Paycheck view</a>: pay, rent and what gets you hired<br>' : '') +
    '<a href="' + L.mangle + '">Your free Mangle Metric score</a>: see where you stand for this job</p>' +
    '<p style="color:#56636e;font-size:12.5px;margin-top:24px">You are getting this because you signed up through Career Route. ' +
    'Reply "unsubscribe" to stop. Independent prototype for Bowie State College of Business students, not an official university service.</p></div>';

  const text = ['Hi ' + firstName_(sub.name) + ',', '',
    (opts.welcome ? 'You are signed up for ' : 'Your weekly openings for ') + target + ', ' + where + '.', '',
    heading + ':'].concat(list.length ? list.map(function (o) {
      return '- ' + o.title + ', ' + o.company + ', ' + o.location + '. Apply by ' + fmtDate_(o.deadline) + ': ' + o.apply_url;
    }) : ['- None this week. Try the searches below.']).concat(['',
    'LinkedIn: ' + L.linkedin, 'USAJOBS: ' + L.usajobs,
    L.paycheck ? 'Major to Paycheck: ' + L.paycheck : '', 'Mangle Metric: ' + L.mangle, '',
    'Reply "unsubscribe" to stop.']).filter(function (x) { return x !== null; }).join('\n');
  return { subject: subject, html: html, text: text };
}

function buildDm(plan) {
  const sub = plan.sub;
  const L = links(plan);
  const target = plan.role ? plan.role.title.split(' / ')[0] : (sub.job || 'your target job');
  const list = (plan.fresh.length ? plan.fresh : plan.stillOpen).slice(0, 3);
  const lines = ['Hi ' + firstName_(sub.name) + '! ' + target + ' openings this week:'];
  if (list.length) {
    list.forEach(function (o, i) { lines.push((i + 1) + ') ' + o.title + ', ' + o.company + ', apply by ' + fmtDate_(o.deadline) + ': ' + o.apply_url); });
  } else {
    lines.push('No federal ones this week. Every employer: ' + L.linkedin);
  }
  lines.push('Where you stand: ' + L.mangle);
  lines.push('Reply STOP to stop.');
  return lines.join('\n');
}

// ------------------------------------------------------------ Google glue
function deliver_(ss, sub, plan, opts) {
  const email = buildEmail(plan, opts);
  const me = Session.getEffectiveUser().getEmail();
  if (opts.test) {
    MailApp.sendEmail({ to: me, subject: '[TEST for ' + sub.email + '] ' + email.subject,
      htmlBody: email.html, body: email.text, name: CONFIG.FROM_NAME });
    return;
  }
  const mail = { to: sub.email, subject: email.subject, htmlBody: email.html, body: email.text, name: CONFIG.FROM_NAME };
  if (CONFIG.REPLY_TO) mail.replyTo = CONFIG.REPLY_TO;
  MailApp.sendEmail(mail);
  if (sub.channel === 'Instagram DM' || sub.channel === 'Text') {
    getSheet_(ss, SHEETS.dm, ['Date', 'Channel', 'Handle or number', 'Name', 'Message', 'Done']).appendRow(
      [new Date(), sub.channel, sub.handle, sub.name, buildDm(plan), '']);
  }
  const log = getSheet_(ss, SHEETS.sent, ['Date', 'Email', 'Listing id', 'Listing']);
  plan.fresh.forEach(function (o) { log.appendRow([new Date(), sub.email.toLowerCase(), o.id, o.title + ', ' + o.company]); });
}

function fetchFeed_() {
  if (!CONFIG.FEED_URL) return { openings: [] };
  try {
    const res = UrlFetchApp.fetch(CONFIG.FEED_URL, { muteHttpExceptions: true });
    if (res.getResponseCode() !== 200) throw new Error('HTTP ' + res.getResponseCode());
    return JSON.parse(res.getContentText());
  } catch (err) {
    Logger.log('Could not read the openings feed (' + err + '). Sending search links only.');
    return { openings: [] };
  }
}

function getSheet_(ss, name, header) {
  let sh = ss.getSheetByName(name);
  if (!sh) {
    sh = ss.insertSheet(name);
    if (header) sh.appendRow(header);
  }
  return sh;
}

function splitMulti_(v) { return String(v || '').split(',').map(function (s) { return s.trim(); }).filter(String); }

function subscriberFromNamed_(nv) {
  const get = function (t) { return nv[t] ? String(nv[t][0] || '').trim() : ''; };
  // Checkbox answers come back comma separated, so look for each known form label in the raw answer
  const raw = get(Q.places);
  const known = Object.keys(ROUTE.places).map(placeLabel_).concat([ANYWHERE]);
  const places = known.filter(function (n) { return raw.indexOf(n) >= 0; });
  return { name: get(Q.name), email: get(Q.email), program: get(Q.program), job: get(Q.job), places: places,
           channel: get(Q.channel) || 'Email', handle: get(Q.handle), share: get(Q.share), wants: splitMulti_(get(Q.wants)) };
}

function readSubscribers_(ss) {
  const sheet = ss.getSheets().filter(function (s) { return s.getFormUrl && s.getFormUrl(); })[0];
  if (!sheet) throw new Error('No form response sheet found. Run setupForm first.');
  const values = sheet.getDataRange().getValues();
  const head = values.shift();
  const unsub = {};
  const u = ss.getSheetByName(SHEETS.unsub);
  if (u) u.getDataRange().getValues().forEach(function (r) { if (r[0]) unsub[String(r[0]).trim().toLowerCase()] = true; });
  const latest = {};
  values.forEach(function (row) {
    const nv = {};
    head.forEach(function (h, i) { nv[h] = [row[i]]; });
    const s = subscriberFromNamed_(nv);
    const key = s.email.toLowerCase();
    if (key && !unsub[key]) latest[key] = s; // later rows replace earlier ones from the same email
  });
  return Object.keys(latest).map(function (k) { return latest[k]; });
}

function readSent_(ss) {
  const out = {};
  const sh = ss.getSheetByName(SHEETS.sent);
  if (!sh) return out;
  sh.getDataRange().getValues().slice(1).forEach(function (r) {
    const k = String(r[1]).toLowerCase();
    (out[k] = out[k] || []).push(String(r[2]));
  });
  return out;
}
