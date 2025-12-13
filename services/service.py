from candidates.candidates import CandidateSupplier
from companies.companies import JobSupplier, Job

class Service:
    def __init__(self):
        self.candidate_supplier = CandidateSupplier()
        self.job_supplier = JobSupplier()

    
    def add_candidate(self, candidate_id: str, password: str, name: str, skills: list):
        self.candidate_supplier.add_candidate(candidate_id, password, name, skills)


    def job_search(self, candidate_id: str):
        candidate_skills = self.candidate_supplier.get_candidate_skills(candidate_id) or {}

        all_jobs = []
        bids_map = {}

        # Iterate companies and jobs to build serializable results
        for company_id, company in self.job_supplier.companies.items():
            for job in company.jobs:
                job_dict = {
                    'job_id': job.job_id,
                    'title': job.title,
                    'description': job.description,
                    'weights': job.weights,
                    'match_threshold': job.match_threshold,
                    'maximum_pay': job.maximum_pay,
                    'starting_pay': job.starting_pay,
                    'company_email': company_id,
                    'company_name': company.name
                }

                try:
                    match_score = job.calculate_match(candidate_skills)
                    job_dict['_match_score'] = round(float(match_score), 4)
                    job_dict['_meets'] = (match_score > float(job.match_threshold))
                except Exception:
                    job_dict['_match_score'] = 0.0
                    job_dict['_meets'] = False

                try:
                    bid_amount = job.calculate_bid(candidate_skills)
                    if bid_amount is not None:
                        bid_amount = round(float(bid_amount), 2)
                    job_dict['_bid_amount'] = bid_amount
                except Exception:
                    job_dict['_bid_amount'] = None

                all_jobs.append(job_dict)

                # if there is a bid, add to bids_map keyed by job_id
                if job_dict.get('_bid_amount') is not None:
                    bids_map[job.job_id] = job_dict['_bid_amount']

        # persist bid offers to candidate record
        try:
            self.candidate_supplier.add_bid_offers(candidate_id, bids_map)
        except Exception:
            # don't fail the whole search if persisting bids fails
            pass

        return all_jobs


    def add_job(self, company_id: str, job_id: str, title: str, description: str, weights: dict, match_threshold: float, maximum_pay: float, starting_pay: float):

        job = Job(
            job_id=job_id,
            title=title,
            description=description,
            weights=weights,
            match_threshold=match_threshold,
            maximum_pay=maximum_pay,
            starting_pay=starting_pay
        )

        company = self.job_supplier.companies[company_id]
        company.add_job(job)
