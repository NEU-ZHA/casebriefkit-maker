# Cloudflare Pages Launch Checklist

Target domain: `casebrieftemplate.com`

Production host: Cloudflare Pages

Repository: `NEU-ZHA/casebriefkit-maker`

## Buy Only The Domain

- Buy `casebrieftemplate.com` for 1 year if the registrar shows ordinary `.com` pricing.
- Do not add a mainland server, paid SSL certificate, paid DNS plan, site builder, email, or filing service.
- Complete the registrar identity template and domain purchase in the Tencent Cloud account.

## Prepare The Repository

Run these only after the domain is purchased:

```bash
python3 scripts/apply_custom_domain.py casebrieftemplate.com --platform cloudflare-pages --dry-run
python3 scripts/apply_custom_domain.py casebrieftemplate.com --platform cloudflare-pages --apply
python3 scripts/build_clean_urls.py
python3 scripts/build_discovery_files.py
python3 verify-free-site.py
```

Commit and push the resulting static files before connecting Cloudflare Pages.

## Cloudflare Pages Project

Create a Pages project from the GitHub repository:

- Production branch: `main`
- Build command: `exit 0`
- Build output directory: `.`
- Root directory: leave blank

The repository already includes `_headers`, `_redirects`, `404.html`, `robots.txt`, `sitemap.xml`, `feed.xml`, and `llms.txt`.

Cloudflare static HTML guide:
https://developers.cloudflare.com/pages/framework-guides/deploy-anything/

## Custom Domain

For the apex domain `casebrieftemplate.com`, add the domain as a Cloudflare zone and change the nameservers at Tencent Cloud to the two nameservers Cloudflare provides.

After the zone is active:

1. Go to Workers & Pages.
2. Open the Pages project.
3. Open Custom domains.
4. Add `casebrieftemplate.com`.
5. Add `www.casebrieftemplate.com` if Cloudflare does not add it automatically.
6. Prefer the apex domain as canonical because all site metadata points there.

Cloudflare custom domain guide:
https://developers.cloudflare.com/pages/configuration/custom-domains/

## Verify

After DNS and HTTPS settle:

```bash
python3 scripts/check_custom_domain.py casebrieftemplate.com --platform cloudflare-pages
```

Expected result:

- Cloudflare nameservers detected.
- `https://casebrieftemplate.com/` returns 200.
- `https://casebrieftemplate.com/sitemap.xml` returns 200.
- `https://casebrieftemplate.com/robots.txt` returns 200.
- The home page contains `CaseBriefKit`.

Then move Search Console and any index submission to `https://casebrieftemplate.com/`.
