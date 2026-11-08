# Prooflane brand update — 9 November 2026

The team-supplied logo now appears in the public application's masthead and on all six presentation slides. The README's first image and the submission cover use the unchanged team-supplied cover. Real application captures remain separately identified.

## Asset handling

- Original logo: `docs/brand/prooflane-logo-original.png`, 1248×726. The website's lossless WebP has identical decoded pixels and is 385,564 bytes instead of 616,383 bytes. An SVG viewport crops only the surrounding whitespace; the original file remains intact. A CSS brightness adjustment and darken blend remove the visible paper rectangle against the application background.
- Cover: `docs/images/prooflane-cover.png` and `submission/agent-rush/cover.png`, 1672×941. Their bytes match the supplied image. The depicted interface, counts, percentages, supplier approval and PO/GRN features are illustrative. They do not establish implemented capabilities or measured results.
- Asset rights: [third-party notices](../THIRD_PARTY_NOTICES.md). User supply does not independently establish authorship or third-party clearance.

## Checks actually performed

- Public HTTPS application rendered at desktop 1440×960 and mobile 390×844. The logo remained legible and no horizontal page overflow was observed. Its home link retained the accessible name `Prooflane home`; decorative SVG content is hidden from the accessibility tree. The mobile target measured 168×45.75 CSS pixels. This is a browser/DOM accessibility check, not a new screen-reader test.
- Opened the reviewed fictional example on the deployed site after the update: 7 included rows, 1 excluded row, USD768.00 positive variance, explicitly labeled Reference mode. No new AI generation was used for this branding check. The earlier actual AI recording remains separately evidenced.
- Browser error/warning log was empty at the inspected public result. The remote service remained active; public HTTPS health reported Docker available and inference configured/enabled. Deployed file hashes matched local files.
- Existing JavaScript tests and bootstrap structural verification passed. No backend logic changed.
- Imported and edited the existing six-slide PPTX in an Artifact Session, exported it, passed package/layout validation with zero findings and two native tables, and inspected all six rendered slides. The PDF was regenerated from those renders. Native PowerPoint rendering was not tested. The rebuild script now preserves the supplied logo and cover.
- Upload archive CRC and every bundled file's SHA256 were checked after repackaging. These checks do not confirm an official hackathon submission.

Screenshots and measured browser evidence: [brand verification artifacts](../artifacts/brand-update-20261109/).

## Entry-page recommendation

The existing root page is the workspace and restores a previous review. This behavior is functional. For first-time visitors, a short introductory page could explain the invoice-review problem, show an actual example, and provide a direct `Open demo` action without registration. Preserve a direct workspace link for returning reviewers and judges. Clear purpose and a clear starting action follow [NN/g's homepage guidance](https://www.nngroup.com/articles/homepage-design-principles/). A separate landing page has **not** been implemented in this branding update.
