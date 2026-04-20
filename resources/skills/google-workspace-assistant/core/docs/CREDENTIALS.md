# Credentials Guide: google-workspace-assistant

This skill requires access to the Google Workspace API. You need to provide OAuth 2.0 credentials.

## Required Credentials

| ID | Type | Description | Required |
|----|------|-------------|----------|
| `GOOGLE_OAUTH_CREDENTIALS` | path | Path to `credentials.json` (Desktop app type). | **Yes** |
| `GOOGLE_TOKEN_PATH` | path | Path to `token.json` (stored user session). | **Yes** |

## Setup Instructions

### 1. Obtain `credentials.json`
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project.
3. Enable the APIs: Gmail API, Google Calendar API, and Google Drive API.
4. Go to **Credentials** -> **Create Credentials** -> **OAuth client ID**.
5. Select **Desktop App** as the application type.
6. Download the JSON file and rename it to `credentials.json`.

### 2. Configuration
Place the file in your runtime configuration folder:
`runtime/{{context}}/{{env}}/google-workspace-assistant/config/credentials.json`

Set the environment variable or update your local config:
`export GOOGLE_OAUTH_CREDENTIALS=runtime/{{context}}/{{env}}/google-workspace-assistant/config/credentials.json`

### 3. Generate `token.json`
The first time you run the skill, it will open a browser window to authorize access. After completion, a `token.json` file will be created at the `GOOGLE_TOKEN_PATH`.
