# CaseBriefKit Maker

Free case brief maker and law school template pages.

This public launch is intentionally limited to the free, indexable tool flow:

- Case brief maker
- IRAC, FIRAC, Word, Google Docs, Markdown, PDF, and DOCX template pages
- How to brief a case guide page
- Example case brief page
- Basic privacy, terms, and contact pages

Commercial download pages are not part of this launch copy.

Intent signal:

- Public feedback thread: https://github.com/NEU-ZHA/casebriefkit-maker/issues/1
- Printable file requests are collected through GitHub Issues.
- Expanded DOCX/PDF file interest is collected through GitHub Issues as a purchase-intent signal before any sale flow is opened.
- A case brief template pack preview page targets more commercial search intent before a buyer flow exists.
- A separate template pack preview PDF is published as a release asset so high-intent downloads can be counted without requiring GitHub login.
- Ad-ready house placements are live, and `ads.txt` is present for future authorized seller lines after ad network approval.
- A public one-page PDF/DOCX sample is included for lower-friction testing.
- The printable DOCX/PDF buttons use the public release assets so downloads can be counted without adding tracking scripts.
- Download, feedback, and maker CTA links include `data-track-event` attributes so GA4 can record intent events once a measurement ID is connected.
- The request flow does not ask for private student records or sensitive details.
- A public request is treated as a stronger signal than a page view.

- Usage feedback is collected through GitHub Issues as a non-purchase signal.

Traffic measurement readiness:

- GitHub Pages does not provide enough page-level analytics for SEO validation.
- Without an analytics provider, external posts can only be judged by downloads, GitHub issues, sponsor inquiries, and visible platform replies.
- Cloudflare Web Analytics can be added after creating a site token:
  `python3 scripts/apply_analytics.py --cloudflare-token TOKEN --dry-run`
  `python3 scripts/apply_analytics.py --cloudflare-token TOKEN --apply`
- Microsoft Clarity can be added after creating a project id:
  `python3 scripts/apply_analytics.py --clarity-id PROJECT_ID --dry-run`
  `python3 scripts/apply_analytics.py --clarity-id PROJECT_ID --apply`
- Check current analytics state with:
  `python3 scripts/check_analytics.py`
- Remove snippets with:
  `python3 scripts/apply_analytics.py --remove --apply`

Custom domain readiness:

- Do not add `CNAME` before the domain is purchased.
- After buying a domain, run `python3 scripts/apply_custom_domain.py casebriefkit.com --dry-run`.
- If the dry run is correct, run `python3 scripts/apply_custom_domain.py casebriefkit.com --apply`.
- Configure DNS at the registrar, then run `python3 scripts/check_custom_domain.py casebriefkit.com`.
- Only after DNS, HTTPS, sitemap, and robots checks pass should Search Console and IndexNow move to the custom domain.
