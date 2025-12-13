import json

class JobSupplier:
    def __init__(self):
        self.companies = self.load_companies()


    def load_companies(self, file_path: str='data/users.json'):
        with open(file_path, 'r') as f:
            users = json.load(f)

        companies = {}

        for user_id, user_info in users.items():
            if user_info.get('role') == 'employer':
                company = Company(
                    company_id=user_id,
                    name=user_info.get('name', ''),
                    match_threshold=user_info.get('match_threshold', 0.0),
                    jobs=[]
                )
                company.load_jobs()
                companies[user_id] = company

        return companies
    

    def get_bids_for_candidate(self, candidate_skills: dict):
        bids = {}
        for _, company in self.companies.items():
            job, bid_amount = company.find_job_bid_for_candidate(candidate_skills)
            if job is not None:
                bids[company] = {
                    "job": job,
                    "bid_amount": bid_amount
                }  
        return bids
        

class Job:
    def __init__(self, job_id: str, title: str, description: str, weights: dict, match_threshold: float, maximum_pay: float, starting_pay: float):
        self.job_id = job_id
        self.title = title
        self.description = description
        self.weights = weights
        self.match_threshold = match_threshold
        self.maximum_pay = maximum_pay
        self.starting_pay = starting_pay


    def calculate_bid(self, candidate_skills: dict):
        match_score = self.calculate_match(candidate_skills)
        if match_score <= self.match_threshold:
            return None
        
        bid_amount = self.starting_pay + (match_score * (self.maximum_pay - self.starting_pay))
        return bid_amount


    def calculate_match(self, candidate_skills: dict):
        total_weight = sum(self.weights.values())
        if total_weight == 0:
            return 0.0
        match_score = 0.0
        for skill, weight in self.weights.items():
            candidate_skill_level = candidate_skills.get(skill, 0)
            try:
                match_score += (float(candidate_skill_level) * float(weight))
            except Exception:
                # ignore non-numeric values
                pass

        return match_score / total_weight
    

class Company:
    def __init__(self, company_id: str, name: str, match_threshold: float, jobs: list):
        self.company_id = company_id
        self.name = name
        self.match_threshold = match_threshold
        self.jobs = jobs


    def load_jobs(self):
        with open('data/users.json', 'r') as f:
            users = json.load(f)

        company_info = users.get(self.company_id, {})
        jobs_data = company_info.get('jobs', [])

        self.jobs = []
        for job_data in jobs_data:
            job = Job(
                job_id=job_data['job_id'],
                title=job_data['title'],
                description=job_data['description'],
                weights=job_data['weights'],
                match_threshold=job_data['match_threshold'],
                maximum_pay=job_data['maximum_pay'],
                starting_pay=job_data['starting_pay']
            )
            self.jobs.append(job)


    def add_job(self, job: Job):
        with open('data/users.json', 'r') as f:
            users = json.load(f)

        users[self.company_id]['jobs'].append({
            "job_id": job.job_id,
            "title": job.title,
            "description": job.description,
            "weights": job.weights,
            "match_threshold": job.match_threshold,
            "maximum_pay": job.maximum_pay,
            "starting_pay": job.starting_pay
        })

        with open('data/users.json', 'w') as f:
            json.dump(users, f, indent=4)

        self.load_jobs()


    def find_job_bid_for_candidate(self, candidate_skills: dict):
        highest_suitable_job = None
        highest_bid_amount = 0.0
        for job in self.jobs:
            bid_amount = job.calculate_bid(candidate_skills)
            if bid_amount >= self.match_threshold and bid_amount > highest_bid_amount:
                highest_bid_amount = bid_amount
                highest_suitable_job = job
        return highest_suitable_job, highest_bid_amount
    