"""
github_detector.py - Détection Dockerfile via URL GitHub
- Parse URL, appelle GitHub API + raw.githubusercontent
- Fallback: tentative fetch direct sans token
"""
import re
import requests

GITHUB_API = "https://api.github.com"
RAW_BASE = "https://raw.githubusercontent.com"

def parse_github_url(url: str):
    """
    Supporte:
    - https://github.com/org/repo
    - https://github.com/org/repo.git
    - https://github.com/org/repo/tree/main
    - git@github.com:org/repo.git
    """
    url = url.strip().rstrip("/")
    # SSH
    m = re.match(r"git@github\.com:([^/]+)/([^/]+?)(\.git)?$", url)
    if m:
        return m.group(1), m.group(2)
    # HTTPS
    m = re.match(r"https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?(?:/.*)?$", url)
    if m:
        return m.group(1), m.group(2)
    raise ValueError("URL GitHub invalide. Ex: https://github.com/org/repo")

def fetch_repo_info(owner: str, repo: str, token: str = None):
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    r = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}", headers=headers, timeout=10)
    if r.status_code == 404:
        raise FileNotFoundError("Repo non trouvé ou privé (token requis)")
    r.raise_for_status()
    j = r.json()
    return {
        "full_name": j["full_name"],
        "default_branch": j.get("default_branch", "main"),
        "language": j.get("language"),
        "private": j.get("private"),
        "description": j.get("description"),
    }

def detect_dockerfile(owner: str, repo: str, branch: str, token: str = None):
    """
    Cherche Dockerfile à la racine et dans subpaths courants.
    Retourne {found, path, raw_url}
    """
    candidates = ["Dockerfile", "docker/Dockerfile", "build/Dockerfile", "Dockerfile.dev"]
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"

    # 1. Essai via GitHub API contents
    for path in candidates:
        url = f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}?ref={branch}"
        try:
            r = requests.get(url, headers=headers, timeout=8)
            if r.status_code == 200:
                j = r.json()
                return {
                    "found": True,
                    "path": path,
                    "raw_url": j.get("download_url") or f"{RAW_BASE}/{owner}/{repo}/{branch}/{path}",
                    "size": j.get("size"),
                }
        except requests.RequestException:
            continue

    # 2. Fallback raw fetch direct (public repos)
    for path in candidates:
        raw = f"{RAW_BASE}/{owner}/{repo}/{branch}/{path}"
        try:
            r = requests.head(raw, timeout=6)
            if r.status_code == 200:
                return {"found": True, "path": path, "raw_url": raw, "size": None}
        except requests.RequestException:
            continue

    return {"found": False, "path": None, "raw_url": None}

def fetch_file_content(raw_url: str, token: str = None) -> str:
    headers = {}
    if token and "api.github.com" in raw_url:
        headers["Authorization"] = f"token {token}"
    r = requests.get(raw_url, headers=headers, timeout=10)
    r.raise_for_status()
    return r.text

def fetch_repo_file_list(owner: str, repo: str, branch: str, token: str = None):
    """Liste fichiers racine pour détection technologie (package.json etc)"""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    r = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}/contents?ref={branch}", headers=headers, timeout=10)
    if r.status_code != 200:
        return []
    try:
        return [x["name"] for x in r.json() if isinstance(x, dict) and "name" in x]
    except Exception:
        return []
