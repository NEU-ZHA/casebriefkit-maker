# Cloudflare Pages Launch Checklist

Target domain: `casebrieftemplate.com`

Production host: Cloudflare Pages

Deployment method: Direct Upload

## Why This Route

This launch follows a keyword-first SEO test:

- The public entry point is `https://casebrieftemplate.com/`.
- Cloudflare Pages hosts the static site.
- Dynadot only holds the domain registration.
- GitHub is not required for Cloudflare deployment.
- Do not buy a mainland server, paid SSL certificate, paid DNS plan, site builder, email, or filing service.

## Prepare The Repository

Run these before each Direct Upload deployment:

```bash
python3 scripts/apply_custom_domain.py casebrieftemplate.com --platform cloudflare-pages --dry-run
python3 scripts/apply_custom_domain.py casebrieftemplate.com --platform cloudflare-pages --apply
python3 scripts/build_clean_urls.py
python3 scripts/build_discovery_files.py
python3 verify-free-site.py
python3 scripts/build_cloudflare_upload.py
```

Commit the resulting static-file changes for local history. Cloudflare does not need GitHub access when using Direct Upload.

## Cloudflare Direct Upload

In Cloudflare:

1. Go to Workers & Pages.
2. Select Create application.
3. Choose Upload your static files.
4. Upload the generated `casebrieftemplate-cloudflare-pages-upload.zip` file.
5. Set the worker/project name to `casebrieftemplate`.
6. Deploy the site.

The upload package includes `_headers`, `_redirects`, `404.html`, `robots.txt`, `sitemap.xml`, `feed.xml`, `llms.txt`, static HTML pages, assets, and free sample downloads.

Cloudflare Direct Upload guide:
https://developers.cloudflare.com/pages/get-started/direct-upload/

## Custom Domain

For the apex domain `casebrieftemplate.com`, add the domain as a Cloudflare zone and change the nameservers at Dynadot to the two nameservers Cloudflare provides.

After the zone is active:

1. Go to Workers & Pages.
2. Open the Pages project.
3. Open Custom domains.
4. Add `casebrieftemplate.com`.
5. Add `www.casebrieftemplate.com` if Cloudflare does not add it automatically.
6. Prefer the apex domain as canonical because all site metadata points there.

Cloudflare custom domain guide:
https://developers.cloudflare.com/pages/configuration/custom-domains/

## Do Not Add These

- No GitHub integration is required for the first launch.
- No mainland server.
- No paid SSL certificate.
- No paid DNS plan.
- No ICP filing.
- No email hosting bundle.
- No extra domains unless search evidence supports them.

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
