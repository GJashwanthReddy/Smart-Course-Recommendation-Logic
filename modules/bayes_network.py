"""
=============================================================
BAYES_NETWORK: Success Confidence Forecasting
=============================================================
Implements:
  - Bayesian Network representing academic success variables
  - Directed structure: 
      Prereq (P) ──┐
      Interest (I) ┼──> Success (C)
      StudyTime (S)┘
  - Conditional Probability Tables (CPTs)
  - Exact joint probability inference (Inference by Enumeration)
  - Confidence scoring for taking recommended courses
=============================================================
"""

from typing import List, Dict, Set, Tuple, Optional
from .formulation import CourseRecord, CandidateProfile

class SuccessNetwork:
    """
    Models joint probabilities of course success using a Bayesian Network.
    Nodes:
      - P (Prereq Completed): Prior probability based on whether student has met prereqs.
      - I (Interest High): Prior probability based on interest match utility.
      - S (Study Time High): Prior probability based on CGPA and course workload.
      - C (Course Success): Dependent on P, I, S.
    """
    def __init__(self):
        # CPT for P(C | P, I, S)
        # Key: (P_val, I_val, S_val) where values are booleans
        # Value: P(C = True | P, I, S)
        self.cpt_c: Dict[Tuple[bool, bool, bool], float] = {
            (True, True, True): 0.95,     # All factors favorable
            (True, True, False): 0.75,    # Misses sufficient study time
            (True, False, True): 0.80,    # Lacks interest but works hard
            (True, False, False): 0.50,   # Has prereqs only
            (False, True, True): 0.60,    # Lacks prereqs but has interest/hard work
            (False, True, False): 0.40,   # Interest only
            (False, False, True): 0.30,   # Study time only
            (False, False, False): 0.10,  # No favorable factors
        }

    def compute_prior_p(self, course: CourseRecord, profile: CandidateProfile) -> float:
        """Determines prior probability P(P = True) based on completed prerequisites."""
        if not course.prereqs:
            return 1.0
        met_count = sum(1 for p in course.prereqs if p in profile.completed)
        return met_count / len(course.prereqs)

    def compute_prior_i(self, course: CourseRecord, profile: CandidateProfile) -> float:
        """Determines prior probability P(I = True) based on interest match."""
        # Simple interest match ratio
        if not profile.interests:
            return 0.5
        matched = 0
        search_space = (course.title + " " + course.description + " " + " ".join(course.skills)).lower()
        for interest in profile.interests:
            if interest.lower() in search_space:
                matched += 1
        return 0.1 + 0.8 * (matched / len(profile.interests))  # Bound between 0.1 and 0.9

    def compute_prior_s(self, course: CourseRecord, profile: CandidateProfile) -> float:
        """Determines prior probability P(S = True) based on student CGPA and workload."""
        # Study time probability is higher for high CGPA and low difficulty courses
        cgpa_factor = profile.cgpa / 10.0
        difficulty_factor = 1.0 - (course.difficulty / 5.0)
        prob = 0.5 * cgpa_factor + 0.5 * difficulty_factor
        return max(0.1, min(0.9, prob))

    def evaluate_joint(self, p_val: bool, i_val: bool, s_val: bool, c_val: bool, 
                       prior_p: float, prior_i: float, prior_s: float) -> float:
        """Returns joint probability P(P=p, I=i, S=s, C=c)."""
        # P(P)
        p_prob = prior_p if p_val else (1.0 - prior_p)
        # P(I)
        i_prob = prior_i if i_val else (1.0 - prior_i)
        # P(S)
        s_prob = prior_s if s_val else (1.0 - prior_s)
        # P(C | P, I, S)
        cond_c = self.cpt_c[(p_val, i_val, s_val)]
        c_prob = cond_c if c_val else (1.0 - cond_c)
        
        return p_prob * i_prob * s_prob * c_prob

    def query_success_marginal(self, course: CourseRecord, profile: CandidateProfile, 
                               evidence: Dict[str, bool] = None) -> float:
        """
        Runs Inference by Enumeration to compute P(C = True | Evidence).
        Evidence can specify values for 'P', 'I', or 'S'.
        """
        prior_p = self.compute_prior_p(course, profile)
        prior_i = self.compute_prior_i(course, profile)
        prior_s = self.compute_prior_s(course, profile)
        
        if evidence is None:
            evidence = {}

        # If variable is in evidence, its value is fixed, else we sum over both True and False
        p_domain = [evidence['P']] if 'P' in evidence else [True, False]
        i_domain = [evidence['I']] if 'I' in evidence else [True, False]
        s_domain = [evidence['S']] if 'S' in evidence else [True, False]
        
        # Calculate P(C = True, Evidence)
        numerator = 0.0
        for p in p_domain:
            for i in i_domain:
                for s in s_domain:
                    numerator += self.evaluate_joint(p, i, s, True, prior_p, prior_i, prior_s)
                    
        # Calculate P(Evidence) = P(C=True, Evidence) + P(C=False, Evidence)
        denominator = numerator
        for p in p_domain:
            for i in i_domain:
                for s in s_domain:
                    denominator += self.evaluate_joint(p, i, s, False, prior_p, prior_i, prior_s)
                    
        if denominator == 0.0:
            return 0.0
            
        return numerator / denominator

def run_bayes_demo(catalog: List[CourseRecord], profile: CandidateProfile):
    """Demonstrates Bayesian network inference for catalog courses."""
    print("\n" + "=" * 60)
    print("  BAYESIAN NETWORK FOR SUCCESS CONFIDENCE FORECASTING")
    print("=" * 60)
    
    network = SuccessNetwork()
    
    print(f"  Student Profile: CGPA={profile.completed} (CGPA={profile.cgpa}), Interests={profile.interests}")
    print("-" * 60)
    
    print(f"  {'Code':<7} | {'Course Title':<25} | {'P(P=T)':<7} | {'P(I=T)':<7} | {'P(S=T)':<7} | {'P(Success)'}")
    print(f"  {'-'*7} | {'-'*25} | {'-'*7} | {'-'*7} | {'-'*7} | {'-'*10}")
    
    for c in catalog:
        prior_p = network.compute_prior_p(c, profile)
        prior_i = network.compute_prior_i(c, profile)
        prior_s = network.compute_prior_s(c, profile)
        
        # Query 1: Marginal probability of success with no evidence (just priors)
        p_success = network.query_success_marginal(c, profile)
        
        print(f"  {c.code:<7} | {c.title:<25} | {prior_p:<7.2f} | {prior_i:<7.2f} | {prior_s:<7.2f} | {p_success:.2%}")
        
    print("\n  [INFERENCE BY ENUMERATION QUERY DEMONSTRATIONS]")
    print("-" * 60)
    # Pick a course (e.g. the first one)
    test_course = catalog[0]
    print(f"  Selected Course for Query: {test_course.code} ({test_course.title})")
    
    # Query A: Success marginal (Priors only)
    ans_a = network.query_success_marginal(test_course, profile)
    print(f"  - P(Success) [Priors only]: {ans_a:.2%}")
    
    # Query B: Success given low study time
    ans_b = network.query_success_marginal(test_course, profile, evidence={'S': False})
    print(f"  - P(Success | StudyTime = Low): {ans_b:.2%}")
    
    # Query C: Success given prerequisites completed and high study time
    ans_c = network.query_success_marginal(test_course, profile, evidence={'P': True, 'S': True})
    print(f"  - P(Success | PrereqsMet = True, StudyTime = High): {ans_c:.2%}")
    print()
