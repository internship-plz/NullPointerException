from candidates.candidates import CandidateSupplier

class Service:
    def __init__(self):
        self.candidate_supplier = CandidateSupplier()

    
    def add_candidate(self, candidate_id: str, password: str, name: str, skills: list):
        self.candidate_supplier.add_candidate(candidate_id, password, name, skills)


    def job_search(self, candidate_id: str):
        pass
