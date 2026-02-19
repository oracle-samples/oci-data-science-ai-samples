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
  - **IMPORTANT FIRST TIME USAGE INSTRUCTIONS:**
    -   After installation and prior to starting Claude Code, update `~/.claude.json` with `{"hasCompletedOnboarding": true}` in order to bypass Anthropic's required account creation and login and to skip in this integration.
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
# Refer to First Time Setup prior to next step if nor previously onboarded
make proxy-and-claude
```

## 7. First Time Setup

- **Anthropic requires an account login on first time usage, to bypass this, add `{"hasCompletedOnboarding": true}` to `~/.claude.json`.**
  - If you **did not do this** and you see the following you can exit and enter `{"hasCompletedOnboarding": true}` in `~/.claude.json`, otherwise proceed with creating an Anthropic account (Selection 1).:
    ```
      Welcome to Claude Code v2.1.25
      …………………………………………………………………………………………………………………………………………………………

          *                                       █████▓▓░
                                      *         ███▓░     ░░
                  ░░░░░░                        ███▓░
          ░░░   ░░░░░░░░░░                      ███▓░
        ░░░░░░░░░░░░░░░░░░░    *                ██▓░░      ▓
                                                  ░▓▓███▓▓░
      *                                 ░░░░
                                      ░░░░░░░░
                                    ░░░░░░░░░░░░░░░░
            █████████                                        *
            ██▄█████▄██                        *
            █████████      *
      …………………█ █   █ █………………………………………………………………………………………………………………


      Claude Code can be used with your Claude subscription or billed based on API usage through your Console account.

      Select login method:

        1. Claude account with subscription · Pro, Max, Team, or Enterprise

        2. Anthropic Console account · API usage billing

        3. 3rd-party platform · Amazon Bedrock, Microsoft Foundry, or Vertex AI
    ```
  - Claude Code will walk through multiple selections during first time usage.
    - Select desired theme:
      ```
      Welcome to Claude Code v2.1.25
      …………………………………………………………………………………………………………………………………………………………

          *                                       █████▓▓░
                                      *         ███▓░     ░░
                  ░░░░░░                        ███▓░
          ░░░   ░░░░░░░░░░                      ███▓░
        ░░░░░░░░░░░░░░░░░░░    *                ██▓░░      ▓
                                                  ░▓▓███▓▓░
      *                                 ░░░░
                                      ░░░░░░░░
                                    ░░░░░░░░░░░░░░░░
            █████████                                        *
            ██▄█████▄██                        *
            █████████      *
      …………………█ █   █ █………………………………………………………………………………………………………………
      Let's get started.

      Choose the text style that looks best with your terminal
      To change this later, run /theme

        1. Dark mode ✔
        2. Light mode
        3. Dark mode (colorblind-friendly)
        4. Light mode (colorblind-friendly)
        5. Dark mode (ANSI colors only)
        6. Light mode (ANSI colors only)

      1  function greet() {
      2 -  console.log("Hello, World!");
      2 +  console.log("Hello, Claude!");
      3  }
      ```
    - Confirm or Deny trust in the current working directory (Select 1):
      ```
      Quick safety check: Is this a project you created or one you trust? (Like your own code, a well-known open source project, or work from your team). If not, take a moment to review what's in this folder first.

      Claude Code'll be able to read, edit, and execute files here.

      Security guide

      ❯ 1. Yes, I trust this folder
        2. No, exit

      Enter to confirm · Esc to cancel
      ```
    - Confirm usage of custom API key from environment variable (Select 1. (Yes)):
      ```
      Detected a custom API key in your environment

      ANTHROPIC_API_KEY: sk-ant-...dummy

      Do you want to use this API key?

        1. Yes
      ❯ 2. No (recommended) ✔

      Enter to confirm · Esc to cancel
      ```
    - You should now see the Claude Code CLI:
      ```

      ╭─── Claude Code v2.1.25 ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
      │                                                   │ Tips for getting started                                                       │
      │                   Welcome back!                   │ Run /init to create a CLAUDE.md file with instructions for Claude              │
      │                                                   │ ─────────────────────────────────────────────────────────────────              │
      │                                                   │ Recent activity                                                                │
      │                      ▐▛███▜▌                      │ No recent activity                                                             │
      │                     ▝▜█████▛▘                     │                                                                                │
      │                       ▘▘ ▝▝                       │                                                                                │
      │      openai/gpt-oss-20b · API Usage Billing       │                                                                                │
      │   ~/…/model-deployment/claude_integration_proxy   │                                                                                │
      ╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

        /model to try Opus 4.5

      ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
      ❯ Try "refactor <filepath>"
      ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
        ? for shortcuts                                                                    Update available! Run: brew upgrade claude-code
      ```
    - Example Query and Output:
      ```
      ╭─── Claude Code v2.1.25 ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
      │                                                   │ Tips for getting started                                                       │
      │                   Welcome back!                   │ Run /init to create a CLAUDE.md file with instructions for Claude              │
      │                                                   │ ─────────────────────────────────────────────────────────────────              │
      │                                                   │ Recent activity                                                                │
      │                      ▐▛███▜▌                      │ No recent activity                                                             │
      │                     ▝▜█████▛▘                     │                                                                                │
      │                       ▘▘ ▝▝                       │                                                                                │
      │      openai/gpt-oss-20b · API Usage Billing       │                                                                                │
      │   ~/…/model-deployment/claude_integration_proxy   │                                                                                │
      ╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

        /model to try Opus 4.5

      ❯ Create a python function to print "Hello, World!" ten times.

      ⏺ Searched for 3 patterns (ctrl+o to expand)

      ⏺ Write(hello_world.py)
        ⎿  Wrote 4 lines to hello_world.py
            1 def print_hello_world():
            2     for _ in range(10):
            3         print("Hello, World!")

      ⏺ A new file hello_world.py has been created with the requested function:

        def print_hello_world():
            for _ in range(10):
                print("Hello, World!")

        You can now import and run print_hello_world() in your Python environment.

      ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
      ❯
      ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
        1 file +0 -0                                                                       Update available! Run: brew upgrade claude-code
      ```
## 8. Install & Run Manually

If you prefer direct commands:

```bash
npm install
node proxy-sdk.js > proxy.log 2>&1 &
tail -f proxy.log
```

## 9. Smoke Test

```bash
curl -s "http://127.0.0.1:${PORT}/v1/messages?beta=true" \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"ping"}],"max_tokens":20}'
```

Expect an Anthropic-compatible JSON response or streaming payload.

## 10. Using with Claude

When `make run-claude` is not used, export the same variables manually and start `claude`. Ensure the selected workspace model matches the OCI deployment.

## 11. Troubleshooting Quick Hits

- **401/403 from upstream** – refresh the OCI session, verify profile names, confirm system clock accuracy.
- **404 from upstream** - Ensure model deployment endpoint is correct and accessible.
- **502 from upstream/gateway** - Ensure correctness of Environment Variables including `ANTHROPIC_BASE_URL` and `OCI_BASE_URL`.
- **`MODULE_NOT_FOUND`** – re-run `npm install` in the bundle folder.
- **Connection refused** – confirm the proxy log shows `listening` and that `ANTHROPIC_BASE_URL` matches `http://127.0.0.1:<PORT>`.
- **`count_tokens` errors** – retry with valid JSON; the proxy shims the endpoint locally.
- **Corporate proxy interference** – use `make run-claude` to launch with proxy bypass environment.

## 12. Clean Up

Stop the proxy (`make stop-proxy`) and delete temporary logs when finished. OCI session tokens expire automatically; re-run `oci session authenticate` as needed.
