"""API Client for Alpha Smart Cloud."""

import json
import logging
from typing import Any

import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials
from pycognito import Cognito
import requests

_LOGGER = logging.getLogger(__name__)


class AlphaSmartCloudAPI:
    """API client for Alpha Smart Cloud using AWS Cognito authentication."""

    def __init__(
        self,
        region: str,
        user_pool_id: str,
        client_id: str,
        identity_pool_id: str,
        api_id: str,
        stage: str = "prod",
    ) -> None:
        """Initialize the API client."""
        self.region = region
        self.user_pool_id = user_pool_id
        self.client_id = client_id
        self.identity_pool_id = identity_pool_id
        self.api_id = api_id
        self.stage = stage
        self.base_url = f"https://{api_id}.execute-api.{region}.amazonaws.com/{stage}"

        self._cognito_user: Cognito | None = None
        self._aws_credentials: Credentials | None = None
        self._identity_id: str | None = None

    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate with Cognito User Pool and get AWS credentials."""
        try:
            # Step 1: Authenticate with Cognito User Pool
            self._cognito_user = Cognito(
                user_pool_id=self.user_pool_id,
                client_id=self.client_id,
                username=username,
            )
            self._cognito_user.authenticate(password=password)

            # Step 2: Get AWS credentials from Cognito Identity Pool
            cognito_identity = boto3.client(
                "cognito-identity",
                region_name=self.region,
            )

            logins = {
                f"cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}": self._cognito_user.id_token
            }

            identity = cognito_identity.get_id(
                IdentityPoolId=self.identity_pool_id,
                Logins=logins,
            )
            self._identity_id = identity["IdentityId"]

            creds = cognito_identity.get_credentials_for_identity(
                IdentityId=self._identity_id,
                Logins=logins,
            )["Credentials"]

            self._aws_credentials = Credentials(
                access_key=creds["AccessKeyId"],
                secret_key=creds["SecretKey"],
                token=creds["SessionToken"],
            )
        except Exception:
            _LOGGER.exception("Authentication failed")
            return False
        else:
            return True

    def _make_signed_request(
        self,
        method: str,
        endpoint: str,
        headers: dict[str, str] | None = None,
        data: dict[str, Any] | None = None,
    ) -> requests.Response:
        """Make a signed AWS SigV4 request to the API."""
        if not self._aws_credentials:
            raise ValueError("Not authenticated. Call authenticate() first.")

        url = f"{self.base_url}{endpoint}"

        request_headers = {"Accept": "application/json"}
        if headers:
            request_headers.update(headers)

        body = None
        if data is not None:
            body = json.dumps(data, separators=(",", ":"))
            request_headers["Content-Type"] = "application/json"

        req = AWSRequest(
            method=method.upper(),
            url=url,
            headers=request_headers,
            data=body,
        )

        SigV4Auth(self._aws_credentials, "execute-api", self.region).add_auth(req)
        prepared = req.prepare()

        response = requests.request(
            method=method.upper(),
            url=url,
            headers=prepared.headers,
            data=body,
            timeout=10,
        )

        response.raise_for_status()
        return response

    def get_homes(self) -> list[dict[str, Any]]:
        """Get list of homes."""
        response = self._make_signed_request("GET", "/v1/homes")
        return response.json()

    def get_devices(self) -> list[dict[str, Any]]:
        """Get list of devices."""
        response = self._make_signed_request("GET", "/v1/devices")
        return response.json()

    def get_device_values(self, device_id: str) -> dict[str, Any]:
        """Get device values by device ID."""
        response = self._make_signed_request("GET", f"/v1/devices/{device_id}/values")
        return response.json()

    def set_device_value(self, device_id: str, element_id: str, value: Any) -> bool:
        """Set device value by device ID and element ID."""
        data = {element_id: value}
        response = self._make_signed_request(
            "PUT", f"/v1/devices/{device_id}/values", data=data
        )
        response.raise_for_status()
        return True

    def get_device_template(self, device_id: str) -> dict[str, Any]:
        """Get device template by device ID."""
        response = self._make_signed_request("GET", f"/v1/devices/{device_id}/template")
        return response.json()

    def get_device_with_template(self, device_id: str) -> dict[str, Any]:
        """Get device values enriched with human-readable information from template."""
        values = self.get_device_values(device_id)
        template = self.get_device_template(device_id)

        # Build a lookup map from element ID to element metadata
        element_map = {}
        for shadow in template.get("shadows", []):
            shadow_name = shadow.get("name")
            shadow_category = shadow.get("category")
            for element in shadow.get("elements", []):
                element_id = element.get("id")
                element_map[element_id] = {
                    "shadow": shadow_name,
                    "shadowCategory": shadow_category,
                    "category": element.get("content", {}).get("category"),
                    "properties": element.get("content", {}).get("properties", {}),
                    "writable": element.get("writable", False),
                    "userWritable": element.get("userWritable"),
                    "disabled": element.get("disabled"),
                    "installationOnly": element.get("installationOnly"),
                }

        # Enrich values with template metadata
        enriched_values = []
        for key, value in values.items():
            metadata = element_map.get(key, {})
            enriched_values.append(
                {
                    "id": key,
                    "value": value,
                    "category": metadata.get("category", "unknown"),
                    "shadow": metadata.get("shadow", "unknown"),
                    "writable": metadata.get("writable", False),
                    "userWritable": metadata.get("userWritable"),
                    "properties": metadata.get("properties", {}),
                }
            )

        device_type = template.get("type")
        if device_type == "rbg":
            device_type = "Raumbediengerät"

        return {
            "deviceId": device_id,
            "deviceInfo": {
                "oem": template.get("oem"),
                "type": device_type,
                "description": template.get("description"),
                "gtin": template.get("gtin"),
            },
            "properties": enriched_values,
            "rawTemplate": template,
        }
