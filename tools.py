import json
from fixtures import FAILURE_LOGS, TEST_HISTORY, RECENT_COMMITS, ENV_STATUS


def get_failure_log(test_name: str) -> dict:
    """Returns the failure log for a specific test."""
    return FAILURE_LOGS.get(test_name, {"error": f"No log found for {test_name}"})


def get_test_history(test_name: str) -> dict:
    """Returns pass/fail history for the last 50 runs of a test."""
    history = TEST_HISTORY.get(test_name, {})
    if history:
        history["flakiness_rate"] = round(history["fails"] / history["runs"], 2)
    return history


def get_recent_commits(file_hint: str) -> list:
    """Returns recent commits touching files related to the hint.

    Args:
        file_hint: A keyword or filename to match against recent commits (e.g. 'Login', 'Payment').
    """
    matches = []
    for filename, commits in RECENT_COMMITS.items():
        if file_hint.lower() in filename.lower():
            matches.extend([{**c, "file": filename} for c in commits])
    return matches


def check_env_status() -> dict:
    """Returns the current status of staging environment components."""
    return ENV_STATUS


# Map tool name -> function for the agent loop
AVAILABLE_TOOLS = {
    "get_failure_log": get_failure_log,
    "get_test_history": get_test_history,
    "get_recent_commits": get_recent_commits,
    "check_env_status": check_env_status,
}


# OpenAI-format schema descriptions for the agent
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_failure_log",
            "description": "Fetch the detailed failure log (error type, message, stack trace) for a specific failed test.",
            "parameters": {
                "type": "object",
                "properties": {
                    "test_name": {"type": "string", "description": "Full test name e.g. 'LoginTest.testInvalidPassword'"}
                },
                "required": ["test_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_test_history",
            "description": "Get pass/fail history for a test over the last 50 runs. Use this to assess flakiness.",
            "parameters": {
                "type": "object",
                "properties": {
                    "test_name": {"type": "string"}
                },
                "required": ["test_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_recent_commits",
            "description": "Find recent commits touching code related to a keyword (e.g. component or feature name). Use this to check if a code change might have caused the failure.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_hint": {"type": "string", "description": "Keyword like 'Login', 'Payment', 'Dashboard'"}
                },
                "required": ["file_hint"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_env_status",
            "description": "Check the current status of staging environment components (db, api, web). Use this when failures look infrastructure-related.",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]