# Notes on the existing access-request screen (v1, shipped 2023)

We are replacing this. These notes describe what is on screen today so the new
spec knows what people are used to.

## What the current screen shows

A single page reached from **Settings → Data Access**. Top to bottom:

- A page title, "Request access".
- A dropdown labelled "Dataset" listing every dataset the user can see. There
  is no search; the list is alphabetical and roughly 400 items long.
- A text field labelled "Reason". Optional. Most submissions leave it blank.
- A dropdown labelled "Level" with two options, "Viewer" and "Editor".
- A "Submit" button. No confirmation step.
- After submit, the page replaces the form with the sentence "Your request has
  been submitted." and nothing else. No id, no link, no way back.

## What the screen does not show

- Any indication of who will decide the request.
- Any indication of how long a decision usually takes.
- Any list of the user's own past or pending requests. Users ask support for
  this constantly.
- Any state between "submitted" and "granted". If a request is denied the user
  finds out because access never appears.
- Anything at all about expiry. Access granted here does not expire, which
  security has flagged twice.

## Terminology on the current screen

- "Dataset" here means what the catalog calls a "data product".
- "Viewer" / "Editor" here map to what the entitlement service calls
  `read` / `read-write`.
- "Owner" is not used on this screen at all, though internally each dataset has
  one.

## Behaviour we know is wrong

- Submitting twice creates two requests; there is no duplicate detection.
- If the dataset is deleted while a request is pending, the request stays in
  the queue forever.
- The reason field being optional means owners approve blind about 70% of the
  time.
