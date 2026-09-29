# Event Materiality Review

Rubric for judging whether an 8-K filing is a real, database-worthy event vs. routine
noise. Developed over ~150 individually-read filings across the stale-URL sweep review
sessions (2026-09-28/29). Referenced from `SCRIPTS.md`.

## The core test, always

Would this filing's content, read on its own by a reasonably informed investor, change
how they'd price the stock or think about the company's near-term trajectory — versus
being administrative housekeeping that follows from something already known or priced in?

The category patterns below are a first-pass sort, **not a final verdict**. Every category
has real exceptions, and the exceptions are never random — they turn on whether the
surrounding context makes the filing genuinely informative, not on the document's surface
shape (buyback, lawsuit-filed, pill-adoption). A rule that pattern-matches on document type
alone will systematically miss the real exceptions below.

## Deals & acquisitions
- **Confirm**: a named counterparty + some indication of scale (dollar figure, "definitive
  agreement," or described strategic scope) is enough even with no price stated.
- **Watch for duplicates**: administrative steps *within* an already-disclosed deal
  (shareholder vote results, HSR clearance, financial-statement filings for a pending deal)
  usually duplicate the real event already captured at announcement — reject as duplicate,
  not as noise.
- **Exception**: a vote result IS the real event when no earlier filing captured the actual
  approval milestone for that specific transaction (confirmed CCL's DLC unification vote on
  this basis).

## Restructuring / workforce actions
- **Confirm**: a quantified charge (dollar range) OR a quantified headcount number.
- **Reject**: restructuring language with neither number — nothing for the market to price.
- **Numbers alone aren't sufficient** — they must be material relative to company size.
  Rejected ALGN's $2.6M/38-employee reduction (trivial for the company) while confirming
  AMAT's ~1,000 positions.

## Leadership changes
- **Confirm**: CEO, CFO, President, Chairman. Division-level COO is a real judgment call,
  not automatic.
- **Reject**: mid-level VP appointments, routine board refresh with no stated cause for
  concern.
- **Test**: does the role sit close enough to strategic control that a change would alter
  how the market reads the company's direction? A named executive officer designation under
  Item 5.02 signals SEC-recognized materiality regardless of specific function (confirmed a
  Chief Ethics and Compliance Officer resignation on this basis).

## Capital raises / financing
- **Reject**: standalone debt/equity issuance with no stated deal purpose — routine
  treasury activity.
- **Confirm**: the same kind of filing when it names a specific acquisition it's funding —
  a dated, real commitment to a transaction.
- **Exception**: buybacks/dividends can be confirmed standalone when large enough relative
  to the company to signal a genuine capital-allocation shift — confirmed CSX's ~$2B
  buyback (~15% of market cap) with no acquisition attached, purely on scale. The blanket
  "reject standalone buybacks" rule would have missed this.

## Legal / regulatory
- **Confirm**: a settlement with a dollar figure, a guilty plea, a consent decree, an SEC
  Wells notice — any concrete resolution or formal regulatory action.
- **Reject**: a lawsuit merely filed with no resolution yet — an allegation isn't yet a
  quantifiable liability (rejected BDX's antitrust suits on this basis).
- **Exception**: some facts are material without a dollar figure attached because the fact
  itself is undeniably significant — Boeing's 737 MAX charge disclosure, a confirmed
  ransomware attack with unauthorized data access (CCL 2020).

## Governance actions
- **Reject in isolation**: poison pill adoption/termination, majority-voting bylaw
  amendments, foreign-private-issuer status changes, listing-venue transfers — corporate
  machinery, not news.
- **Confirm the same filing type** when it's clearly a response to a live activist campaign
  or hostile bid already in the news — kept Duke's Elliott cooperation-agreement pill,
  Netflix's 2012 pill (Icahn), HP's 2020 pill (Xerox bid) on this basis.

## Process notes
- Never bulk-confirm or bulk-reject a batch — every row gets individually read against this
  test before a verdict.
- When in doubt about scale (restructuring size, buyback size, etc.), check it against the
  company's market cap or existing scale rather than judging the raw number alone.
