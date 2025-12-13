import json

class Candidate:
    def __init__(self, candidate_id: str, name: str, skills: list, bids: dict):
        self.candidate_id = candidate_id
        self.name = name
        self.skills = skills
        self.bids = bids


    def add_bid_offers(self, bids: dict):
        self.bids.update(bids)

        with open('data/users.json', 'r') as f:
            users = json.load(f)
        if self.candidate_id in users:
            users[self.candidate_id]['bids'] = self.bids
        with open('data/users.json', 'w') as f:
                json.dump(users, f, indent=4)


class CandidateSupplier:
    def __init__(self):
        self.candidates = self.load_candidates()


    def load_candidates(self, file_path: str='data/users.json'):
        with open(file_path, 'r') as f:
            users = json.load(f)

        candidates = {}

        for user_id, user_info in users.items():
            if user_info.get('role') == 'candidate':
                raw_skills = user_info.get('skills', {})
                # normalize skills to a dict mapping skill -> float
                if isinstance(raw_skills, list):
                    skills = {}
                else:
                    skills = raw_skills or {}

                candidates[user_id] = Candidate(
                    candidate_id=user_id,
                    name=user_info.get('name', ''),
                    skills=skills,
                    bids=user_info.get('bids', {})
                )

        # store and return candidates mapping
        self.candidates = candidates
        return candidates


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
        if not candidate:
            return {}
        # ensure skills is a dict
        if isinstance(candidate.skills, dict):
            return candidate.skills
        return {}
    

    def add_bid_offers(self, candidate_id: str, bids: dict):
        candidate = self.candidates.get(candidate_id)
        if candidate:
            candidate.add_bid_offers(bids)
