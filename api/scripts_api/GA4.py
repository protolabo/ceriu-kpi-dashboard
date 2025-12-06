import json
import requests
from datetime import date, timedelta

property_Id = "378994390"   #Id du GA4
oauth_File  = "oauth-token.json"

# Charge oauth-token.json
with open(oauth_File, encoding="utf-8") as f:
    oauth = json.load(f)

#on Obtient un access_token
token_url = oauth["token_uri"]
tok = {
    "client_id": oauth["client_id"],
    "client_secret": oauth["client_secret"],
    "refresh_token": oauth["refresh_token"],
    "grant_type": "refresh_token"
}
token_resp = requests.post(token_url, data=tok, timeout=20)
token_resp.raise_for_status()
access_token = token_resp.json()["access_token"]

#On Construit la requête a runReport
time = (date.today() - timedelta(days=1)).isoformat()
body = {
    "dateRanges": [{"startDate": time, "endDate": time}],
    "metrics": [{"name": "activeUsers"}],
    "limit": 1
}
url = "https://analyticsdata.googleapis.com/v1beta/properties/" + property_Id + ":runReport"
headers = {
    "Authorization": "Bearer " + access_token,
    "Content-Type": "application/json",
    "Accept": "application/json"
}

#On appel et on lis la réponse
resp = requests.post(url, headers=headers, json=body, timeout=30)
if resp.status_code == 200:
    data = resp.json()
    rows = data.get("rows", [])
    if rows:
        metric_values = rows[0].get("metricValues", [])
        if metric_values:
            value = metric_values[0].get("value")
            print("activeUsers hier = " + str(value))
        else:
            print("pas de metricValues")
    else:
        print("pas de rows")
else:
    print("FAIL" + str(resp.status_code) + " " + resp.text[:300])
