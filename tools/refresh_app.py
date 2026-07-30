"""
Petite app permettant de rafraichir les tables qui provoquent un timeout Power Query
dans Power BI (Mailchimp click reports, Facebook posts + insights, LinkedIn posts + stats).

Dependance supplementaire : pip install msal

Les cles/token Mailchimp/Facebook/LinkedIn sont redemandes a chaque lancement (rien
n'est sauvegarde sur disque).
"""

import csv
import io
import queue
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

import requests
import msal

API_BASE_URL = "https://canal-api.onrender.com/api/v1"
REQUEST_TIMEOUT = 180
LINKEDIN_REQUEST_TIMEOUT = 600  # plus long : jusqu'a plusieurs milliers de posts

# Authentification Microsoft (Graph)
CLIENT_ID = "14d82eec-204b-4c2f-b7e8-296a70dab67e"
AUTHORITY = "https://login.microsoftonline.com/common"


GRAPH_SCOPES = ["Files.ReadWrite.All"]
# remettre lorsquon livre avec un compte ayant acces au sharepoint du CERIU :
# GRAPH_SCOPES = ["Files.ReadWrite.All", "Sites.ReadWrite.All"]

# Destination des CSV

DEFAULT_SITE_PATH = "ceriu.sharepoint.com:/sites/PartageCeriu"
DEFAULT_FOLDER_PATH = "Communications/Tableau de Bord KPI"

# Autres valeurs par defaut, pre-remplies dans l'app mais modifiables
DEFAULT_FACEBOOK_PAGE_ID = "631772673852970"
DEFAULT_LINKEDIN_ORG_URN = "urn:li:organization:11042657"


def get_graph_token() -> str:
    """Ouvre une fenetre de connexion Microsoft standard et retourne un token Graph.
    timeout : si la connexion n'est pas terminee dans ce delai (ex: onglet ferme
    sans se connecter), leve une erreur plutot que d'attendre indefiniment."""
    app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY)
    result = app.acquire_token_interactive(scopes=GRAPH_SCOPES, timeout=120)
    if result is None:
        raise RuntimeError("Connexion Microsoft annulee ou expiree (delai de 120s depasse).")
    if "access_token" not in result:
        raise RuntimeError(f"Connexion Microsoft echouee : {result.get('error_description', result)}")
    return result["access_token"]


def resolve_upload_base(token: str, site_path: str, folder_path: str) -> str:
    """Construit l'URL Graph du dossier cible, en utilisant les acces de la
    personne connectee (le token). Aucun identifiant technique (site_id) a
    connaitre a l'avance - tout est resolu ici, a l'execution."""
    site_path = site_path.strip().strip("/")
    folder_path = folder_path.strip().strip("/")

    if site_path:
        resp = requests.get(
            f"https://graph.microsoft.com/v1.0/sites/{site_path}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        site_id = resp.json()["id"]
        base = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:"
    else:
        base = "https://graph.microsoft.com/v1.0/me/drive/root:"

    if folder_path:
        base = f"{base}/{folder_path}"
    return base


def upload_csv_to_graph(rows: list[dict], filename: str, token: str, upload_base_url: str):
    """Ecrit rows directement sur OneDrive/SharePoint via Microsoft Graph (PUT).
    Le sous-dossier cible est cree automatiquement par Graph s'il n'existe pas
    encore."""
    if not rows:
        return
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    csv_bytes = buffer.getvalue().encode("utf-8-sig")

    url = f"{upload_base_url.rstrip('/')}/{filename}:/content"
    resp = requests.put(
        url,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "text/csv"},
        data=csv_bytes,
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()


def mailchimp_click_reports(api_key: str) -> list[dict]:
    """Un seul appel : /campaigns/click-details agrege deja toutes les
    campagnes cote serveur quand campaign_id n'est pas fourni."""
    headers = {"X-Mailchimp-API-Key": api_key}
    resp = requests.get(
        f"{API_BASE_URL}/mailchimp/campaigns/click-details",
        headers=headers,
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


def facebook_post_insights(access_token: str, page_id: str) -> list[dict]:
    """Un seul appel : /posts-insights agrege deja tous les posts + leurs
    insights cote serveur."""
    headers = {"X-Facebook-Page-Access-Token": access_token}
    params = {"page_id": page_id, "limit": 100}
    resp = requests.get(
        f"{API_BASE_URL}/facebook/posts-insights",
        headers=headers,
        params=params,
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json().get("posts", [])


def linkedin_posts_with_stats(linkedin_token: str, organization_urn: str) -> list[dict]:
    """
    Recupere tous les posts LinkedIn (historique complet) + leurs stats individuelles.
    linkedin_token : la valeur brute a mettre dans X-OAuth-Credentials,
    deja encodee en base64
    """
    headers = {"X-OAuth-Credentials": linkedin_token}
    params = {"organization_urn": organization_urn}
    resp = requests.get(
        f"{API_BASE_URL}/linkedin/posts",
        headers=headers,
        params=params,
        timeout=LINKEDIN_REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    posts = resp.json().get("posts", [])

    flat_rows: list[dict] = []
    for p in posts:
        stats = p.get("stats") or {}
        flat_rows.append({
            "id": p.get("id"),
            "created_at": p.get("created_at"),
            "published_at": p.get("published_at"),
            "commentary": p.get("commentary"),
            "visibility": p.get("visibility"),
            "impressions": stats.get("impressions"),
            "unique_impressions": stats.get("unique_impressions"),
            "clicks": stats.get("clicks"),
            "likes": stats.get("likes"),
            "comments": stats.get("comments"),
            "shares": stats.get("shares"),
            "engagement": stats.get("engagement"),
        })
    return flat_rows


def run_refresh(mailchimp_key: str, facebook_token: str, facebook_page_id: str,
                 linkedin_token: str, linkedin_org_urn: str,
                 site_path: str, folder_path: str, log_queue: queue.Queue):
    try:
        log_queue.put("Connexion a Microsoft (une fenetre va s'ouvrir)...")
        token = get_graph_token()
        log_queue.put("Connexion Microsoft reussie.")
    except Exception as e:
        log_queue.put(f"ERREUR connexion Microsoft : {e}")
        log_queue.put("TERMINE")
        return

    try:
        log_queue.put("Resolution du dossier de destination...")
        upload_base = resolve_upload_base(token, site_path, folder_path)
        log_queue.put("Dossier de destination trouve.")
    except Exception as e:
        log_queue.put(f"ERREUR resolution du dossier : {e}")
        log_queue.put("TERMINE")
        return

    try:
        log_queue.put("Mailchimp : recuperation des click reports...")
        rows = mailchimp_click_reports(mailchimp_key)
        upload_csv_to_graph(rows, "mailchimp_click_reports.csv", token, upload_base)
        log_queue.put(f"Mailchimp : {len(rows)} lignes envoyees sur SharePoint/OneDrive.")
    except Exception as e:
        log_queue.put(f"Mailchimp : ERREUR - {e}")

    try:
        log_queue.put("Facebook : recuperation des posts + insights...")
        rows = facebook_post_insights(facebook_token, facebook_page_id)
        upload_csv_to_graph(rows, "facebook_posts.csv", token, upload_base)
        log_queue.put(f"Facebook : {len(rows)} lignes envoyees sur SharePoint/OneDrive.")
    except Exception as e:
        log_queue.put(f"Facebook : ERREUR - {e}")

    if linkedin_token:
        try:
            log_queue.put("LinkedIn : recuperation des posts + stats (peut prendre plusieurs minutes)...")
            rows = linkedin_posts_with_stats(linkedin_token, linkedin_org_urn)
            upload_csv_to_graph(rows, "linkedin_posts.csv", token, upload_base)
            log_queue.put(f"LinkedIn : {len(rows)} lignes envoyees sur SharePoint/OneDrive.")
        except Exception as e:
            log_queue.put(f"LinkedIn : ERREUR - {e}")
    else:
        log_queue.put("LinkedIn : ignore (champ vide).")

    log_queue.put("TERMINE")


def main():
    root = tk.Tk()
    root.title("Rafraichissement CSV - CERIU")
    root.geometry("480x680")

    frm = ttk.Frame(root, padding=12)
    frm.pack(fill="both", expand=True)

    ttk.Label(frm, text="Cle API Mailchimp :").pack(anchor="w")
    mailchimp_var = tk.StringVar()
    ttk.Entry(frm, textvariable=mailchimp_var, width=45, show="*").pack(fill="x", pady=(0, 8))

    ttk.Label(frm, text="Token Facebook (page access token) :").pack(anchor="w")
    facebook_var = tk.StringVar()
    ttk.Entry(frm, textvariable=facebook_var, width=45, show="*").pack(fill="x", pady=(0, 8))

    ttk.Label(frm, text="ID de la page Facebook :").pack(anchor="w")
    facebook_page_id_var = tk.StringVar(value=DEFAULT_FACEBOOK_PAGE_ID)
    ttk.Entry(frm, textvariable=facebook_page_id_var, width=45).pack(fill="x", pady=(0, 8))

    ttk.Label(frm, text="Token LinkedIn:").pack(anchor="w")
    linkedin_token_var = tk.StringVar()
    ttk.Entry(frm, textvariable=linkedin_token_var, width=45, show="*").pack(fill="x", pady=(0, 8))

    ttk.Label(frm, text="LinkedIn Organization URN :").pack(anchor="w")
    linkedin_org_urn_var = tk.StringVar(value=DEFAULT_LINKEDIN_ORG_URN)
    ttk.Entry(frm, textvariable=linkedin_org_urn_var, width=45).pack(fill="x", pady=(0, 8))

    ttk.Label(frm, text="Site SharePoint :").pack(anchor="w")
    site_path_var = tk.StringVar(value=DEFAULT_SITE_PATH)
    ttk.Entry(frm, textvariable=site_path_var, width=45).pack(fill="x", pady=(0, 8))

    ttk.Label(frm, text="Dossier cible :").pack(anchor="w")
    folder_path_var = tk.StringVar(value=DEFAULT_FOLDER_PATH)
    ttk.Entry(frm, textvariable=folder_path_var, width=45).pack(fill="x", pady=(0, 12))

    progress = ttk.Progressbar(frm, mode="indeterminate")
    progress.pack(fill="x", pady=(0, 8))

    log_box = scrolledtext.ScrolledText(frm, height=12, state="disabled")
    log_box.pack(fill="both", expand=True, pady=(0, 12))

    def log(msg: str):
        log_box.configure(state="normal")
        log_box.insert("end", msg + "\n")
        log_box.see("end")
        log_box.configure(state="disabled")

    log_queue: queue.Queue = queue.Queue()

    def poll_queue():
        try:
            while True:
                msg = log_queue.get_nowait()
                if msg == "TERMINE":
                    progress.stop()
                    log("Rafraichissement termine. Vous pouvez fermer cette fenetre.")
                    button.config(state="normal")
                    return
                log(msg)
        except queue.Empty:
            pass
        root.after(100, poll_queue)

    def start():
        mailchimp_key = mailchimp_var.get().strip()
        facebook_token = facebook_var.get().strip()
        facebook_page_id = facebook_page_id_var.get().strip()
        linkedin_token = linkedin_token_var.get().strip()
        linkedin_org_urn = linkedin_org_urn_var.get().strip()
        site_path = site_path_var.get().strip()
        folder_path = folder_path_var.get().strip()

        if not mailchimp_key or not facebook_token or not facebook_page_id:
            messagebox.showerror("Champs manquants", "Renseignez la cle, le token et l'ID de page.")
            return

        button.config(state="disabled")
        progress.start(10)
        log("Demarrage du rafraichissement...")
        threading.Thread(
            target=run_refresh,
            args=(
                mailchimp_key, facebook_token, facebook_page_id,
                linkedin_token, linkedin_org_urn,
                site_path, folder_path, log_queue,
            ),
            daemon=True,
        ).start()
        root.after(100, poll_queue)

    button = ttk.Button(frm, text="Lancer le rafraichissement", command=start)
    button.pack()

    root.mainloop()


if __name__ == "__main__":
    main()