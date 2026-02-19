# Node SDK Proxy/Request Signer Runbook

## 1. Overview

This example contains a single-file Node.js proxy (`proxy-sdk.js`) intended to be used in conjunction with Claude Code that signs Anthropic-compatible `/v1/messages` requests with the OCI Node SDK and forwards them to your OCI Data Science Model Deployment. Run it on a workstation with network access to the OCI endpoint; Claude desktop or CLI clients can then point at `http://127.0.0.1:<PORT>`.

## 2. Contents

- `proxy-sdk.js` – local HTTP proxy that signs and forwards requests.
- `package.json` / `package-lock.json` – pin `oci-common` and `undici` dependencies.
- `.env.example` – sample environment variable template for required exports.
- `Makefile` – helper commands to run the proxy and Claude.

## 3. Prerequisites

- macOS/Linux/Windows host with Node.js 18+ and npm.
- OCI CLI installed and configured with a profile that uses session authentication (security token + key file).
- Access to the target OCI Model Deployment invoke endpoint (for example `https://modeldeployment.<region>.oci.oc-test.com/<mdOcid>`).
- A Claude desktop/CLI installation for end-to-end validation.
- A vLLM-backed model deployment configured with `--tool-call-parser <parser - openai, etc.>`, `--enable-auto-tool-choice`, and `--max-model-len` ≥ 32000.

## 4. One-Time OCI Authentication

1. Launch an OCI session for the desired tenancy/profile. Example helper alias:
   ```bash
   alias oci-session='oci session authenticate --region us-ashburn-1 --profile-name DEFAULT --tenancy-name <tenancy>'
   oci-session
   ```
2. Confirm the target profile in `~/.oci/config` now contains `security_token_file` and `key_file` entries populated by the session command.

## 5. Environment Variables

Populate these variables (copy `.env.example` → `.env` and edit):

```dotenv
OCI_PROFILE=DEFAULT
OCI_CONFIG_FILE=~/.oci/config
OCI_BASE_URL=https://modeldeployment.<region>.oci.oc-test.com/<mdOcid>
OCI_INVOKE_PREFIX=/predictWithResponseStream
PORT=8080
ANTHROPIC_BASE_URL=http://127.0.0.1:8080
ANTHROPIC_API_KEY=dummy
ANTHROPIC_DEFAULT_OPUS_MODEL=openai/gpt-oss-20b
ANTHROPIC_DEFAULT_SONNET_MODEL=openai/gpt-oss-20b
ANTHROPIC_DEFAULT_HAIKU_MODEL=openai/gpt-oss-20b
```

Notes:
- `OCI_BASE_URL` must stop at the MD OCID path (no `/predictWithResponseStream` or `/v1/messages`).
- Localhost and port default to `http://127.0.0.1:8080`; adjust `PORT` if needed.

## 6. Make Targets

- `make deps` – install npm dependencies.
- `make start-proxy` – run the proxy with env vars from `.env`; logs go to `proxy.log` and PID → `.proxy.pid`.
- `make stop-proxy` – stop the background proxy process.
- `make run-claude` – launch the Claude CLI with proxy-aware env vars and proxy bypass for corporate networks.
- `make proxy-and-claude` – start the proxy, then run Claude, automatically stopping the proxy afterward.

Example combined flow:

```bash
cp .env.example .env && $EDITOR .env
make proxy-and-claude
```

## 7. Install & Run Manually

If you prefer direct commands:

```bash
npm install
node proxy-sdk.js > proxy.log 2>&1 &
tail -f proxy.log
```

## 8. Smoke Test

```bash
curl -s "http://127.0.0.1:${PORT}/v1/messages?beta=true" \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"ping"}],"max_tokens":20}'
```

Expect an Anthropic-compatible JSON response or streaming payload.

## 9. Using with Claude

When `make run-claude` is not used, export the same variables manually and start `claude`. Ensure the selected workspace model matches the OCI deployment.

## 10. Troubleshooting Quick Hits

- **401/403 from upstream** – refresh the OCI session, verify profile names, confirm system clock accuracy.
- **404 from upstream** - Ensure model deployment endpoint is correct and accessible.
- **`MODULE_NOT_FOUND`** – re-run `npm install` in the bundle folder.
- **Connection refused** – confirm the proxy log shows `listening` and that `ANTHROPIC_BASE_URL` matches `http://127.0.0.1:<PORT>`.
- **`count_tokens` errors** – retry with valid JSON; the proxy shims the endpoint locally.
- **Corporate proxy interference** – use `make run-claude` to launch with proxy bypass environment.

## 11. Clean Up

Stop the proxy (`make stop-proxy`) and delete temporary logs when finished. OCI session tokens expire automatically; re-run `oci session authenticate` as needed.
