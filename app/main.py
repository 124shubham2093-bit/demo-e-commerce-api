import os
import traceback

import requests
from fastapi import FastAPI

app = FastAPI(title="Demo E-Commerce API")


INTELLIINCIDENT_URL = os.getenv(
    "INTELLIINCIDENT_URL",
    "http://127.0.0.1:8000",
)

INTELLIINCIDENT_API_KEY = os.getenv(
    "INTELLIINCIDENT_API_KEY",
)


def send_incident_telemetry(exc: Exception) -> None:
    """Send a runtime exception to IntelliIncident."""

    if not INTELLIINCIDENT_API_KEY:
        print("IntelliIncident API key is not configured.")
        return

    payload = {
        "title": "Runtime Exception: Inventory Service Failure",
        "service": "Demo E-Commerce API",
        "summary": str(exc),
        "status": "OPEN",
        "error_type": type(exc).__name__,
        "error_message": str(exc),
        "stack_trace": traceback.format_exc(),
        "metrics": {
            "error_rate": 18.5,
            "latency_p99": 850.0,
            "latency_p50": 65.0,
            "affected_users": 1420,
            "request_volume": 4200,
            "deployment_recency_minutes": 25,
            "cpu_utilization": 78.0,
            "memory_utilization": 82.0,
            "service_criticality": 4,
        },
    }

    try:
        response = requests.post(
            f"{INTELLIINCIDENT_URL}/api/incidents",
            json=payload,
            headers={
                "X-API-Key": INTELLIINCIDENT_API_KEY,
                "Content-Type": "application/json",
            },
            timeout=10,
        )

        print(
            f"IntelliIncident telemetry response: "
            f"{response.status_code} {response.text}"
        )

    except requests.RequestException as telemetry_error:
        print(
            "Failed to send telemetry to IntelliIncident:",
            telemetry_error,
        )


@app.get("/")
def home():
    return {
        "service": "Demo E-Commerce API",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/api/products")
def products():
    return {
        "products": [
            {"id": 1, "name": "Laptop", "price": 65000},
            {"id": 2, "name": "Keyboard", "price": 2500},
            {"id": 3, "name": "Mouse", "price": 1200},
        ]
    }


@app.get("/api/demo-error")
def demo_error():
    try:
        inventory = None

        # Deliberate runtime failure for the IntelliIncident demonstration.
        return inventory["available_stock"]

    except Exception as exc:
        send_incident_telemetry(exc)
        raise