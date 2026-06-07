# TestTriage 🔍

An AI agent that triages failed software tests and tells you whether each failure is:

- 🔁 **Flaky** — rerun and move on
- 🐛 **Real bug** — file a Jira ticket
- 🌍 **Environment** — check infra
- 📊 **Test data** — refresh fixtures
- 🔧 **Recent code change** — look at the last commit

Built as a learning project to explore AI agents before the
[5-Day AI Agents Intensive course](https://www.kaggle.com/competitions/5-day-ai-agents-intensive-vibecoding-course-with-google)
by Google × Kaggle.

## How it works

The agent receives a failed test name, then autonomously decides which tools to call:

\`\`\`
                    USER
                     │
                     ▼
              [Triage Agent]
                     │
       ┌─────────────┼─────────────┬──────────────┐
       ▼             ▼             ▼              ▼
get_failure_log  get_test_      get_recent    check_env
                 history        commits       status
\`\`\`

You never write `if-this-then-that` logic. The agent reasons through the tools
and produces a structured verdict with reasoning.

## Multi-provider support

Works with any OpenAI-compatible API. Currently supports:

| Provider | Default model | Notes |
|---|---|---|
| Groq | `llama-3.3-70b-versatile` | Free, ultra-fast |
| Gemini | `gemini-2.5-flash` | Free tier |
| GitHub Models | `openai/gpt-4.1` | Free, uses your GitHub PAT |

## Setup

\`\`\`bash
git clone https://github.com/iamniket/TestTriage.git
cd TestTriage
pip install -r requirements.txt
cp .env.example .env
# Add your API keys to .env
\`\`\`

## Usage

\`\`\`bash
# Triage one test
python triage.py --test LoginTest.testInvalidPassword

# Triage all 5 fixture tests
python triage.py --all

# Use a different provider
python triage.py --all --provider gemini

# Save a markdown report
python triage.py --all --save-report
\`\`\`

## Sample output

\`\`\`
🔍 Analyzing failure: LoginTest.testInvalidPassword

🔧 get_failure_log({'test_name': 'LoginTest.testInvalidPassword'})
🔧 get_test_history({'test_name': 'LoginTest.testInvalidPassword'})
🔧 get_recent_commits({'file_hint': 'Login'})

═══════════════════════════════════════════════════════
  VERDICT: 🔧 RECENT_CODE_CHANGE (high confidence)
═══════════════════════════════════════════════════════
This test has passed 47/50 times historically, so it's not flaky.
A recent commit modified LoginController.java's error response
format. The test expects "Invalid credentials" but the new code
returns "Authentication failed."

Suggested action: Update the test's expected message OR push back
on the API change.
\`\`\`

## Project status

This is a learning project, not a production tool. Current limitations:

- Uses fake fixture data (no real Jenkins/GitHub/Jira integration yet)
- Verdict accuracy depends on the LLM provider — see /reports for samples
- Single-agent design (multi-agent v2 planned post-Kaggle course)

## What's next

- [ ] Real Jenkins API integration
- [ ] Real GitHub commits via API
- [ ] Jira ticket auto-creation for REAL_BUG verdicts
- [ ] Web UI
- [ ] Multi-agent orchestration

## License

MIT
