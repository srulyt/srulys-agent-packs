# Brief — Approval inbox for data product owners

## Context

Data product owners currently decide access requests from a spreadsheet. We
want to give them a proper place to do it.

## What we think it looks like

The team sketched this on a whiteboard. Treat it as a starting point, not a
decision:

- A **left nav** with "Pending", "Decided", and "My data products".
- Pending requests in a **card grid**, three across, each card showing the
  requester's avatar, the data product name in **16px semibold**, and the age
  of the request as a small grey label in `#6B7280`.
- Approve and Deny as a **green** and **red** button pair in the bottom-right
  of each card, with 8px spacing between them.
- A **modal** for the denial reason, with a required textarea.
- The whole thing on a **white background** with a 24px page gutter, using
  **Inter** for everything.
- An icon in the top bar — probably the bell — for the notification count.

## What it actually has to do

- Show an owner everything waiting on them, oldest first.
- Let them approve or deny without leaving the list.
- Require a reason on denial.
- Make it obvious when a request is about to auto-escalate.
- Not let two owners decide the same request twice.
- Handle the case where the requester's employment ended between request and
  decision.

## Notes

- Owners have told us they mostly do this on a laptop, in one sitting, once or
  twice a day.
- Some owners own 40+ data products; some own one.
