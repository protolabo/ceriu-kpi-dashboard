import requests
from datetime import date, timedelta
from typing import Dict, Any
from app.models.ga4_model import GA4QueryParams
from app.services.oauth_service import OAuthService


class GA4Service:
    BASE_URL = "https://analyticsdata.googleapis.com/v1beta"

    def __init__(self, oauth_service: OAuthService):
        self.oauth_service = oauth_service

    def run_report(self, params: GA4QueryParams) -> Dict[str, Any]:
        """Execute GA4 runReport API call"""
        # Set default dates if not provided
        start_date = params.start_date or (date.today() - timedelta(days=1))
        end_date = params.end_date or (date.today() - timedelta(days=1))

        # Build request body
        body = {
            "dateRanges": [{
                "startDate": start_date.isoformat(),
                "endDate": end_date.isoformat()
            }],
            "metrics": [{"name": metric} for metric in params.metrics],
            "limit": params.limit
        }

        # Add dimensions if provided
        if params.dimensions:
            body["dimensions"] = [{"name": dim} for dim in params.dimensions]

        # Make API request
        url = f"{self.BASE_URL}/properties/{params.property_id}:runReport"
        headers = {
            "Authorization": f"Bearer {self.oauth_service.get_access_token()}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        try:
            response = requests.post(url, headers=headers, json=body, timeout=30)
            response.raise_for_status()
            return self._parse_response(response.json())
        except requests.RequestException as e:
            raise ValueError(f"GA4 API request failed: {str(e)}")

    def _parse_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse GA4 response into a cleaner format"""
        rows = data.get("rows", [])
        parsed_data = []

        for row in rows:
            row_data = {}
            
            # Extract dimensions
            if "dimensionValues" in row:
                row_data["dimensions"] = [
                    dim.get("value") for dim in row["dimensionValues"]
                ]
            
            # Extract metrics
            if "metricValues" in row:
                row_data["metrics"] = [
                    metric.get("value") for metric in row["metricValues"]
                ]
            
            parsed_data.append(row_data)

        return {
            "rows": parsed_data,
            "row_count": len(parsed_data),
            "metadata": data.get("metadata", {})
        }