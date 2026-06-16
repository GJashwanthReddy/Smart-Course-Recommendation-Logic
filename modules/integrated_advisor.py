"""
=============================================================
INTEGRATED_ADVISOR: Executing Consolidated AI Reasoning
=============================================================
Implements:
  - Unified pipeline coupling CO1-CO5 components:
    * Graph Search (A* Pathfinding to target skills)
    * CSP Scheduler (Term assignments for path courses)
    * Bayesian Forecasting (Term-by-term success probability)
    * Decision Theory (MAUT rankings & Minimax choice validation)
  - Detailed system trace report outlining multi-agent decisions
=============================================================
"""

from typing import List, Dict, Set, Tuple
from .formulation import CourseRecord, CandidateProfile, AdvisorState
from .search_logic import CourseSearcher
from .csp_scheduler import CourseCSP
from .decision_making import CourseMAUT, GameDecisionMaker, AdvisingGameState
from .bayes_network import SuccessNetwork

class IntegratedAdvisorPipeline:
    """
    Ties search pathfinders, CSP constraint propagation, Bayesian forecasting,
    and decision-theoretic ranking into an explainable advising system.
    """
    def __init__(self, catalog: List[CourseRecord]):
        self.catalog = catalog
        self.maut = CourseMAUT()
        self.bayes = SuccessNetwork()

    def execute_pipeline(self, profile: CandidateProfile) -> Dict:
        """Runs the end-to-end reasoning engine for a candidate student."""
        trace = []
        trace.append(f"Initializing Smart Course Recommendation logic for: '{profile.career_goal}'")
        
        # 1. State-Space Graph Pathfinding (A* Search)
        start_state = AdvisorState(
            completed=set(profile.completed), 
            skills=set(), 
            cgpa=profile.cgpa, 
            credits=0
        )
        
        # Pull initial skills from already completed courses
        for code in profile.completed:
            match = next((c for c in self.catalog if c.code == code), None)
            if match:
                for s in match.skills:
                    start_state.skills.add(s)
                    
        target_skills = set(profile.skills_to_learn)
        trace.append(f"Step 1: Running A* Search to find shortest path to target skills {target_skills}")
        
        astar_res = CourseSearcher.run_astar(start_state, target_skills, self.catalog)
        path_codes = astar_res["path"]
        
        if not path_codes:
            trace.append("A* Search warning: No additional courses needed or path was not resolved.")
            # Fallback to scheduling all courses in catalog that are not completed
            path_courses = [c for c in self.catalog if c.code not in profile.completed]
        else:
            trace.append(f"A* Search Success: Found optimal sequence {path_codes}")
            path_courses = [next(c for c in self.catalog if c.code == code) for code in path_codes]

        # Ensure prerequisites of path courses are also scheduled (if not completed)
        extra_prereqs = []
        for pc in path_courses:
            for p in pc.prereqs:
                if p not in profile.completed and p not in [c.code for c in path_courses]:
                    match_p = next((c for c in self.catalog if c.code == p), None)
                    if match_p:
                        extra_prereqs.append(match_p)
        
        # Combine and order
        courses_to_schedule = extra_prereqs + path_courses
        # Remove duplicates preserving order
        seen = set()
        final_schedule_list = []
        for c in courses_to_schedule:
            if c.code not in seen:
                seen.add(c.code)
                final_schedule_list.append(c)

        trace.append(f"Step 2: Feeding {len(final_schedule_list)} courses to CSP Scheduler under constraints.")
        
        # 2. CSP Scheduler
        scheduler = CourseCSP(final_schedule_list, total_terms=3, max_credits=9)
        schedule = scheduler.solve()
        
        # 3. Bayesian Success & Decision Utilities
        semester_report = {}
        if schedule:
            trace.append("CSP Scheduler Success: Term assignment completed successfully.")
            for c_code, term in schedule.items():
                course_record = next(c for c in self.catalog if c.code == c_code)
                
                # Bayes Network Probability
                p_success = self.bayes.query_success_marginal(course_record, profile)
                
                # Decision Utility (MAUT)
                util, bd = self.maut.evaluate_course(course_record, profile)
                
                if term not in semester_report:
                    semester_report[term] = []
                    
                semester_report[term].append({
                    "code": c_code,
                    "title": course_record.title,
                    "credits": course_record.credits,
                    "difficulty": course_record.difficulty,
                    "success_confidence": p_success,
                    "utility": util
                })
        else:
            trace.append("CSP Scheduler Warning: Could not resolve term constraints. Generating default sequence.")
            # Fallback simple bucket allocation
            term = 1
            for idx, c in enumerate(final_schedule_list):
                term = (idx // 2) + 1
                p_success = self.bayes.query_success_marginal(c, profile)
                util, bd = self.maut.evaluate_course(c, profile)
                
                if term not in semester_report:
                    semester_report[term] = []
                semester_report[term].append({
                    "code": c.code,
                    "title": c.title,
                    "credits": c.credits,
                    "difficulty": c.difficulty,
                    "success_confidence": p_success,
                    "utility": util
                })

        # 4. Game Decision Maker (Minimax Game Selection for Term 1 immediate choice)
        term_1_options = [c for c in final_schedule_list if c.code in [r['code'] for r in semester_report.get(1, [])]]
        trace.append(f"Step 3: Simulating enrollment game for Term 1 options: {[o.code for o in term_1_options]}")
        
        game_state = AdvisingGameState(chosen=[], remaining_options=term_1_options, profile=profile, is_max=True)
        game_solver = GameDecisionMaker(self.maut)
        
        best_val, best_enrollment = game_solver.minimax_alpha_beta(
            game_state, depth=3, alpha=-float('inf'), beta=float('inf'), is_max=True
        )
        
        trace.append(f"Pipeline Completed. Recommended first enrollment course choice: '{best_enrollment}'")
        
        return {
            "trace": trace,
            "path_found": path_codes,
            "scheduler_success": schedule is not None,
            "semester_report": semester_report,
            "best_immediate_choice": best_enrollment,
            "estimated_game_utility": best_val
        }

def display_integrated_report(results: Dict):
    """Prints a beautiful summary of the integrated reasoning pipeline."""
    print("\n" + "=" * 70)
    print("  INTEGRATED ACADEMIC ADVISING REPORT (CO1-CO6 SYSTEM PIPELINE)")
    print("=" * 70)
    
    print("  [Step-by-Step AI Execution Trace]")
    for line in results["trace"]:
        print(f"   * {line}")
    print("-" * 70)
    
    print("  SEMESTER-BY-SEMESTER ACADEMIC PLAN")
    print("-" * 70)
    
    for term in sorted(results["semester_report"].keys()):
        term_courses = results["semester_report"][term]
        total_credits = sum(c['credits'] for c in term_courses)
        print(f"  TERM {term} ({total_credits} Credits):")
        print(f"    {'Code':<7} | {'Course Title':<28} | {'Cr':<2} | {'Diff':<4} | {'Success%':<8} | {'Utility'}")
        print(f"    {'-'*7} | {'-'*28} | {'-'*2} | {'-'*4} | {'-'*8} | {'-'*7}")
        for c in term_courses:
            print(f"    {c['code']:<7} | {c['title']:<28} | {c['credits']:<2} | {c['difficulty']:<4.1f} | {c['success_confidence']:<8.2%} | {c['utility']:.3f}")
        print()
        
    print("-" * 70)
    print("  AI DECISION RECOMMENDATION SUMMARY")
    print("-" * 70)
    print(f"  Optimal Target Path: {' -> '.join(results['path_found']) if results['path_found'] else 'None'}")
    print(f"  Immediate Choice for Term 1 Enrollment: {results['best_immediate_choice']}")
    print(f"  Predicted Choice Game Utility Score  : {results['estimated_game_utility']:.3f}")
    print("=" * 70 + "\n")
