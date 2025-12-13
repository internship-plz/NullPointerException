import requests
from pathlib import Path
import json
url = "https://leetcode.com/graphql"
query = """
query getUserProfile($username: String!) {
  matchedUser(username: $username) {
    username
    submitStatsGlobal {
      acSubmissionNum {
        difficulty
        count
        submissions
      }
    }
  }
}
"""

query2 = """
query getUserProfile($username: String!) {
  matchedUser(username: $username) {
    username
    languageProblemCount {
      languageName
      problemsSolved
    }
    submitStatsGlobal {
      acSubmissionNum {
        difficulty
        count
      }
    }
  }
}
"""
def analyze_leetcode(username):
  variables = {"username": username}

  r = requests.post(url, json={"query": query2, "variables": variables})
  data = r.json()

  # Example: extract languages
  langs = data["data"]["matchedUser"]["languageProblemCount"]
  lang_vector = {l["languageName"]: l["problemsSolved"] for l in langs}
  final_vector = {"languages": lang_vector}

  r = requests.post(url, json={"query": query, "variables": variables}).json()
  final_vector["submissions"] = r["data"]["matchedUser"]["submitStatsGlobal"]["acSubmissionNum"]
  return final_vector
def load_users():
    DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "users.json"

    if not DATA_PATH.exists():
        return {}
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "users.json"

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)
def add_leetcode(username, email):
    profile = analyze_leetcode(username)
    users = load_users()
    users[email]["leetcode"] = profile
    save_users(users)
add_leetcode("chillyy", "hi@hi")
