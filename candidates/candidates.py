import json

def job_search(candidate_id: str):
    with open('data/users.json', 'r') as f:
        users = json.load(f)

    candidate = users.get(candidate_id, {})
    
    if not candidate:
        return {}
    
    return candidate['skills']
