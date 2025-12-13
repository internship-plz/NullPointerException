from candidates.candidates import CandidateSupplier
from companies.companies import JobSupplier, Job

class Service:
    def __init__(self):
        self.candidate_supplier = CandidateSupplier()
        self.job_supplier = JobSupplier()

    
    def add_candidate(self, candidate_id: str, password: str, name: str, skills: list):
        self.candidate_supplier.add_candidate(candidate_id, password, name, skills)


    def job_search(self, candidate_id: str):
        return self.job_supplier.get_bids_for_candidate(
            self.candidate_supplier.get_candidate_skills(candidate_id)
        )


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
