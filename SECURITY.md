# Security model

The application is a static, client-side resume generator.

- Resume contents are processed in the browser and are not sent to an API.
- Content Security Policy sets `connect-src 'none'`, blocking fetch, XHR,
  WebSocket and EventSource connections.
- The DOCX dependency is vendored locally. No third-party JavaScript is loaded.
- Draft persistence is disabled by default and requires explicit opt-in.
- The photo is never placed in browser storage and is limited to JPEG/PNG files
  of at most 5 MB.
- Generated files are downloaded locally as a ZIP archive.

## Vendored dependency

`vendor/docx-9.6.1/docx.iife.js`

- Package: `docx`
- Version: `9.6.1`
- SHA-256: `ecef72931c98461fc327aa6e95867820aced5db4c3d971ac5ad38ccda21dd360`
- License: MIT, included in the same directory

## Deployment

Serve the files only over HTTPS. Do not add analytics, tag managers, remote
fonts or third-party scripts without reviewing the privacy impact and updating
the Content Security Policy.

GitHub Pages cannot set all HTTP security headers. The application therefore
uses an HTML CSP. If it is later moved to a host with configurable headers, add
the same CSP as an HTTP response header together with `X-Content-Type-Options:
nosniff`, `Permissions-Policy` and `frame-ancestors 'none'`.
