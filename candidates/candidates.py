import json

class CandidateSupplier:
    def __init__(self):
        self.candidates = self.load_candidates()


    def load_candidates(self, file_path: str='data/users.json'):
        with open(file_path, 'r') as f:
            users = json.load(f)

        candidates = {}

        for user_id, user_info in users.items():
            if user_info.get('role') == 'candidate':
                candidates[user_id] = Candidate(
                    candidate_id=user_id,
                    name=user_info.get('name', ''),
                    skills=user_info.get('skills', [])
                )


    def add_candidate(self, candidate_id: str, password: str, name: str, skills: list):
        with open('data/users.json', 'r') as f:
            users = json.load(f)
        users[candidate_id] = {
            "name": name,
            "password": password,
            "role": "candidate",
            "skills": skills
        }
        with open('data/users.json', 'w') as f:
            json.dump(users, f, indent=4)
        self.load_candidates()


    def get_candidate_skills(self, candidate_id: str):
        candidate = self.candidates.get(candidate_id)
        
        return candidate.skills


class Candidate:
    def __init__(self, candidate_id: str, name: str, skills: list):
        self.candidate_id = candidate_id
        self.name = name
        self.skills = skills
