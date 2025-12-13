import requests

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
username = "chillyy"

variables = {"username": username}

r = requests.post(url, json={"query": query2, "variables": variables})
data = r.json()

# Example: extract languages
langs = data["data"]["matchedUser"]["languageProblemCount"]
lang_vector = {l["languageName"]: l["problemsSolved"] for l in langs}
print(lang_vector)

r = requests.post(url, json={"query": query, "variables": variables})
print(r.json())
#-------------------------------------------------------------