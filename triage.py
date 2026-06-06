import json
import sys
from openai import BadRequestError
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
            except BadRequestError as e:
                if attempt == 2:
                    raise
                print(f"  ⚠ Tool call malformed, retrying ({attempt + 1}/3)…")
        else:
            break

        msg = response.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:
            print("═" * 60)
            print(msg.content)
            print("═" * 60)
            break

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


if __name__ == "__main__":
    # Try all three failures
    for test in ["LoginTest.testInvalidPassword", "PaymentTest.testRefund", "DashboardTest.testKpiLoad"]:
        triage_failure(test, provider="groq")
        print("\n")