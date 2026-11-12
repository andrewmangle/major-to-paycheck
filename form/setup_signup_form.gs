/**
 * Major to Paycheck sign-up form setup.
 *
 * Adds the sign-up questions to Andrew's Google Form and prints the pre-filled link
 * that the site's "Get openings for this job" buttons use.
 *
 * How to run (once):
 *   1. Open the form in edit mode, then Extensions > Apps Script.
 *   2. Replace everything in Code.gs with this file and click Save.
 *   3. Choose setUpSignupForm in the function menu and click Run. Approve access when Google asks.
 *   4. Open the Execution log, copy the block that starts with "PASTE THIS INTO CLAUDE CODE",
 *      and paste it into Claude Code.
 *
 * Safe to run again: questions that already exist (same title and type) are updated, not duplicated.
 */

const FORM_ID = '1iULh9xo4Mdg42vcvy0nBgVo9N4xvB6u-SmagbndvgYo';

// Program names must match the site's program names exactly so pre-fill works.
const PROGRAMS = [
  'Accounting', 'Risk Management & Insurance', 'Banking & Finance', 'Economics',
  'Business Information Systems', 'Data Analytics', 'Entrepreneurship & Small Business',
  'General Business', 'Management', 'Marketing', 'Other',
];
const PLACES = ['Baltimore', 'Washington DC', 'Northern Virginia', 'Open to anywhere'];

function setUpSignupForm() {
  const form = FormApp.openById(FORM_ID);
  const T = FormApp.ItemType;

  find_(form, 'Name', T.TEXT, () => form.addTextItem()).asTextItem()
    .setRequired(true);

  find_(form, 'Email', T.TEXT, () => form.addTextItem()).asTextItem()
    .setRequired(true)
    .setValidation(FormApp.createTextValidation()
      .requireTextIsEmail()
      .setHelpText('Enter a valid email address.')
      .build());

  const program = find_(form, 'Program', T.LIST, () => form.addListItem()).asListItem()
    .setChoiceValues(PROGRAMS);

  const job = find_(form, 'Job you’re interested in', T.TEXT, () => form.addTextItem()).asTextItem();

  const where = find_(form, 'Where you want to live', T.CHECKBOX, () => form.addCheckboxItem()).asCheckboxItem()
    .setChoiceValues(PLACES);

  find_(form, 'Class standing', T.MULTIPLE_CHOICE, () => form.addMultipleChoiceItem()).asMultipleChoiceItem()
    .setChoiceValues(['Freshman', 'Sophomore', 'Junior', 'Senior', 'Graduate student', 'Recent graduate']);

  find_(form, 'Expected graduation (month and year)', T.TEXT, () => form.addTextItem()).asTextItem()
    .setHelpText('For example, May 2027');

  find_(form, 'What should we send you?', T.CHECKBOX, () => form.addCheckboxItem()).asCheckboxItem()
    .setChoiceValues(['Internships for this job', 'Entry-level openings', 'Case challenges and events',
      'Tips to close the gap']);

  find_(form, 'Best way to reach you', T.MULTIPLE_CHOICE, () => form.addMultipleChoiceItem()).asMultipleChoiceItem()
    .setChoiceValues(['Email', 'Instagram DM', 'Text']);

  find_(form, 'Instagram handle or phone number', T.TEXT, () => form.addTextItem()).asTextItem()
    .setHelpText('Only needed if you picked Instagram DM or Text.');

  // Consent stays in its own section so it reads as a separate choice. Required to answer, but No is a full answer.
  find_(form, 'Sharing with employers', T.SECTION_HEADER, () => form.addSectionHeaderItem()).asSectionHeaderItem()
    .setHelpText('Optional to say yes. Saying no does not change anything else you signed up for.');

  find_(form, 'Can we share your profile with employers hiring for this job?', T.MULTIPLE_CHOICE,
    () => form.addMultipleChoiceItem()).asMultipleChoiceItem()
    .setChoiceValues(['Yes', 'No'])
    .setRequired(true);

  form.setAcceptingResponses(true);
  try {
    form.setPublished(true);  // forms made since 2025 must be published to take responses
  } catch (e) {
    Logger.log('Could not publish automatically. Click Publish at the top of the form. (' + e + ')');
  }

  // Build a pre-filled link with marker values, then read each question's entry number from it.
  const url = form.createResponse()
    .withItemResponse(program.createResponse('Accounting'))
    .withItemResponse(job.createResponse('JOB'))
    .withItemResponse(where.createResponse(['Baltimore']))
    .toPrefilledUrl();
  const ids = {};
  url.replace(/entry\.(\d+)=([^&]*)/g, (m, id, value) => {
    ids[decodeURIComponent(value.replace(/\+/g, ' '))] = 'entry.' + id;
  });

  Logger.log([
    'PASTE THIS INTO CLAUDE CODE',
    'form: ' + url.split('?')[0],
    'program: ' + ids['Accounting'],
    'job: ' + ids['JOB'],
    'place: ' + ids['Baltimore'],
    'prefilled: ' + url,
  ].join('\n'));
}

/** Returns the existing item with this title and type, or a new one made by add(), as a generic Item. */
function find_(form, title, type, add) {
  const existing = form.getItems().filter((it) => it.getTitle() === title && it.getType() === type)[0];
  if (existing) return existing;
  const created = add().setTitle(title);
  return form.getItemById(created.getId());
}
