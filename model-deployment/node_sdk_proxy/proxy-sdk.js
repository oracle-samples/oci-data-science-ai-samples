const http = require('http');
const https = require('https');
const { URL } = require('url');
const crypto = require('crypto');
const fs = require('fs');
const os = require('os');
const path = require('path');

const common = require('oci-common');
const { Headers } = require('undici'); // just for Headers interface expected by signer

const PORT = Number(process.env.PORT || 8080);
const OCI_PROFILE = process.env.OCI_PROFILE || process.env.OCI_CLI_PROFILE || 'DEFAULT';
const OCI_CONFIG_FILE = expandHome(process.env.OCI_CONFIG_FILE || '~/.oci/config');

const OCI_BASE_URL = process.env.OCI_BASE_URL; // REQUIRED: https://.../<modelDeploymentOcid>
if (!OCI_BASE_URL) {
  throw new Error('OCI_BASE_URL is required (must be the model deployment base URL ending in the deployment OCID path).');
}
const INVOKE_PREFIX = process.env.OCI_INVOKE_PREFIX || '/predictWithResponseStream';

const HOP_BY_HOP_HEADERS = new Set([
  'connection','keep-alive','proxy-authenticate','proxy-authorization','te','trailer','transfer-encoding','upgrade',
]);

// Keep-alive for outbound TLS
const httpsAgent = new https.Agent({ keepAlive: true });

function expandHome(p) {
  if (!p) return p;
  if (p.startsWith('~/')) return path.join(os.homedir(), p.slice(2));
  return p;
}

function parseIni(text) {
  const out = {};
  let section = null;
  for (const raw of text.split(/\r?\n/)) {
    const line = raw.trim();
    if (!line || line.startsWith('#') || line.startsWith(';')) continue;

    const sec = line.match(/^\[(.+?)\]$/);
    if (sec) {
      section = sec[1].trim();
      out[section] = out[section] || {};
      continue;
    }

    const idx = line.indexOf('=');
    if (idx === -1 || !section) continue;

    const k = line.slice(0, idx).trim();
    let v = line.slice(idx + 1).trim();
    v = v.replace(/^"(.*)"$/, '$1').replace(/^'(.*)'$/, '$1');
    out[section][k] = v;
  }
  return out;
}

async function readBody(req) {
  const chunks = [];
  for await (const c of req) chunks.push(c);
  return Buffer.concat(chunks);
}

function estimateTokensFromAnthropicMessages(reqJson) {
  try {
    const s = JSON.stringify(reqJson || {});
    return Math.max(1, Math.ceil(s.length / 4));
  } catch {
    return 1;
  }
}

function normalizeHeaderValue(v) {
  if (Array.isArray(v)) return v.join(', ');
  if (v == null) return '';
  return String(v);
}

function buildForwardHeaders(req, upstreamHost) {
  const out = {};
  for (const [k, v] of Object.entries(req.headers)) {
    const key = k.toLowerCase();
    if (HOP_BY_HOP_HEADERS.has(key)) continue;
    if (key === 'host' || key === 'content-length') continue;
    if (key === 'authorization' || key === 'x-api-key') continue;
    out[key] = normalizeHeaderValue(v);
  }
  out['host'] = upstreamHost;
  out['content-type'] = out['content-type'] || 'application/json';
  // This can reduce surprises with intermediates:
  out['accept-encoding'] = out['accept-encoding'] || 'identity';
  return out;
}

function addBodyHeaders(headersObj, bodyBuf) {
  const body = bodyBuf || Buffer.alloc(0);
  headersObj['content-length'] = String(body.length);
  headersObj['x-content-sha256'] =
    headersObj['x-content-sha256'] ||
    crypto.createHash('sha256').update(body).digest('base64');
  headersObj['date'] = headersObj['date'] || new Date().toUTCString();
}

function headersObjectToHeaders(obj) {
  const h = new Headers();
  for (const [k, v] of Object.entries(obj)) h.set(k, v);
  return h;
}

function headersToPlainObject(headers) {
  const out = {};
  for (const [k, v] of headers.entries()) out[k] = v;
  return out;
}

/**
 * Synchronous security-token auth provider compatible with DefaultRequestSigner.
 * Must return private key as Buffer.
 */
class SecurityTokenFileAuthProviderSync {
  constructor({ configFile, profile }) {
    const iniText = fs.readFileSync(configFile, 'utf8');
    const cfg = parseIni(iniText);
    const prof = cfg[profile];
    if (!prof) throw new Error(`Profile [${profile}] not found in ${configFile}`);

    const tokenFile = prof.security_token_file ? expandHome(prof.security_token_file) : null;
    const keyFile = prof.key_file ? expandHome(prof.key_file) : null;
    const pass = prof.pass_phrase || prof.passphrase || null;

    if (!tokenFile || !keyFile) {
      throw new Error(`Profile [${profile}] must include security_token_file and key_file. Run osa/oci session authenticate.`);
    }

    this.securityToken = fs.readFileSync(tokenFile, 'utf8').trim();
    this.privateKey = fs.readFileSync(keyFile); // Buffer
    this.passphrase = pass;
  }

  getKeyId() { return `ST$${this.securityToken}`; }
  getPrivateKey() { return this.privateKey; }
  getPassphrase() { return this.passphrase; }
  getSecurityToken() { return this.securityToken; }
}

const provider = new SecurityTokenFileAuthProviderSync({ configFile: OCI_CONFIG_FILE, profile: OCI_PROFILE });
const signer = new common.DefaultRequestSigner(provider);

async function signedHttpsRequest(targetUrlObj, method, headersObj, bodyBuf) {
  addBodyHeaders(headersObj, bodyBuf);

  // Required for security token auth
  headersObj['x-security-token'] = provider.getSecurityToken();

  // Signer expects Headers interface
  const signHeaders = headersObjectToHeaders(headersObj);
  const reqToSign = { method, uri: targetUrlObj.toString(), headers: signHeaders };
  await signer.signHttpRequest(reqToSign);

  // Safe debug
  const authz = reqToSign.headers.get('authorization') || '';
  const keyId = authz.match(/keyId="([^"]+)"/)?.[1] || '(none)';
  console.log('Signed keyId prefix:', keyId.slice(0, 3), 'has x-security-token:', reqToSign.headers.has('x-security-token'));

  const signedHeaders = headersToPlainObject(reqToSign.headers);
  const body = bodyBuf || Buffer.alloc(0);

  const pathWithQuery = targetUrlObj.pathname + (targetUrlObj.search || '');

  return new Promise((resolve, reject) => {
    const upstreamReq = https.request(
      {
        protocol: targetUrlObj.protocol,
        hostname: targetUrlObj.hostname,
        port: targetUrlObj.port || 443,
        method,
        path: pathWithQuery,
        headers: signedHeaders,
        agent: httpsAgent,

        // Workaround for upstream sending both Content-Length and Transfer-Encoding
        insecureHTTPParser: true,
      },
      (upstreamRes) => resolve(upstreamRes)
    );

    upstreamReq.on('error', reject);
    if (body.length) upstreamReq.write(body);
    upstreamReq.end();
  });
}

const server = http.createServer(async (req, res) => {
  try {
    const mdBase = new URL(OCI_BASE_URL);
    const reqUrl = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
    const incomingPath = reqUrl.pathname.startsWith('/') ? reqUrl.pathname : `/${reqUrl.pathname}`;

    if (incomingPath === '/v1/messages/count_tokens') {
      const bodyBuf = await readBody(req);
      let reqJson = null;
      try { reqJson = JSON.parse(bodyBuf.toString('utf8')); } catch {}
      const inputTokens = estimateTokensFromAnthropicMessages(reqJson);
      res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
      res.end(JSON.stringify({ input_tokens: inputTokens }));
      return;
    }

    // Compose upstream URL
    const targetUrlObj = new URL(mdBase.toString());
    targetUrlObj.pathname = mdBase.pathname.replace(/\/$/, '') + INVOKE_PREFIX + incomingPath;
    targetUrlObj.search = reqUrl.search;

    const bodyBuf = await readBody(req);
    const headersObj = buildForwardHeaders(req, targetUrlObj.host);

    console.log(`Forwarding ${req.method} ${incomingPath} -> ${targetUrlObj.toString()}`);

    const upstreamRes = await signedHttpsRequest(targetUrlObj, req.method, headersObj, bodyBuf);

    const contentType = upstreamRes.headers['content-type'] || 'application/json; charset=utf-8';
    console.log(`Upstream status=${upstreamRes.statusCode} content-type=${contentType}`);

    // Return upstream response; do NOT forward invalid hop-by-hop headers
    res.writeHead(upstreamRes.statusCode || 502, {
      'Content-Type': contentType,
      'Cache-Control': upstreamRes.headers['cache-control'] || 'no-cache',
    });

    // Pipe through (tolerates upstream’s TE/CL weirdness because Node’s http parser is lenient)
    upstreamRes.pipe(res);

    res.on('close', () => {
      try { upstreamRes.destroy(); } catch {}
    });
  } catch (e) {
    res.writeHead(502, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end(`Proxy error:\n${e.stack || e.message}`);
  }
});

server.listen(PORT, () => {
  console.log(`Proxy (oci-common signer + https client) listening on http://127.0.0.1:${PORT}`);
  console.log(`Using OCI profile [${OCI_PROFILE}] from ${OCI_CONFIG_FILE}`);
});