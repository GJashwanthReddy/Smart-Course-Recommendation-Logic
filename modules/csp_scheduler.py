"""
=============================================================
CSP_SCHEDULER: Term-by-Term Scheduler (Constraint Propagation)
=============================================================
Implements:
  - Variables (courses to schedule) and Domains (available terms)
  - Prerequisite and term credit constraints
  - Backtracking search for valid schedules
  - Variable ordering heuristics: Minimum Remaining Values (MRV) & Degree Heuristic
  - Value propagation: Forward Checking (FC)
=============================================================
"""

from typing import List, Dict, Set, Tuple, Optional
from .formulation import CourseRecord

class CourseCSP:
    """
    Formulates and solves the course scheduling problem as a CSP.
    Variables: Course codes
    Domains: Available terms (e.g., {1, 2, 3})
    Constraints:
      - Prerequisite order: term(prereq) < term(course)
      - Term Credit Limit: sum of credits in a term <= max_credits
    """
    def __init__(self, courses_to_schedule: List[CourseRecord], total_terms: int = 3, max_credits: int = 8):
        self.courses = {c.code: c for c in courses_to_schedule}
        self.variables = list(self.courses.keys())
        self.total_terms = total_terms
        self.max_credits = max_credits
        
        # Initial domains: each course can be scheduled in any term 1 to total_terms
        self.domains: Dict[str, Set[int]] = {code: set(range(1, total_terms + 1)) for code in self.variables}
        
        # Tracks variables constraints (edges) for degree heuristic
        # An edge exists between two courses if one is a prerequisite of another
        self.constraints: Dict[str, Set[str]] = {code: set() for code in self.variables}
        for code, course in self.courses.items():
            for prereq in course.prereqs:
                if prereq in self.constraints:
                    self.constraints[code].add(prereq)
                    self.constraints[prereq].add(code)

        # Logging trace of steps
        self.trace_logs: List[str] = []
        self.backtrack_count = 0
        self.nodes_visited = 0

    def get_mrv_variables(self, assignment: Dict[str, int]) -> List[str]:
        """Returns unassigned variables with the minimum domain size."""
        unassigned = [v for v in self.variables if v not in assignment]
        if not unassigned:
            return []
        
        # Find minimum domain size
        min_size = min(len(self.domains[v]) for v in unassigned)
        return [v for v in unassigned if len(self.domains[v]) == min_size]

    def select_variable(self, assignment: Dict[str, int]) -> str:
        """Selects variable using MRV with Degree Heuristic as a tie-breaker."""
        mrv_candidates = self.get_mrv_variables(assignment)
        if len(mrv_candidates) == 1:
            self.trace_logs.append(f"  [MRV] Selected '{mrv_candidates[0]}' (only candidate with min domain size {len(self.domains[mrv_candidates[0]])})")
            return mrv_candidates[0]
        
        # Tie break using Degree Heuristic (most constraints with other unassigned variables)
        best_var = mrv_candidates[0]
        max_degree = -1
        
        unassigned_set = set(self.variables) - set(assignment.keys())
        for var in mrv_candidates:
            # Count constraints with other UNASSIGNED variables
            degree = len(self.constraints[var].intersection(unassigned_set))
            if degree > max_degree:
                max_degree = degree
                best_var = var
                
        self.trace_logs.append(
            f"  [MRV+Degree] Selected '{best_var}' (mrv size {len(self.domains[best_var])}, unassigned degree {max_degree})"
        )
        return best_var

    def check_consistency(self, var: str, val: int, assignment: Dict[str, int]) -> bool:
        """Checks if assigning course 'var' to term 'val' violates constraints."""
        # 1. Check Credit Limit constraint
        current_term_credits = self.courses[var].credits
        for assigned_var, assigned_val in assignment.items():
            if assigned_val == val:
                current_term_credits += self.courses[assigned_var].credits
                
        if current_term_credits > self.max_credits:
            return False

        # 2. Check Prerequisite constraints
        course = self.courses[var]
        
        # Check: If prereq is already assigned, it must be in a strictly earlier term
        for prereq in course.prereqs:
            if prereq in assignment:
                if assignment[prereq] >= val:
                    return False
                    
        # Check: If dependents are already assigned, they must be in a strictly later term
        for other_code, other_course in self.courses.items():
            if var in other_course.prereqs and other_code in assignment:
                if assignment[other_code] <= val:
                    return False
                    
        return True

    def forward_check(self, var: str, val: int, assignment: Dict[str, int]) -> Optional[Dict[str, Set[int]]]:
        """
        Performs forward checking: refines domains of unassigned variables based on assigning var=val.
        Returns a copy of revised domains, or None if any domain becomes empty.
        """
        revised_domains = {v: set(domain) for v, domain in self.domains.items()}
        unassigned = [v for v in self.variables if v not in assignment and v != var]
        
        # For the assigned variable, restrict its domain to just the chosen value
        revised_domains[var] = {val}
        
        for u in unassigned:
            u_course = self.courses[u]
            to_remove = set()
            
            for possible_val in revised_domains[u]:
                # Check prereq constraint: if var is prereq of u, u must be scheduled after var
                if var in u_course.prereqs and possible_val <= val:
                    to_remove.add(possible_val)
                    
                # Check prereq constraint: if u is prereq of var, u must be scheduled before var
                if u in self.courses[var].prereqs and possible_val >= val:
                    to_remove.add(possible_val)
                    
            if to_remove:
                revised_domains[u] = revised_domains[u] - to_remove
                if not revised_domains[u]:
                    self.trace_logs.append(f"    [FC Failure] Domain of unassigned '{u}' became empty. Backtracking.")
                    return None  # Failure: empty domain
                    
        return revised_domains

    def solve(self) -> Optional[Dict[str, int]]:
        """Starts the recursive backtracking search."""
        self.trace_logs = []
        self.backtrack_count = 0
        self.nodes_visited = 0
        self.trace_logs.append(f"Starting CSP Scheduler (Terms: {self.total_terms}, Max Credits/Term: {self.max_credits})")
        
        assignment = {}
        result = self._backtrack(assignment)
        if result:
            self.trace_logs.append("CSP Search successfully completed with a valid schedule.")
        else:
            self.trace_logs.append("CSP Search failed to find a valid schedule.")
        return result

    def _backtrack(self, assignment: Dict[str, int]) -> Optional[Dict[str, int]]:
        self.nodes_visited += 1
        
        # Base case: assignment is complete
        if len(assignment) == len(self.variables):
            return assignment

        var = self.select_variable(assignment)
        ordered_values = sorted(list(self.domains[var]))
        
        for val in ordered_values:
            self.trace_logs.append(f"  Trying '{var}' in Term {val}")
            
            if self.check_consistency(var, val, assignment):
                # Apply assignment
                assignment[var] = val
                
                # Save domain state and run forward checking
                old_domains = self.domains
                fc_result = self.forward_check(var, val, assignment)
                
                if fc_result is not None:
                    self.domains = fc_result
                    # Recurse
                    result = self._backtrack(assignment)
                    if result is not None:
                        return result
                    
                # Backtrack: restore domains and remove assignment
                self.domains = old_domains
                del assignment[var]
                self.backtrack_count += 1
                self.trace_logs.append(f"  [Backtrack] Removed '{var}' from Term {val}")
            else:
                self.trace_logs.append(f"    [Inconsistent] '{var}' cannot be in Term {val} due to constraints")
                
        return None

def run_scheduler_demo(catalog: List[CourseRecord]):
    """Demonstrates course scheduler with trace logs and nice output formatting."""
    print("\n" + "=" * 60)
    print("  TERM-BY-TERM COURSE SCHEDULER (CSP SOLVER)")
    print("=" * 60)
    
    # We will schedule all courses in the catalog
    scheduler = CourseCSP(catalog, total_terms=3, max_credits=8)
    schedule = scheduler.solve()
    
    # Print scheduling trace log (first 15 lines, then summary)
    print("  [CSP Backtracking Search Trace]")
    for line in scheduler.trace_logs[:20]:
        print(line)
    if len(scheduler.trace_logs) > 20:
        print(f"  ... [Truncated {len(scheduler.trace_logs) - 20} trace lines] ...")
        print(scheduler.trace_logs[-1])
        
    print(f"\n  Search Nodes Visited: {scheduler.nodes_visited}")
    print(f"  Total Backtracks Encountered: {scheduler.backtrack_count}")
    print("-" * 60)
    
    if schedule:
        # Sort courses by assigned term
        term_buckets: Dict[int, List[str]] = {t: [] for t in range(1, scheduler.total_terms + 1)}
        for c_code, term in schedule.items():
            term_buckets[term].append(c_code)
            
        print("  FINAL SCHEDULE LAYOUT")
        print("-" * 60)
        for term in sorted(term_buckets.keys()):
            term_courses = term_buckets[term]
            term_credits = sum(scheduler.courses[c].credits for c in term_courses)
            print(f"  Term {term} ({term_credits} credits):")
            for c_code in term_courses:
                c = scheduler.courses[c_code]
                print(f"    - {c.code:<7} | {c.title:<28} | {c.credits} Credits | Diff: {c.difficulty}")
            print()
    else:
        print("  Error: No valid schedule could be resolved under constraints.")
    print()
