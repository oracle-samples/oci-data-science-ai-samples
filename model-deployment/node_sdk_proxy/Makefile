SHELL := /bin/bash
ENV_FILE ?= .env
PROXY_LOG ?= proxy.log
PROXY_PID_FILE ?= .proxy.pid
CLAUDE_BIN ?= claude
PORT ?= 8080
ANTHROPIC_BASE_URL ?= http://127.0.0.1:$(PORT)
ANTHROPIC_API_KEY ?= dummy
ANTHROPIC_DEFAULT_OPUS_MODEL ?= openai/gpt-oss-20b
ANTHROPIC_DEFAULT_SONNET_MODEL ?= openai/gpt-oss-20b
ANTHROPIC_DEFAULT_HAIKU_MODEL ?= openai/gpt-oss-20b

ifneq (,$(wildcard $(ENV_FILE)))
include $(ENV_FILE)
export $(shell sed -n 's/^\([A-Za-z_][A-Za-z0-9_]*\)=.*/\1/p' $(ENV_FILE))
endif

.PHONY: deps start-proxy stop-proxy run-claude proxy-and-claude

deps:
	npm install

start-proxy: deps
	@set -euo pipefail; \
	  : "${OCI_BASE_URL:?Define OCI_BASE_URL in $(ENV_FILE)}"; \
	  if [ -f $(PROXY_PID_FILE) ] && kill -0 $$(cat $(PROXY_PID_FILE)) 2>/dev/null; then \
	    echo "Proxy already running (PID $$(cat $(PROXY_PID_FILE)))."; \
	  else \
	    echo "Starting proxy on http://127.0.0.1:$(PORT) ..."; \
	    nohup env PORT="$(PORT)" node proxy-sdk.js > $(PROXY_LOG) 2>&1 & \
	    PID=$$!; \
	    echo $$PID > $(PROXY_PID_FILE); \
	    echo "Proxy PID $$PID (logs -> $(PROXY_LOG))."; \
	  fi

stop-proxy:
	@set -euo pipefail; \
	  if [ -f $(PROXY_PID_FILE) ]; then \
	    PID=$$(cat $(PROXY_PID_FILE)); \
	    if kill -0 $$PID 2>/dev/null; then \
	      kill $$PID && echo "Stopped proxy $$PID."; \
	    else \
	      echo "No proxy process found; removing stale PID file."; \
	    fi; \
	    rm -f $(PROXY_PID_FILE); \
	  else \
	    echo "Proxy is not running."; \
	  fi

run-claude:
	@set -euo pipefail; \
	  : "${ANTHROPIC_API_KEY:?Define ANTHROPIC_API_KEY in $(ENV_FILE)}"; \
	  : "${ANTHROPIC_DEFAULT_OPUS_MODEL:?}"; \
	  : "${ANTHROPIC_DEFAULT_SONNET_MODEL:?}"; \
	  : "${ANTHROPIC_DEFAULT_HAIKU_MODEL:?}"; \
	  if ! command -v $(CLAUDE_BIN) >/dev/null 2>&1; then \
	    echo "Claude CLI ('$(CLAUDE_BIN)') not found on PATH."; \
	    exit 1; \
	  fi; \
	  echo "Launching Claude with proxy endpoint $(ANTHROPIC_BASE_URL)..."; \
	  env -u http_proxy -u https_proxy -u all_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
	    NO_PROXY="127.0.0.1,modeldeployment-int.us-ashburn-1.oci.oc-test.com,localhost,::1" \
	    no_proxy="127.0.0.1,modeldeployment-int.us-ashburn-1.oci.oc-test.com,localhost,::1" \
	    ANTHROPIC_BASE_URL="$(ANTHROPIC_BASE_URL)" \
	    ANTHROPIC_API_KEY="$(ANTHROPIC_API_KEY)" \
	    ANTHROPIC_DEFAULT_OPUS_MODEL="$(ANTHROPIC_DEFAULT_OPUS_MODEL)" \
	    ANTHROPIC_DEFAULT_SONNET_MODEL="$(ANTHROPIC_DEFAULT_SONNET_MODEL)" \
	    ANTHROPIC_DEFAULT_HAIKU_MODEL="$(ANTHROPIC_DEFAULT_HAIKU_MODEL)" \
	    $(CLAUDE_BIN)

proxy-and-claude:
	@set -euo pipefail; \
	  $(MAKE) start-proxy; \
	  trap '$(MAKE) stop-proxy' EXIT INT TERM; \
	  $(MAKE) run-claude
