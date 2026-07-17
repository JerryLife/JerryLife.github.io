/**
 * Minimal GitHub OAuth proxy for Decap CMS.
 *
 * This Worker never stores GitHub access tokens. It only exchanges the
 * one-time OAuth code, validates the signed-in user and repository access,
 * then returns the token to the CMS popup using Decap's postMessage protocol.
 */

export interface Env {
  GITHUB_CLIENT_ID: string;
  GITHUB_CLIENT_SECRET: string;
  OAUTH_STATE_SECRET: string;
  CMS_ALLOWED_GITHUB_LOGIN: string;
  CMS_REPOSITORY: string;
  CMS_BRANCH: string;
  CMS_ALLOWED_ORIGINS: string;
}

interface Config {
  allowedGithubLogin: string;
  repository: string;
  branch: string;
  allowedCmsOrigins: Set<string>;
}

interface OAuthState {
  version: 1;
  nonce: string;
  cmsOrigin: string;
  callbackOrigin: string;
  expiresAt: number;
}

interface GitHubTokenResponse {
  access_token?: string;
  error?: string;
  error_description?: string;
}

interface GitHubUser {
  login?: string;
}

interface GitHubRepository {
  permissions?: {
    push?: boolean;
  };
}

const GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize";
const GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token";
const GITHUB_API_URL = "https://api.github.com";
const STATE_VERSION = "v1";
const STATE_TTL_MS = 10 * 60 * 1000;
const STATE_COOKIE_PREFIX = "__Host-decap-oauth-state-";
const TEXT_ENCODER = new TextEncoder();
const TEXT_DECODER = new TextDecoder();

function securityHeaders(contentType: string): Headers {
  return new Headers({
    "Cache-Control": "no-store, max-age=0",
    "Content-Security-Policy": "default-src 'none'; base-uri 'none'; frame-ancestors 'none'",
    "Content-Type": contentType,
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
  });
}

function textResponse(message: string, status = 200, extraHeaders?: HeadersInit): Response {
  const headers = securityHeaders("text/plain; charset=utf-8");
  if (extraHeaders) {
    for (const [name, value] of new Headers(extraHeaders)) {
      headers.append(name, value);
    }
  }

  return new Response(message, { status, headers });
}

function htmlResponse(html: string, extraHeaders?: HeadersInit): Response {
  const headers = securityHeaders("text/html; charset=utf-8");
  // The callback must use a small inline script for Decap's popup handshake.
  headers.set(
    "Content-Security-Policy",
    "default-src 'none'; script-src 'unsafe-inline'; base-uri 'none'; frame-ancestors 'none'"
  );
  if (extraHeaders) {
    for (const [name, value] of new Headers(extraHeaders)) {
      headers.append(name, value);
    }
  }

  return new Response(html, { status: 200, headers });
}

function isLocalHttpOrigin(url: URL): boolean {
  return (
    url.protocol === "http:" &&
    (url.hostname === "localhost" || url.hostname === "127.0.0.1" || url.hostname === "[::1]")
  );
}

function parseOrigin(value: string, variableName: string): string {
  let url: URL;
  try {
    url = new URL(value);
  } catch {
    throw new Error(`${variableName} must contain valid origins.`);
  }

  if (
    url.username ||
    url.password ||
    url.pathname !== "/" ||
    url.search ||
    url.hash ||
    (url.protocol !== "https:" && !isLocalHttpOrigin(url))
  ) {
    throw new Error(`${variableName} must contain HTTPS origins only.`);
  }

  return url.origin;
}

function parseRepository(value: string): string {
  const parts = value.trim().split("/");
  if (parts.length !== 2 || parts.some(part => !/^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}$/.test(part))) {
    throw new Error("CMS_REPOSITORY must be in owner/repository format.");
  }

  return parts.join("/");
}

function validateConfig(env: Env): Config {
  const login = env.CMS_ALLOWED_GITHUB_LOGIN?.trim();
  if (!login || !/^[A-Za-z0-9][A-Za-z0-9-]{0,38}$/.test(login)) {
    throw new Error("CMS_ALLOWED_GITHUB_LOGIN is invalid.");
  }

  const branch = env.CMS_BRANCH?.trim();
  if (!branch || branch.length > 255 || /[\u0000-\u001f\u007f]/.test(branch)) {
    throw new Error("CMS_BRANCH is invalid.");
  }

  const origins = env.CMS_ALLOWED_ORIGINS?.split(",")
    .map(origin => origin.trim())
    .filter(Boolean);
  if (!origins?.length) {
    throw new Error("CMS_ALLOWED_ORIGINS is required.");
  }

  const allowedCmsOrigins = new Set(origins.map(origin => parseOrigin(origin, "CMS_ALLOWED_ORIGINS")));
  if (!env.GITHUB_CLIENT_ID?.trim() || !env.GITHUB_CLIENT_SECRET?.trim()) {
    throw new Error("GitHub OAuth credentials are not configured.");
  }
  if (!env.OAUTH_STATE_SECRET || env.OAUTH_STATE_SECRET.length < 32) {
    throw new Error("OAUTH_STATE_SECRET must be at least 32 characters.");
  }

  return {
    allowedGithubLogin: login.toLowerCase(),
    repository: parseRepository(env.CMS_REPOSITORY),
    branch,
    allowedCmsOrigins,
  };
}

function bytesToBase64Url(bytes: Uint8Array): string {
  let binary = "";
  for (const byte of bytes) {
    binary += String.fromCharCode(byte);
  }

  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

function base64UrlToBytes(value: string): Uint8Array | null {
  if (!/^[A-Za-z0-9_-]+$/.test(value)) {
    return null;
  }

  try {
    const padded = value.replace(/-/g, "+").replace(/_/g, "/") + "=".repeat((4 - (value.length % 4)) % 4);
    const binary = atob(padded);
    return Uint8Array.from(binary, character => character.charCodeAt(0));
  } catch {
    return null;
  }
}

function randomBase64Url(bytes: number): string {
  const randomBytes = new Uint8Array(bytes);
  crypto.getRandomValues(randomBytes);
  return bytesToBase64Url(randomBytes);
}

function toArrayBuffer(bytes: Uint8Array): ArrayBuffer {
  const copy = new Uint8Array(bytes.byteLength);
  copy.set(bytes);
  return copy.buffer;
}

async function getStateKey(secret: string): Promise<CryptoKey> {
  return crypto.subtle.importKey(
    "raw",
    TEXT_ENCODER.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign", "verify"]
  );
}

async function createSignedState(state: OAuthState, secret: string): Promise<string> {
  const payload = bytesToBase64Url(TEXT_ENCODER.encode(JSON.stringify(state)));
  const signedValue = `${STATE_VERSION}.${payload}`;
  const signature = new Uint8Array(await crypto.subtle.sign("HMAC", await getStateKey(secret), TEXT_ENCODER.encode(signedValue)));
  return `${signedValue}.${bytesToBase64Url(signature)}`;
}

async function verifySignedState(value: string, secret: string): Promise<OAuthState | null> {
  if (value.length > 2048) {
    return null;
  }

  const parts = value.split(".");
  if (parts.length !== 3 || parts[0] !== STATE_VERSION) {
    return null;
  }

  const [version, payload, encodedSignature] = parts;
  const signature = base64UrlToBytes(encodedSignature);
  const decodedPayload = base64UrlToBytes(payload);
  if (!signature || !decodedPayload) {
    return null;
  }

  const signatureIsValid = await crypto.subtle.verify(
    "HMAC",
    await getStateKey(secret),
    toArrayBuffer(signature),
    TEXT_ENCODER.encode(`${version}.${payload}`)
  );
  if (!signatureIsValid) {
    return null;
  }

  try {
    const parsed = JSON.parse(TEXT_DECODER.decode(decodedPayload)) as Partial<OAuthState>;
    if (
      parsed.version !== 1 ||
      typeof parsed.nonce !== "string" ||
      !/^[A-Za-z0-9_-]{43}$/.test(parsed.nonce) ||
      typeof parsed.cmsOrigin !== "string" ||
      typeof parsed.callbackOrigin !== "string" ||
      typeof parsed.expiresAt !== "number"
    ) {
      return null;
    }

    const now = Date.now();
    // A state is minted for STATE_TTL_MS. Allow a small cross-edge clock skew
    // while still rejecting values with an unexpectedly long lifetime.
    if (parsed.expiresAt < now || parsed.expiresAt > now + STATE_TTL_MS + 60_000) {
      return null;
    }

    return parsed as OAuthState;
  } catch {
    return null;
  }
}

function stateCookieName(nonce: string): string {
  return `${STATE_COOKIE_PREFIX}${nonce}`;
}

function stateCookie(name: string, value: string, maxAge: number): string {
  return `${name}=${value}; HttpOnly; Path=/; Max-Age=${maxAge}; SameSite=Lax; Secure`;
}

function getCookie(request: Request, name: string): string | null {
  const cookieHeader = request.headers.get("Cookie");
  if (!cookieHeader) {
    return null;
  }

  for (const item of cookieHeader.split(";")) {
    const separator = item.indexOf("=");
    if (separator === -1) {
      continue;
    }

    if (item.slice(0, separator).trim() === name) {
      return item.slice(separator + 1).trim();
    }
  }

  return null;
}

function constantTimeEqual(left: string, right: string): boolean {
  if (left.length !== right.length) {
    return false;
  }

  let difference = 0;
  for (let index = 0; index < left.length; index += 1) {
    difference |= left.charCodeAt(index) ^ right.charCodeAt(index);
  }

  return difference === 0;
}

function callbackUrlFor(requestUrl: URL): string {
  return new URL("/callback", requestUrl.origin).toString();
}

function originFromHeader(value: string): string | null {
  try {
    return new URL(value).origin;
  } catch {
    return null;
  }
}

function callerCmsOrigin(request: Request, allowedOrigins: Set<string>): string | null {
  const originHeader = request.headers.get("Origin");
  const referrerHeader = request.headers.get("Referer");
  const suppliedOrigin = originHeader ? originFromHeader(originHeader) : referrerHeader ? originFromHeader(referrerHeader) : null;

  if (suppliedOrigin) {
    return allowedOrigins.has(suppliedOrigin) ? suppliedOrigin : null;
  }

  return allowedOrigins.size === 1 ? [...allowedOrigins][0] : null;
}

function githubHeaders(accessToken: string): Headers {
  return new Headers({
    Accept: "application/vnd.github+json",
    Authorization: `Bearer ${accessToken}`,
    "User-Agent": "decap-cms-cloudflare-oauth-proxy",
    "X-GitHub-Api-Version": "2022-11-28",
  });
}

async function githubJson<T>(path: string, accessToken: string): Promise<{ response: Response; body: T | null }> {
  const response = await fetch(`${GITHUB_API_URL}${path}`, { headers: githubHeaders(accessToken) });
  try {
    return { response, body: (await response.json()) as T };
  } catch {
    return { response, body: null };
  }
}

async function exchangeCode(code: string, callbackUrl: string, env: Env): Promise<string | null> {
  const body = new URLSearchParams({
    client_id: env.GITHUB_CLIENT_ID,
    client_secret: env.GITHUB_CLIENT_SECRET,
    code,
    redirect_uri: callbackUrl,
  });
  const response = await fetch(GITHUB_TOKEN_URL, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body,
  });

  let payload: GitHubTokenResponse | null = null;
  try {
    payload = (await response.json()) as GitHubTokenResponse;
  } catch {
    // The status check below returns a generic error without exposing a response body.
  }

  return response.ok && payload?.access_token ? payload.access_token : null;
}

async function tokenCanManageCms(accessToken: string, config: Config): Promise<boolean> {
  const user = await githubJson<GitHubUser>("/user", accessToken);
  if (!user.response.ok || user.body?.login?.toLowerCase() !== config.allowedGithubLogin) {
    return false;
  }

  const repository = await githubJson<GitHubRepository>(`/repos/${config.repository}`, accessToken);
  if (!repository.response.ok || repository.body?.permissions?.push !== true) {
    return false;
  }

  const branch = await githubJson<unknown>(`/repos/${config.repository}/branches/${encodeURIComponent(config.branch)}`, accessToken);
  return branch.response.ok;
}

function scriptLiteral(value: string): string {
  return JSON.stringify(value)
    .replace(/</g, "\\u003c")
    .replace(/>/g, "\\u003e")
    .replace(/&/g, "\\u0026")
    .replace(/\u2028/g, "\\u2028")
    .replace(/\u2029/g, "\\u2029");
}

function decapCallbackResponse(accessToken: string, cmsOrigin: string, clearCookie: string): Response {
  const authorizationMessage = `authorization:github:success:${JSON.stringify({ token: accessToken })}`;
  const html = `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="referrer" content="no-referrer">
    <title>Authorizing Decap</title>
  </head>
  <body>
    <p>Authorizing Decap...</p>
    <script>
      (() => {
        const targetOrigin = ${scriptLiteral(cmsOrigin)};
        const authorizationMessage = ${scriptLiteral(authorizationMessage)};
        const opener = window.opener;
        if (!opener) {
          return;
        }

        const receiveMessage = event => {
          if (event.origin !== targetOrigin || event.source !== opener) {
            return;
          }
          opener.postMessage(authorizationMessage, targetOrigin);
          window.removeEventListener("message", receiveMessage, false);
          window.setTimeout(() => window.close(), 0);
        };

        window.addEventListener("message", receiveMessage, false);
        opener.postMessage("authorizing:github", targetOrigin);
      })();
    </script>
  </body>
</html>`;

  return htmlResponse(html, { "Set-Cookie": clearCookie });
}

function callbackFailure(message: string, cookieName?: string): Response {
  const headers = cookieName ? { "Set-Cookie": stateCookie(cookieName, "", 0) } : undefined;
  return textResponse(message, 400, headers);
}

async function handleAuth(request: Request, url: URL, env: Env, config: Config): Promise<Response> {
  if (url.searchParams.get("provider") !== "github") {
    return textResponse("Only the GitHub OAuth provider is supported.", 400);
  }

  const cmsOrigin = callerCmsOrigin(request, config.allowedCmsOrigins);
  if (!cmsOrigin) {
    return textResponse("The CMS origin is not allowed.", 403);
  }

  const callbackUrl = callbackUrlFor(url);
  const nonce = randomBase64Url(32);
  const state = await createSignedState(
    {
      version: 1,
      nonce,
      cmsOrigin,
      callbackOrigin: url.origin,
      expiresAt: Date.now() + STATE_TTL_MS,
    },
    env.OAUTH_STATE_SECRET
  );
  const authorizationUrl = new URL(GITHUB_AUTHORIZE_URL);
  authorizationUrl.search = new URLSearchParams({
    client_id: env.GITHUB_CLIENT_ID,
    redirect_uri: callbackUrl,
    scope: "public_repo read:user",
    state,
  }).toString();

  return new Response(null, {
    status: 302,
    headers: {
      "Cache-Control": "no-store, max-age=0",
      Location: authorizationUrl.toString(),
      "Referrer-Policy": "no-referrer",
      "Set-Cookie": stateCookie(stateCookieName(nonce), state, Math.ceil(STATE_TTL_MS / 1000)),
    },
  });
}

async function handleCallback(request: Request, url: URL, env: Env, config: Config): Promise<Response> {
  const stateValue = url.searchParams.get("state");
  if (!stateValue) {
    return callbackFailure("OAuth state is missing.");
  }

  const state = await verifySignedState(stateValue, env.OAUTH_STATE_SECRET);
  if (!state || state.callbackOrigin !== url.origin || !config.allowedCmsOrigins.has(state.cmsOrigin)) {
    return callbackFailure("OAuth state is invalid or expired.");
  }

  const cookieName = stateCookieName(state.nonce);
  const cookieValue = getCookie(request, cookieName);
  if (!cookieValue || !constantTimeEqual(cookieValue, stateValue)) {
    return callbackFailure("OAuth state could not be verified.", cookieName);
  }

  if (url.searchParams.get("error")) {
    return callbackFailure("GitHub authorization was cancelled or denied.", cookieName);
  }

  const code = url.searchParams.get("code");
  if (!code || code.length > 2048) {
    return callbackFailure("GitHub did not return a valid authorization code.", cookieName);
  }

  const accessToken = await exchangeCode(code, callbackUrlFor(url), env);
  if (!accessToken) {
    return callbackFailure("GitHub could not complete the token exchange.", cookieName);
  }

  if (!(await tokenCanManageCms(accessToken, config))) {
    return callbackFailure("This GitHub account is not permitted to manage the CMS.", cookieName);
  }

  return decapCallbackResponse(accessToken, state.cmsOrigin, stateCookie(cookieName, "", 0));
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    if (request.method !== "GET") {
      return textResponse("Method not allowed.", 405, { Allow: "GET" });
    }

    let config: Config;
    try {
      config = validateConfig(env);
    } catch (error) {
      console.error("Decap OAuth proxy configuration error:", error instanceof Error ? error.message : "unknown error");
      return textResponse("OAuth proxy configuration is incomplete.", 500);
    }

    const url = new URL(request.url);
    try {
      if (url.pathname === "/auth") {
        return await handleAuth(request, url, env, config);
      }
      if (url.pathname === "/callback") {
        return await handleCallback(request, url, env, config);
      }
      if (url.pathname === "/" || url.pathname === "/health") {
        return textResponse("Decap CMS OAuth proxy is running.");
      }
      return textResponse("Not found.", 404);
    } catch (error) {
      console.error("Decap OAuth proxy request failed:", error instanceof Error ? error.message : "unknown error");
      return textResponse("OAuth proxy request failed.", 500);
    }
  },
};
