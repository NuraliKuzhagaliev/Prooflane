# Landing delivery contract

Objective: build and publish the requested Prooflane landing page; retain the real review workspace and all execution boundaries. Owner: one implementation/review context; no independent agent review is claimed.

Scope: this repository, its existing GitHub main branch and the existing Vultr deployment. Budget USD0; no new resources, provider calls, dependencies or tracking services. Keep Python/FastAPI and vanilla JS/CSS. Secrets, databases, generated code policy and infrastructure settings are excluded.

Acceptance: root serves a clear product entry; `/app` serves the existing workspace; visitors can open a real Reference example and return without losing the saved review; the fictional price preview uses exact cents and explains its limits; keyboard/mobile/reduced-motion behavior works; all links have destinations; deployment and public README match the routes.

## Creative choice before implementation

Three distinct directions were considered by the implementation owner; these are design judgments, not independent scores:

1. **Review desk**: asymmetric headline beside a source-document relationship, followed by a usable price experiment, a real capture and an evidence handover. Navigation follows the review questions. Serif headings, warm off-white, dark green and mint come from the supplied identity. Selected for product fit, clarity and feasible keyboard/mobile equivalents.
2. **Variance billboard**: a giant amount occupies the first screen; the whole page changes with one price control. Strong interactive hook but a decontextualized amount could look like recovered savings and obscure source decisions.
3. **Open casebook**: full-width numbered chapters with one invoice expanded across reading stages. Strong editorial identity but a longer path to a quick demo and weaker immediate product comprehension.

Interaction thesis: demonstrate how a shared source price changes the next review question. Use a real range/number input with named presets and exact arithmetic, not a decorative looping chart. Native links/details work without custom navigation; only result bars transition. Respect reduced motion. No autoplay or artificial loading states.

References checked 9 November: [Mercury Books](https://mercury.com/books) for a visible demo entry; [Ramp AP](https://ramp.com/accounts-payable) for task-specific sequencing; [Linear](https://linear.app/) for product-centered narrative; [Stripe Financial Connections](https://stripe.com/financial-connections) for explanation of boundaries; [NN/g](https://www.nngroup.com/articles/homepage-design-principles/) for clear purpose and next action. These informed principles; no layouts, copy, business claims or capabilities were copied.

## Evidence plan and tooling note

Run the existing Python and JavaScript suites, the meaningful new route/cent-boundary tests and bootstrap structural check. Inspect real local and deployed renders at desktop/tablet/mobile, keyboard input, presets, validation, FAQ, workspace navigation/resume and reduced-motion styles. Record untested physical touch and screen-reader behavior honestly. Refresh README workflow and source release evidence.

The optional Engineering Hub CLI was attempted but could not write its run packet outside the permitted project (`WinError 5`). This project-local contract is the permitted fallback. No adjacent project was modified.
