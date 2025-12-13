class JobSupplier:
    def __init__(self, )

class Company:
    def __init__(self, company_id: str, name: str, match_threshold: float, jobs: list):
        self.company_id = company_id
        self.name = name
        self.jobs = jobs


    def find_job_for_candidate(self, candidate_skills: dict):
        


class Job:
    def __init__(self, job_id: str, title: str, description: str, weights: dict, maximum_pay: float, starting_pay: float):
        self.job_id = job_id
        self.title = title
        self.description = description
        self.weights = weights
        self.maximum_pay = maximum_pay
        self.starting_pay = starting_pay


    def calculate_match(self, candidate_skills: dict) -> float:
        total_weight = sum(self.weights.values())
        if total_weight == 0:
            return 0.0

        match_score = 0.0
        for skill, weight in self.weights.items():
            candidate_skill_level = candidate_skills.get(skill, 0)
            match_score += (candidate_skill_level * weight)

        return match_score / total_weight
    