# Credentials Guide: x-remote-control

This skill controls X (Twitter) accounts using browser automation via CDP.

## Required Credentials

| ID | Type | Description | Required |
|----|------|-------------|----------|
| `X_CDP_URL` | url | The WebSocket URL for the Chrome DevTools Protocol. | **Yes** |
| `X_SESSION_COOKIE` | secret | The `auth_token` cookie for X. | No |

## Setup Instructions

### 1. CDP Endpoint
This skill depends on `chrome-remote-browser-control`. You must provide a valid CDP URL from a running Chrome instance:
`export X_CDP_URL=ws://localhost:9222/devtools/browser/...`

### 2. Authentication
The browser instance should ideally be already logged into X. If not, you can provide the `auth_token` cookie:
1. Log in to X in your browser.
2. Open DevTools -> Application -> Cookies.
3. Copy the value of the `auth_token` cookie.
4. Provide it via environment variable: `export X_SESSION_COOKIE=your_token_here`.
