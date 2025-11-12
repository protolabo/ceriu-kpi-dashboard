from pathlib import Path
import requests

#on Lit la clé API depuis un fichier texte
api_key_path = Path("cléMailchimp.txt")
api_key = api_key_path.read_text(encoding="utf-8").strip()

#on Construit l'URL d'API à partir du data center
data_center = api_key.split("-")[-1]
base_url = "https://" + data_center + ".api.mailchimp.com/3.0/"
auth = ("", api_key)

#on appel /lists pour récupérer les audiences
params = {
    "count": 1000,
    "fields": "lists.name,lists.stats.member_count"
}
response = requests.get(base_url + "lists", params=params, auth=auth, timeout=30)
response.raise_for_status()

#on additionne member_count pour avoir le total
data = response.json()
audience_list = data.get("lists", [])
subscriber_total = 0
for audience in audience_list:
    stats = audience.get("stats", {})
    subscriber_total += stats.get("member_count", 0)

#On affiche le total et le nombre de subscriber par audience
print("Total abonnés : " + str(subscriber_total))
for audience in audience_list:
    name = audience.get("name", "")
    count = audience.get("stats", {}).get("member_count", 0)
    print(name + " : " + str(count))