import argparse
import json
import os
import re
import sys
from datetime import date
from openai import BadRequestError
from fixtures import FAILURE_LOGS
from providers import get_client
from tools import AVAILABLE_TOOLS, TOOL_SCHEMAS

sys.stdout.reconfigure(encoding="utf-8")


SYSTEM_PROMPT = """You are a senior QA engineer triaging test failures.

For each failure, you must:
1. Fetch the failure log to understand the error.
2. Check the test's history to assess flakiness.
3. Check recent commits if it looks code-related.
4. Check environment status if it looks infra-related.
5. Decide a verdict from: FLAKY, REAL_BUG, ENVIRONMENT, TEST_DATA, RECENT_CODE_CHANGE.

End your response with a JSON block in this format:
```json
{
  "verdict": "REAL_BUG",
  "confidence": "high",
  "reasoning": "One-paragraph explanation",
  "suggested_action": "Specific next step"
}
```
"""


def triage_failure(test_name: str, provider: str = "groq"):
    client, model = get_client(provider)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Triage this failed test: {test_name}"}
    ]

    print(f"\n🔍 Analyzing failure: {test_name}\n")

    while True:
        for attempt in range(3):
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    tools=TOOL_SCHEMAS,
                )
                break
            except BadRequestError:
                if attempt == 2:
                    raise
                print(f"  ⚠ Tool call malformed, retrying ({attempt + 1}/3)…")

        msg = response.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:
            print("═" * 60)
            print(msg.content)
            print("═" * 60)
            return msg.content

        for tool_call in msg.tool_calls:
            fn_name = tool_call.function.name
            fn_args = json.loads(tool_call.function.arguments) or {}
            print(f"🔧 {fn_name}({fn_args})")

            result = AVAILABLE_TOOLS[fn_name](**fn_args)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })


def _extract_verdict(content: str) -> dict:
    m = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
    if not m:
        return {}
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return {}


def _write_report(results: list, path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    lines = [
        f"# Test Triage Report — {date.today()}",
        "",
        "| Test | Verdict | Confidence | Suggested Action |",
        "|------|---------|------------|------------------|",
    ]
    for test_name, content in results:
        v = _extract_verdict(content)
        lines.append(
            f"| `{test_name}` | {v.get('verdict', '—')} "
            f"| {v.get('confidence', '—')} "
            f"| {v.get('suggested_action', '—')} |"
        )
    lines += ["", "---", ""]
    for test_name, content in results:
        v = _extract_verdict(content)
        lines += [f"## {test_name}", ""]
        if v:
            lines += [
                f"**Verdict:** {v.get('verdict', '—')}  ",
                f"**Confidence:** {v.get('confidence', '—')}  ",
                "",
                f"**Reasoning:** {v.get('reasoning', '—')}",
                "",
                f"**Suggested Action:** {v.get('suggested_action', '—')}",
            ]
        else:
            lines.append(content)
        lines += ["", "---", ""]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", type=str, help="Triage a single test by name")
    parser.add_argument("--all", action="store_true", help="Triage all fixture tests")
    parser.add_argument("--provider", default="groq", choices=["groq", "github", "gemini"])
    parser.add_argument("--save-report", action="store_true")
    args = parser.parse_args()

    if args.all:
        tests_to_run = list(FAILURE_LOGS.keys())   # all 5
    elif args.test:
        tests_to_run = [args.test]                  # just this one
    else:
        parser.error("Provide either --test <name> or --all")

    results = []
    for test in tests_to_run:
        content = triage_failure(test, provider=args.provider)
        results.append((test, content))
        print()

    if args.save_report:
        report_path = f"reports/triage-{date.today()}.md"
        _write_report(results, report_path)
        print(f"📄 Report saved to: {report_path}")