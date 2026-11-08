# Third-party Python dependencies

Pinned application/test environment. Package metadata inspected locally on 2026-11-03. This is an inventory, not a legal opinion.

| Package | Version | Declared license |
|---|---|---|
| annotated-doc | 0.0.5 | MIT |
| annotated-types | 0.8.0 | MIT |
| anyio | 4.16.0 | MIT |
| certifi | 2026.10.23 | MPL-2.0 |
| click | 8.5.0 | BSD-3-Clause |
| colorama | 0.4.6 | BSD-3-Clause |
| fastapi | 0.162.0 | MIT |
| h11 | 0.16.0 | MIT |
| httpcore | 1.0.9 | BSD-3-Clause |
| httpx | 0.28.1 | BSD-3-Clause |
| idna | 3.20 | BSD-3-Clause |
| iniconfig | 2.3.1 | MIT |
| opentelemetry-api | 1.45.2 | Apache-2.0 |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause |
| pluggy | 1.7.0 | MIT |
| pydantic | 2.14.2 | MIT |
| pydantic_core | 2.50.2 | MIT |
| Pygments | 2.21.0 | BSD-2-Clause |
| pytest | 9.2.0 | MIT |
| starlette | 1.10.0 | BSD-3-Clause |
| typing-inspection | 0.4.4 | MIT |
| typing_extensions | 4.16.0 | PSF-2.0 |
| uvicorn | 0.54.0 | BSD-3-Clause |

Python container base has its own Python/Debian package licenses. The application MIT license does not relicense third-party components.
Original UI uses system fonts and original inline SVG icons. examples/invoices.csv is authored synthetic data.

## Audit Folio typography — 2026-11-05

The redesigned frontend locally hosts Newsreader regular (109,472 bytes) and IBM Plex Mono regular (128,812 bytes). Downloaded from the official Google Fonts stylesheet's fonts.gstatic.com URLs, recorded in `artifacts/design-studio/font-source.css`. No system fonts were installed and the application makes no third-party font requests.

- Newsreader: copyright 2020 The Newsreader Project Authors; SIL Open Font License 1.1. [Upstream](https://github.com/google/fonts/tree/main/ofl/newsreader); full notice retained in `web/fonts/Newsreader-OFL.txt`.
- IBM Plex Mono: copyright 2017 IBM Corp., Reserved Font Name "Plex"; SIL Open Font License 1.1. [Upstream](https://github.com/google/fonts/tree/main/ofl/ibmplexmono); full notice retained in `web/fonts/IBMPlexMono-OFL.txt`.

Font files are unmodified. Controls retain system sans fallbacks; font-display swap keeps the work usable during font loading. These font licenses are separate from the application's MIT license.

Colorama 0.4.6 was checked against the installed distribution's full text on 2026-11-03: `.venv/Lib/site-packages/colorama-0.4.6.dist-info/licenses/LICENSE.txt`, copyright 2010 Jonathan Hartley. The file contains the source-notice, binary-notice and non-endorsement clauses of BSD-3-Clause. Preserve the notice and disclaimer when redistributing this component; the application MIT license does not replace them. This closes the earlier `UNKNOWN` metadata entry by inspection of the actual shipped license text.
