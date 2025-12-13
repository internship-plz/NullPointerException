import os
import requests
from collections import defaultdict
from urllib.parse import urlparse
import json

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
def get_repo_languages(owner: str, repo: str) -> dict:
    """
    Returns:
        { "Python": bytes, "JavaScript": bytes, ... }
    """
    url = f"{GITHUB_API}/repos/{owner}/{repo}/languages"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

GITHUB_API = "https://api.github.com"
from dotenv import load_dotenv
load_dotenv("a.env")
TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github+json"
}

def parse_profile_url(profile_url: str):
    path = profile_url.rstrip("/").split("/")
    return path[-1]

def get_user_repos(username):
    repos = []
    page = 1

    while True:
        r = requests.get(
            f"https://api.github.com/users/{username}/repos",
            headers=HEADERS,
            params={"per_page": 100, "page": page}
        )
        r.raise_for_status()
        batch = r.json()

        if not batch:
            break

        repos.extend(batch)
        page += 1

    return repos
def analyze_profile(profile_url):
    username = parse_profile_url(profile_url)
    repos = get_user_repos(username)

    profile_summary = {
        "username": username,
        "repo_count": len(repos),
        "languages": defaultdict(int)
    }

    for repo in repos:
        if repo["fork"]:
            continue  # skip forks

        owner = repo["owner"]["login"]
        name = repo["name"]

        langs = get_repo_languages(owner, name)
        for lang, bytes_ in langs.items():
            profile_summary["languages"][lang] += bytes_

    return profile_summary
profile = analyze_profile("https://github.com/OliverBao")
save_json(profile, "profile.json")
