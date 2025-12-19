import requests
from datetime import date, timedelta
from typing import Dict, Any, List

from app.models.ga4_model import GA4QueryParams
from app.services.oauth_service import OAuthService


class GA4Service:
    BASE_URL = "https://analyticsdata.googleapis.com/v1beta"

    def __init__(self, oauth_service: OAuthService):
        self.oauth_service = oauth_service

    def run_report(self, params: GA4QueryParams) -> Dict[str, Any]:
        """
        Execute GA4 runReport API call avec pagination (offset).

        - params.limit est interprété comme TAILLE DE PAGE (par ex. 10000),
          pas comme limite totale.
        - Si params.event_name est renseigné (optionnel), on ajoute un
          dimensionFilter GA4 sur eventName = event_name.
        """
        # Dates par défaut si non fournies
        start_date = params.start_date or (date.today() - timedelta(days=1))
        end_date = params.end_date or (date.today() - timedelta(days=1))

        # Body de base sans limit/offset
        base_body: Dict[str, Any] = {
            "dateRanges": [{
                "startDate": start_date.isoformat(),
                "endDate": end_date.isoformat()
            }],
            "metrics": [{"name": metric} for metric in params.metrics],
        }

        # Dimensions
        if params.dimensions:
            base_body["dimensions"] = [{"name": dim} for dim in params.dimensions]

        # Filtre optionnel sur eventName
        event_name = getattr(params, "event_name", None)
        if event_name:
            base_body["dimensionFilter"] = {
                "filter": {
                    "fieldName": "eventName",
                    "stringFilter": {
                        "matchType": "EXACT",
                        "value": event_name,
                        "caseSensitive": False,
                    },
                }
            }

        url = f"{self.BASE_URL}/properties/{params.property_id}:runReport"
        headers = {
            "Authorization": f"Bearer {self.oauth_service.get_access_token()}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        all_rows: List[Dict[str, Any]] = []
        dimension_headers: List[str] = []
        metric_headers: List[str] = []

        offset = 0
        # limit = taille d'une page
        page_limit = params.limit or 10000

        try:
            while True:
                
                body: Dict[str, Any] = dict(base_body)
                body["limit"] = page_limit
                body["offset"] = offset

                response = requests.post(
                    url,
                    headers=headers,
                    json=body,
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()

                parsed_page = self._parse_response(data)

                # Headers d'après la première page
                if not dimension_headers:
                    dimension_headers = parsed_page.get("dimension_headers", [])
                if not metric_headers:
                    metric_headers = parsed_page.get("metric_headers", [])

                page_rows = parsed_page.get("rows", [])
                all_rows.extend(page_rows)

                # Nombre total de lignes côté GA4
                total_row_count = data.get("rowCount", len(all_rows))

                # Avancer l'offset
                offset += len(page_rows)

                # plus de lignes dans cette page ou on a lu toutes les lignes d'après rowCount
                if not page_rows:
                    break
                if offset >= total_row_count:
                    break

            return {
                "rows": all_rows,
                "row_count": len(all_rows),
                "dimension_headers": dimension_headers,
                "metric_headers": metric_headers,
            }

        except requests.RequestException as e:
            raise ValueError(f"GA4 API request failed: {str(e)}")

    def _parse_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse la réponse GA4 brute en un format plus simple :
        - rows : liste de dict {dimension: valeur, metric: valeur}
        - row_count : nombre de lignes dans CETTE page
        - dimension_headers / metric_headers : liste des noms
        """
        dimension_headers = [d["name"] for d in data.get("dimensionHeaders", [])]
        metric_headers = [m["name"] for m in data.get("metricHeaders", [])]

        parsed_rows: List[Dict[str, Any]] = []

        for row in data.get("rows", []):
            row_dict: Dict[str, Any] = {}

            # Dimensions nommées
            dim_values = [dv.get("value") for dv in row.get("dimensionValues", [])]
            for name, value in zip(dimension_headers, dim_values):
                row_dict[name] = value

            # Métriques nommées
            met_values = [mv.get("value") for mv in row.get("metricValues", [])]
            for name, value in zip(metric_headers, met_values):
                row_dict[name] = self._convert_value(value)

            parsed_rows.append(row_dict)

        return {
            "rows": parsed_rows,
            "row_count": len(parsed_rows),
            "dimension_headers": dimension_headers,
            "metric_headers": metric_headers,
        }

    @staticmethod
    def _convert_value(value: Any) -> Any:
        """Convertit les valeurs de chaîne en int ou float si possible."""
        if not isinstance(value, str):
            return value

        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            return value