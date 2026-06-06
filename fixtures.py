"""Fake data for development. Replace with real Jenkins/Jira/GitHub calls later."""

FAILURE_LOGS = {
    "LoginTest.testInvalidPassword": {
        "test_name": "LoginTest.testInvalidPassword",
        "error_type": "AssertionError",
        "message": "Expected 'Invalid credentials' but got 'Authentication failed'",
        "stack_trace_summary": "at LoginTest.java:42",
        "duration_ms": 1200,
        "timestamp": "2026-06-06T02:14:33Z"
    },
    "PaymentTest.testRefund": {
        "test_name": "PaymentTest.testRefund",
        "error_type": "TimeoutException",
        "message": "Element not found within 30s: #refund-success-banner",
        "stack_trace_summary": "at PaymentTest.java:88",
        "duration_ms": 30000,
        "timestamp": "2026-06-06T02:18:12Z"
    },
    "DashboardTest.testKpiLoad": {
        "test_name": "DashboardTest.testKpiLoad",
        "error_type": "ConnectionRefusedError",
        "message": "Could not connect to staging-db.internal:5432",
        "stack_trace_summary": "at DashboardTest.java:15",
        "duration_ms": 5000,
        "timestamp": "2026-06-06T02:22:01Z"
    }
}

TEST_HISTORY = {
    "LoginTest.testInvalidPassword": {"runs": 50, "passes": 47, "fails": 3, "last_failures": ["2026-06-06", "2026-06-06", "2026-05-30"]},
    "PaymentTest.testRefund":        {"runs": 50, "passes": 28, "fails": 22, "last_failures": ["2026-06-06", "2026-06-05", "2026-06-04", "2026-06-03"]},
    "DashboardTest.testKpiLoad":     {"runs": 50, "passes": 49, "fails": 1, "last_failures": ["2026-06-06"]}
}

RECENT_COMMITS = {
    "LoginController.java": [
        {"sha": "a4f8c12", "author": "Gigi", "message": "Standardize auth error messages", "hours_ago": 2}
    ],
    "PaymentService.java": [],
    "DashboardController.java": []
}

ENV_STATUS = {
    "staging-db": "DOWN since 2026-06-06T02:00:00Z",
    "staging-api": "UP",
    "staging-web": "UP"
}