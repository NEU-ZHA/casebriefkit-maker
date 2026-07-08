# CaseBriefKit Maker

Free case brief maker and law school template pages.

This public launch is intentionally limited to the free, indexable tool flow:

- Case brief maker
- IRAC, FIRAC, Word, Google Docs, Markdown, PDF, and DOCX template pages
- How to brief a case guide page
- Example case brief page
- Clean SEO URLs, for example `/case-brief-maker/` and `/case-brief-template/`
- Basic privacy, terms, and contact pages

Commercial download fulfillment is not part of this launch copy.

Intent signal:

- Public feedback thread: https://github.com/NEU-ZHA/casebriefkit-maker/issues/1
- Printable file requests are collected through GitHub Issues.
- Expanded DOCX/PDF file interest is collected through GitHub Issues as a purchase-intent signal before any sale flow is opened.
- A case brief template pack preview page now tests a planned `$9` one-time pack before a real payment link is added.
- A separate template pack preview PDF is published as a release asset so high-intent downloads can be counted without requiring GitHub login.
- Ad-ready house placements are live, and `ads.txt` is present for future authorized seller lines after ad network approval.
- A public sponsor media kit is live at https://casebrieftemplate.com/sponsor-media-kit/.
- The sponsor pilot offer is intentionally small: `$29` for one reviewed 14-day placement or `$49` for two reviewed 14-day placements.
- Sponsor inquiries are collected through GitHub Issues and should not include payment details.
- Sponsor placement updates can be prepared with `python3 scripts/apply_sponsor_placement.py --config CONFIG.json` before review and publish.
- A public one-page PDF/DOCX sample is included for lower-friction testing.
- The printable DOCX/PDF buttons use the public release assets so downloads can be counted without adding tracking scripts.
- Download, feedback, and maker CTA links include `data-track-event` attributes so GA4 can record intent events once a measurement ID is connected.
- The request flow does not ask for private student records or sensitive details.
- A public request is treated as a stronger signal than a page view.
- The `$9` waitlist is not a payment request; it is a price-sensitivity and urgency signal.
- Cold-call prompts or an AI cold-call prep workflow are tracked as future add-on interest, not part of the first paid test.

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

- The preferred production host is Cloudflare Pages, not a mainland server and not the old GitHub Pages URL.
- The preferred first deployment path is Cloudflare Pages Direct Upload, so Cloudflare does not need GitHub access.
- Do not switch canonical URLs before the domain is purchased and the Cloudflare Pages project is ready.
- Canonical URLs and `sitemap.xml` now prefer directory-style pages so the same structure can move cleanly to `https://casebrieftemplate.com/case-brief-maker/`.
- Keep clean URL pages synchronized with `python3 scripts/build_clean_urls.py`.
- Submit updated URLs to IndexNow with:
  `python3 scripts/submit_indexnow.py --apply`
- After buying the domain, run `python3 scripts/apply_custom_domain.py casebrieftemplate.com --platform cloudflare-pages --dry-run`.
- If the dry run is correct, run `python3 scripts/apply_custom_domain.py casebrieftemplate.com --platform cloudflare-pages --apply`.
- Use the Cloudflare Pages launch checklist in `docs/cloudflare-pages-launch.md`.
- Build the Direct Upload zip with `python3 scripts/build_cloudflare_upload.py`.
- Configure Cloudflare nameservers at the registrar, then run `python3 scripts/check_custom_domain.py casebrieftemplate.com --platform cloudflare-pages`.
- Only after DNS, HTTPS, sitemap, and robots checks pass should Search Console and IndexNow move to the custom domain.
