"""Runtime wiring for the Falco event-ingestion service."""

import os

import httpx

from ingestion.api import create_app


class HttpRemediationClient:
    """Call the guarded remediation API over the cluster-internal service DNS name."""

    def __init__(self, endpoint: str, client: httpx.Client | None = None) -> None:
        self._endpoint = endpoint
        self._client = client or httpx.Client(timeout=15.0)

    def handle(
        self, event: dict[str, object], features: dict[str, float]
    ) -> dict[str, object]:
        response = self._client.post(self._endpoint, json={"event": event, "features": features})
        response.raise_for_status()
        return response.json()


def create_runtime_app(remediation_url: str | None = None):
    return create_app(
        HttpRemediationClient(
            remediation_url
            or os.getenv(
                "AUTOGUARD_REMEDIATION_URL",
                "http://autoguard-remediation:8000/events",
            )
        )
    )


app = create_runtime_app()
