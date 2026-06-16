"""
=============================================================
DECISION_MAKING: Attribute Utilities & Minimax Pruner
=============================================================
Implements:
  - Multi-Attribute Utility Theory (MAUT) for course scoring
  - Utility calculations balancing student interest, skill target, and difficulty
  - Game-theoretic decision making modeling course selection as a game
  - Minimax algorithm with Alpha-Beta pruning to find optimal decisions
=============================================================
"""

from typing import List, Dict, Set, Tuple, Optional
import math
from .formulation import CourseRecord, CandidateProfile

class CourseMAUT:
    """
    Ranks courses using Multi-Attribute Utility Theory (MAUT).
    Aggregates utility metrics from multiple features:
      1. Skill Utility: Alignment with target skills
      2. Interest Utility: Overlap with student interests
      3. Workload Utility: Adaptability of course difficulty to student CGPA
    """
    def __init__(self, w_skills: float = 0.4, w_interests: float = 0.4, w_difficulty: float = 0.2):
        self.w_skills = w_skills
        self.w_interests = w_interests
        self.w_difficulty = w_difficulty

    def get_skills_utility(self, course: CourseRecord, target_skills: List[str]) -> float:
        if not target_skills:
            return 1.0
        # Percentage of course skills that match student targets
        matches = sum(1 for s in course.skills if s in target_skills)
        return matches / max(1, len(course.skills))

    def get_interests_utility(self, course: CourseRecord, interests: List[str]) -> float:
        if not interests:
            return 1.0
        # Percentage of interest terms matched in course description, title, or skills
        matched = 0
        search_space = (course.title + " " + course.description + " " + " ".join(course.skills)).lower()
        for interest in interests:
            if interest.lower() in search_space:
                matched += 1
        return matched / len(interests)

    def get_difficulty_utility(self, course: CourseRecord, student_cgpa: float) -> float:
        # High CGPA students are assumed to handle/prefer challenging courses.
        # Low CGPA students are penalized for taking very difficult courses.
        # Ideal difficulty is scaled to student's CGPA (CGPA 10 -> difficulty 5.0, CGPA 6 -> difficulty 2.0)
        target_diff = (student_cgpa / 10.0) * 5.0
        diff_error = abs(course.difficulty - target_diff)
        # Normalize utility to [0.0, 1.0] where 1.0 is a perfect match
        return max(0.0, 1.0 - (diff_error / 5.0))

    def evaluate_course(self, course: CourseRecord, profile: CandidateProfile) -> Tuple[float, Dict[str, float]]:
        """Calculates total MAUT utility and returns attribute scores breakdown."""
        u_skills = self.get_skills_utility(course, profile.skills_to_learn)
        u_interests = self.get_interests_utility(course, profile.interests)
        u_difficulty = self.get_difficulty_utility(course, profile.cgpa)
        
        total_utility = (
            self.w_skills * u_skills +
            self.w_interests * u_interests +
            self.w_difficulty * u_difficulty
        )
        
        breakdown = {
            "skills": u_skills,
            "interests": u_interests,
            "difficulty": u_difficulty,
            "weighted_skills": self.w_skills * u_skills,
            "weighted_interests": self.w_interests * u_interests,
            "weighted_difficulty": self.w_difficulty * u_difficulty
        }
        return total_utility, breakdown


class AdvisingGameState:
    """Represents a game state in course scheduling decisions."""
    def __init__(self, chosen: List[str], remaining_options: List[CourseRecord], profile: CandidateProfile, is_max: bool = True):
        self.chosen = chosen
        self.remaining_options = remaining_options
        self.profile = profile
        self.is_max = is_max  # True = Student/Advisor (MAX), False = Environment Closed/Section Cap (MIN)

    def get_utility(self, evaluator: CourseMAUT) -> float:
        """Utility evaluation function for terminal leaf node states."""
        if not self.chosen:
            return 0.0
        # Calculate sum of utilities for chosen courses
        score = 0.0
        for code in self.chosen:
            # Find in remaining_options or compute ad-hoc
            match = next((c for c in self.remaining_options if c.code == code), None)
            if match:
                score += evaluator.evaluate_course(match, self.profile)[0]
            else:
                score += 0.5  # Neutral default
        return score

class GameDecisionMaker:
    """Implements Minimax decision making with Alpha-Beta pruning."""
    def __init__(self, evaluator: CourseMAUT):
        self.evaluator = evaluator
        self.pruning_logs: List[str] = []
        self.prune_count = 0
        self.nodes_evaluated = 0

    def minimax_alpha_beta(
        self, state: AdvisingGameState, depth: int, alpha: float, beta: float, is_max: bool
    ) -> Tuple[float, Optional[str]]:
        """
        Runs Minimax with Alpha-Beta pruning.
        Returns: Tuple of (utility_score, chosen_course_code)
        """
        self.nodes_evaluated += 1
        
        # Base case: max depth reached or no remaining options
        if depth == 0 or not state.remaining_options:
            return state.get_utility(self.evaluator), None

        best_choice = None
        
        if is_max:
            max_eval = -float('inf')
            # Select from top 3 available course options to limit branching
            # Sort remaining options temporarily by crude MAUT score
            sorted_options = sorted(
                state.remaining_options, 
                key=lambda x: self.evaluator.evaluate_course(x, state.profile)[0], 
                reverse=True
            )[:3]
            
            for option in sorted_options:
                next_chosen = state.chosen + [option.code]
                next_remaining = [c for c in state.remaining_options if c.code != option.code]
                next_state = AdvisingGameState(next_chosen, next_remaining, state.profile, is_max=False)
                
                evaluation, _ = self.minimax_alpha_beta(next_state, depth - 1, alpha, beta, False)
                
                if evaluation > max_eval:
                    max_eval = evaluation
                    best_choice = option.code
                    
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    self.pruning_logs.append(
                        f"  [Pruned at MAX Node] Depth: {depth}, Action: '{option.code}', Alpha: {alpha:.2f}, Beta: {beta:.2f}"
                    )
                    self.prune_count += 1
                    break
            return max_eval, best_choice
            
        else:
            # MIN player models environmental constraints (e.g. course closed, registration failures)
            # which decreases overall academic satisfaction utility
            min_eval = float('inf')
            
            # Simulated environment outcomes: 
            # 1. Normal Registration (utility unchanged)
            # 2. Section Full (penalizes path utility because student takes lower preference courses)
            # 3. Schedule Clash (larger penalty)
            outcomes = [
                ("normal", 0.0),
                ("section_full", -0.4),
                ("schedule_clash", -0.8)
            ]
            
            for outcome_name, penalty in outcomes:
                # Calculate evaluation with environmental penalty applied
                base_val = state.get_utility(self.evaluator)
                # Recurse down to let MAX choose next course under this condition
                next_state = AdvisingGameState(state.chosen, state.remaining_options, state.profile, is_max=True)
                evaluation, _ = self.minimax_alpha_beta(next_state, depth - 1, alpha, beta, True)
                evaluation += penalty
                
                if evaluation < min_eval:
                    min_eval = evaluation
                    best_choice = outcome_name
                    
                beta = min(beta, evaluation)
                if beta <= alpha:
                    self.pruning_logs.append(
                        f"  [Pruned at MIN Node] Depth: {depth}, Outcome: '{outcome_name}', Alpha: {alpha:.2f}, Beta: {beta:.2f}"
                    )
                    self.prune_count += 1
                    break
            return min_eval, best_choice

def run_decision_demo(catalog: List[CourseRecord], profile: CandidateProfile):
    """Demonstrates multi-attribute evaluations and Minimax choices with Alpha-Beta logs."""
    print("\n" + "=" * 60)
    print("  MULTI-ATTRIBUTE UTILITY THEORY (MAUT) RANKINGS")
    print("=" * 60)
    
    maut = CourseMAUT(w_skills=0.4, w_interests=0.4, w_difficulty=0.2)
    
    scored_courses = []
    for c in catalog:
        utility, breakdown = maut.evaluate_course(c, profile)
        scored_courses.append((c, utility, breakdown))
        
    # Sort by utility descending
    scored_courses.sort(key=lambda x: x[1], reverse=True)
    
    print(f"  {'Code':<7} | {'Course Title':<25} | {'Utility':<7} | {'Skills U':<8} | {'Interest U':<10} | {'Workload U'}")
    print(f"  {'-'*7} | {'-'*25} | {'-'*7} | {'-'*8} | {'-'*10} | {'-'*10}")
    for c, util, bd in scored_courses:
        print(f"  {c.code:<7} | {c.title:<25} | {util:<7.3f} | {bd['skills']:<8.2f} | {bd['interests']:<10.2f} | {bd['difficulty']:.2f}")
    print()

    print("-" * 60)
    print("  GAME-THEORETIC SELECTION: MINIMAX WITH ALPHA-BETA PRUNING")
    print("-" * 60)
    print("  (MAX: Advising Agent seeks to maximize course selection utility)")
    print("  (MIN: Environment forces slots availability/penalties)")
    print()
    
    game_state = AdvisingGameState(chosen=[], remaining_options=catalog, profile=profile, is_max=True)
    pruner = GameDecisionMaker(maut)
    
    best_val, best_action = pruner.minimax_alpha_beta(
        game_state, depth=4, alpha=-float('inf'), beta=float('inf'), is_max=True
    )
    
    print("  [Alpha-Beta Decision Logs]")
    if pruner.pruning_logs:
        for log in pruner.pruning_logs[:15]:
            print(log)
        if len(pruner.pruning_logs) > 15:
            print(f"  ... [Truncated {len(pruner.pruning_logs) - 15} pruning logs] ...")
    else:
        print("  No branches pruned during exploration (small search space).")
        
    print(f"\n  Nodes Evaluated: {pruner.nodes_evaluated}")
    print(f"  Pruning Actions Executed: {pruner.prune_count}")
    print(f"  Optimal Starting Recommendation Choice: '{best_action}' (Est. Game Utility Score: {best_val:.3f})")
    print()
