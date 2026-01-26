"""API Client for Alpha Smart Cloud."""

import json
from datetime import datetime, timedelta, timezone
from typing import Any

import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials
from botocore.exceptions import BotoCoreError, ClientError
from pycognito import Cognito
import pycognito.exceptions as cognito_exceptions
import requests

_AUTH_EXCEPTIONS = tuple(
    exc
    for exc in (
        getattr(cognito_exceptions, "NotAuthorizedException", None),
        getattr(cognito_exceptions, "UserNotFoundException", None),
        getattr(cognito_exceptions, "UserNotConfirmedException", None),
        getattr(cognito_exceptions, "PasswordResetRequiredException", None),
    )
    if isinstance(exc, type)
)


class AlphaSmartCloudAuthError(Exception):
    """Error to indicate invalid authentication."""


class AlphaSmartCloudConnectionError(Exception):
    """Error to indicate connection or service failure."""


class AlphaSmartCloudMissingCredentialsError(AlphaSmartCloudAuthError):
    """Error to indicate stored credentials are missing."""


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
        self._aws_credentials_expiration: datetime | None = None
        self._identity_id: str | None = None
        self._username: str | None = None
        self._password: str | None = None

    def authenticate(self, username: str, password: str) -> None:
        """Authenticate with Cognito User Pool and get AWS credentials."""
        self._username = username
        self._password = password
        self._authenticate_cognito()
        self._update_identity_credentials()

    def _authenticate_cognito(self) -> None:
        """Authenticate with Cognito User Pool and set tokens."""
        if not self._username or not self._password:
            raise AlphaSmartCloudMissingCredentialsError("Missing username or password")

        try:
            self._cognito_user = Cognito(
                user_pool_id=self.user_pool_id,
                client_id=self.client_id,
                username=self._username,
            )
            self._cognito_user.authenticate(password=self._password)
        except ClientError as err:
            error_code = err.response.get("Error", {}).get("Code")
            if error_code in {
                "NotAuthorizedException",
                "UserNotFoundException",
                "UserNotConfirmedException",
                "PasswordResetRequiredException",
            }:
                raise AlphaSmartCloudAuthError from err
            raise AlphaSmartCloudConnectionError from err
        except _AUTH_EXCEPTIONS as err:
            raise AlphaSmartCloudAuthError from err
        except BotoCoreError as err:
            raise AlphaSmartCloudConnectionError from err
        except Exception as err:
            raise AlphaSmartCloudConnectionError from err

    def _refresh_cognito_session(self) -> None:
        """Refresh the Cognito user session, or reauthenticate if needed."""
        if not self._cognito_user:
            self._authenticate_cognito()
            return

        refresh = getattr(self._cognito_user, "refresh_session", None)
        if callable(refresh):
            try:
                refresh()
                return
            except ClientError as err:
                error_code = err.response.get("Error", {}).get("Code")
                if error_code in {
                    "NotAuthorizedException",
                    "UserNotFoundException",
                    "UserNotConfirmedException",
                    "PasswordResetRequiredException",
                }:
                    raise AlphaSmartCloudAuthError from err
                raise AlphaSmartCloudConnectionError from err
            except _AUTH_EXCEPTIONS as err:
                raise AlphaSmartCloudAuthError from err
            except BotoCoreError as err:
                raise AlphaSmartCloudConnectionError from err
            except Exception as err:
                raise AlphaSmartCloudConnectionError from err

        renew = getattr(self._cognito_user, "renew_session", None)
        if callable(renew):
            try:
                renew()
                return
            except ClientError as err:
                error_code = err.response.get("Error", {}).get("Code")
                if error_code in {
                    "NotAuthorizedException",
                    "UserNotFoundException",
                    "UserNotConfirmedException",
                    "PasswordResetRequiredException",
                }:
                    raise AlphaSmartCloudAuthError from err
                raise AlphaSmartCloudConnectionError from err
            except _AUTH_EXCEPTIONS as err:
                raise AlphaSmartCloudAuthError from err
            except BotoCoreError as err:
                raise AlphaSmartCloudConnectionError from err
            except Exception as err:
                raise AlphaSmartCloudConnectionError from err

        self._authenticate_cognito()

    def _update_identity_credentials(self) -> None:
        """Fetch AWS credentials using Cognito Identity Pool."""
        if not self._cognito_user:
            raise AlphaSmartCloudMissingCredentialsError("Not authenticated")

        try:
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
        except ClientError as err:
            error_code = err.response.get("Error", {}).get("Code")
            if error_code == "NotAuthorizedException":
                raise AlphaSmartCloudAuthError from err
            raise AlphaSmartCloudConnectionError from err
        except BotoCoreError as err:
            raise AlphaSmartCloudConnectionError from err

        self._aws_credentials = Credentials(
            access_key=creds["AccessKeyId"],
            secret_key=creds["SecretKey"],
            token=creds["SessionToken"],
        )
        expiration = creds.get("Expiration")
        if isinstance(expiration, datetime):
            if expiration.tzinfo is None:
                expiration = expiration.replace(tzinfo=timezone.utc)
            self._aws_credentials_expiration = expiration
        elif isinstance(expiration, str):
            try:
                parsed = datetime.fromisoformat(expiration)
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                self._aws_credentials_expiration = parsed
            except ValueError:
                self._aws_credentials_expiration = None
        else:
            self._aws_credentials_expiration = None

    def _credentials_expiring(self) -> bool:
        if not self._aws_credentials_expiration:
            return True
        now = datetime.now(timezone.utc)
        return now >= self._aws_credentials_expiration - timedelta(minutes=5)

    def _ensure_valid_credentials(self) -> None:
        """Refresh AWS credentials if missing or expiring."""
        if self._aws_credentials and not self._credentials_expiring():
            return

        try:
            self._update_identity_credentials()
            return
        except AlphaSmartCloudAuthError:
            self._refresh_cognito_session()
            self._update_identity_credentials()
        except AlphaSmartCloudMissingCredentialsError:
            self._authenticate_cognito()
            self._update_identity_credentials()

    def _make_signed_request(
        self,
        method: str,
        endpoint: str,
        headers: dict[str, str] | None = None,
        data: dict[str, Any] | None = None,
    ) -> requests.Response:
        """Make a signed AWS SigV4 request to the API."""
        self._ensure_valid_credentials()
        if not self._aws_credentials:
            raise AlphaSmartCloudAuthError("Not authenticated")

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
