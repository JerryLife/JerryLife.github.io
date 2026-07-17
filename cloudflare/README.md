# Cloudflare OAuth Proxy

This directory contains a standalone Cloudflare Worker that supplies the
GitHub OAuth callback required by the Decap CMS GitHub backend. It is designed
for this site's public repository and does not require a database, R2, KV, or
GitHub Actions secret.

The Worker has two routes:

- `GET /auth?provider=github` starts the OAuth popup flow.
- `GET /callback` exchanges GitHub's one-time code and completes Decap's
  `window.postMessage` handshake.

## Configuration checklist

1. Copy the template and replace every placeholder:

   ```sh
   cd cloudflare
   cp wrangler.toml.example wrangler.toml
   ```

   This configuration sets `keep_vars = true`, so undeclared Dashboard-managed
   bindings are retained on deploy. Keep that setting when deploying this
   Worker: it preserves the existing Dashboard `GITHUB_CLIENT_ID` variable and
   the two OAuth secrets.

2. Set these non-secret Cloudflare Worker variables in `wrangler.toml`:

   - `CMS_ALLOWED_GITHUB_LOGIN`: the one GitHub login allowed to use the CMS
     (`JerryLife` for this site).
   - `CMS_REPOSITORY`: the exact `owner/repository` managed by the CMS.
   - `CMS_BRANCH`: the branch Decap writes to, normally `main`.
   - `CMS_ALLOWED_ORIGINS`: exact comma-separated website origins that may
     receive an OAuth token, such as `https://site.example`. Use an origin, not
     a path; `http://localhost` and `http://127.0.0.1` are accepted only for
     local development.

3. Deploy once to learn the Worker base URL:

   ```sh
   npx wrangler login
   npx wrangler deploy
   ```

   Use either the generated `https://<worker>.<account>.workers.dev` URL or a
   dedicated custom domain. A custom domain can be configured with the
   commented `route` example in `wrangler.toml.example`.

4. Create a GitHub OAuth App at GitHub Settings, Developer settings, OAuth
   Apps. Its Authorization callback URL must be exactly:

   ```text
   <WORKER_BASE_URL>/callback
   ```

   The Worker derives this same callback URL from the public request URL, so
   the Worker base URL, GitHub OAuth App callback URL, and Decap `base_url`
   must all use the same hostname. GitHub OAuth Apps do not accept callback
   URL wildcards.

5. Keep `GITHUB_CLIENT_ID` as a non-secret Worker Variable in the Cloudflare
   Dashboard. Store the two secret values in Cloudflare Worker Secrets, never
   in `wrangler.toml`, the repository, or GitHub Actions secrets:

   ```sh
   npx wrangler secret put GITHUB_CLIENT_SECRET
   npx wrangler secret put OAUTH_STATE_SECRET
   ```

   `OAUTH_STATE_SECRET` must be at least 32 characters. Generate a random
   value with `openssl rand -hex 48` and rotate it whenever an administrator
   leaves or a secret may have been exposed.

   Before a deployment, confirm only the secret binding names with:

   ```sh
   npx wrangler secret list
   ```

   The expected names are `GITHUB_CLIENT_SECRET` and `OAUTH_STATE_SECRET`.
   Do not recreate those secrets when they are already listed.

6. Deploy again after setting the secrets:

   ```sh
   npx wrangler deploy
   ```

## Decap CMS configuration

Configure the site's `admin/config.yml` with values matching the Worker:

```yaml
backend:
  name: github
  repo: owner/repository
  branch: main
  base_url: <WORKER_BASE_URL>
  auth_endpoint: auth
```

`<WORKER_BASE_URL>` is the public origin only, with no trailing `/auth` or
`/callback` path. The `repo` and `branch` values must exactly match
`CMS_REPOSITORY` and `CMS_BRANCH` in the Worker configuration.

## Security model

- `GITHUB_CLIENT_ID` is a non-secret Cloudflare Worker Variable;
  `GITHUB_CLIENT_SECRET` and `OAUTH_STATE_SECRET` are Cloudflare Worker
  Secrets. A GitHub Actions secret cannot protect a static browser application
  because Actions secrets are unavailable to it at login time.
- OAuth state is HMAC-signed and is additionally bound to the browser through
  a short-lived, host-only, `HttpOnly`, `Secure`, `SameSite=Lax` cookie. The
  callback rejects an expired, modified, cross-host, or cross-browser state.
- The callback posts the access token only to the origin selected from
  `CMS_ALLOWED_ORIGINS`; it never uses `*` as a `postMessage` target origin.
- Before returning a token, the Worker checks the signed-in GitHub login,
  verifies `push` permission on `CMS_REPOSITORY`, and confirms that
  `CMS_BRANCH` exists.
- The OAuth scope is limited to `public_repo read:user`, appropriate for a
  public repository. GitHub OAuth App tokens are user-scoped rather than
  repository-scoped; restricting the CMS account and the site's allowed
  origin is therefore important.
- The Worker does not persist tokens or content. GitHub receives writes
  directly from Decap CMS after the popup closes.

## Test and operate

After deployment, `GET <WORKER_BASE_URL>/health` should return a short health
message. Test the complete flow by opening the deployed `/admin/` page and
signing in with `CMS_ALLOWED_GITHUB_LOGIN`. A different GitHub account, an
unknown branch, or a site outside `CMS_ALLOWED_ORIGINS` must be rejected.

For local CMS development, add the local origin to `CMS_ALLOWED_ORIGINS`, for
example `http://localhost:4000`, deploy the updated Worker configuration, and
keep the GitHub OAuth App callback pointed at the deployed Worker. Remove the
local origin when testing is complete.
