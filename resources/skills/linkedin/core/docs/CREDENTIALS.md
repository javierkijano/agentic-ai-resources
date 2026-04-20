# Credentials Guide: linkedin

This skill manages LinkedIn interactions. It primarily uses a local memory system but may require session credentials for automation.

## Required Credentials

| ID | Type | Description | Required |
|----|------|-------------|----------|
| `LINKEDIN_SESSION_COOKIE` | secret | The `li_at` session cookie for automated browser actions. | No |
| `LINKEDIN_PROFILE_ID` | string | Default profile name (e.g., `default`). | No |

## Setup Instructions

### 1. Automated Actions (Browser)
If the skill is used with a browser automation tool, you might need to provide the session cookie:
1. Log in to LinkedIn in your browser.
2. Open DevTools -> Application -> Cookies.
3. Copy the value of the `li_at` cookie.
4. Provide it via environment variable: `export LINKEDIN_SESSION_COOKIE=your_cookie_here`.

### 2. Local Memory
The skill maintains a `memory.json` file in the runtime directory. No credentials are required to initialize the memory system, but you must specify a profile name.
