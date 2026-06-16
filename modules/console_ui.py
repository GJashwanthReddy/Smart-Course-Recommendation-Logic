"""
=============================================================
CONSOLE_UI: Interactive Layouts & CLI UI Utilities
=============================================================
Defines:
  - Default Course Catalog Database (prereq relationships, skills, and credits)
  - Default Student Profile structure
  - Interactive profile editors (CGPA, completed courses, and career targets)
  - Academic catalog rendering in tables
  - Course Outcomes (CO1-CO6) mapping description prints
=============================================================
"""

from typing import List, Dict, Set
from .formulation import CourseRecord, CandidateProfile

# Default catalog representing an undergraduate computer science program
DEFAULT_CATALOG = [
    CourseRecord(
        code="CS101",
        title="Intro to Programming",
        category="Core",
        credits=3,
        difficulty=2.0,
        skills=["Programming", "Logic"],
        prereqs=[],
        description="Fundamental coding concepts, variables, loops, arrays, and basic functions."
    ),
    CourseRecord(
        code="CS102",
        title="Data Structures & Alg",
        category="Core",
        credits=4,
        difficulty=3.5,
        skills=["Algorithms", "Complexity"],
        prereqs=["CS101"],
        description="Stacks, queues, trees, graphs, search/sorting, and big-O analysis."
    ),
    CourseRecord(
        code="CS201",
        title="Database Systems",
        category="Core",
        credits=3,
        difficulty=3.0,
        skills=["SQL", "Data Modeling"],
        prereqs=["CS101"],
        description="Relational database schemas, normalization, transactions, and SQL queries."
    ),
    CourseRecord(
        code="CS202",
        title="Web Development",
        category="Elective",
        credits=3,
        difficulty=2.5,
        skills=["HTML", "CSS", "JavaScript"],
        prereqs=["CS101"],
        description="Client-side rendering, server-side scripts, and fullstack frameworks."
    ),
    CourseRecord(
        code="CS301",
        title="Artificial Intelligence",
        category="Specialization",
        credits=4,
        difficulty=4.5,
        skills=["Search", "Reasoning", "Probabilistic ML"],
        prereqs=["CS102"],
        description="State-space pathfinding, CSP scheduling, games, and Bayesian nets."
    ),
    CourseRecord(
        code="CS302",
        title="Machine Learning",
        category="Specialization",
        credits=4,
        difficulty=4.8,
        skills=["Regression", "Neural Networks"],
        prereqs=["CS102"],
        description="Supervised and unsupervised models, optimization, and deep learning."
    ),
    CourseRecord(
        code="CS303",
        title="Cloud Systems & DevOps",
        category="Elective",
        credits=3,
        difficulty=3.8,
        skills=["Docker", "AWS", "CI/CD"],
        prereqs=["CS201"],
        description="Container orchestration, virtual machines, cloud microservices, and deployments."
    )
]

# Default Student Profile structure
def get_default_profile() -> CandidateProfile:
    return CandidateProfile(
        cgpa=8.2,
        completed=["CS101"],
        interests=["Algorithms", "Search", "Logic"],
        skills_to_learn=["Search", "Reasoning", "Probabilistic ML"],
        career_goal="Artificial Intelligence Engineer"
    )

def display_profile(profile: CandidateProfile):
    """Prints student profile with standard console framing."""
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + "             CURRENT STUDENT CANDIDATE PROFILE            " + "║")
    print("╠" + "═" * 58 + "╣")
    print(f"║  Target Career Goal: {profile.career_goal:<36} ║")
    print(f"║  Current CGPA      : {profile.cgpa:<36.2f} ║")
    print(f"║  Completed Courses : {', '.join(profile.completed):<36} ║")
    print(f"║  Student Interests : {', '.join(profile.interests):<36} ║")
    print(f"║  Skills to Acquire : {', '.join(profile.skills_to_learn):<36} ║")
    print("╚" + "═" * 58 + "╝\n")

def display_catalog(catalog: List[CourseRecord]):
    """Prints the academic course catalog in a nice grid format."""
    print("\n" + "═" * 80)
    print("  ACADEMIC COURSE CATALOG DATABASE")
    print("═" * 80)
    print(f"  {'Code':<7} | {'Course Title':<23} | {'Credits':<7} | {'Diff':<4} | {'Prerequisites':<15} | {'Skills Taught'}")
    print(f"  {'-'*7} | {'-'*23} | {'-'*7} | {'-'*4} | {'-'*15} | {'-'*20}")
    for c in catalog:
        prereqs_str = ", ".join(c.prereqs) if c.prereqs else "None"
        skills_str = ", ".join(c.skills)
        print(f"  {c.code:<7} | {c.title:<23} | {c.credits:<7} | {c.difficulty:<4.1f} | {prereqs_str:<15} | {skills_str}")
    print("═" * 80 + "\n")

def display_ai_mapping():
    """Prints how the course outcomes map to specific program files."""
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║                  AI THEORETICAL COURSE OUTCOMES MAPPING            ║")
    print("╠" + "═" * 68 + "╣")
    print("║  Outcome (CO) | AI Concept Covered       | Program Module Location ║")
    print("╠" + "═" * 68 + "╣")
    print("║  CO1          | Problem Formulation/PEAS | modules/formulation.py  ║")
    print("║  CO2          | BFS/DFS/UCS/A* Searching | modules/search_logic.py ║")
    print("║  CO3          | CSP MRV Forward Checking | modules/csp_scheduler.py║")
    print("║  CO4          | MAUT & Minimax AlphaBeta | modules/decision_making ║")
    print("║  CO5          | Bayesian Network Joint P | modules/bayes_network.py║")
    print("║  CO6          | Integrated System Pipeline| modules/integrated_advisor║")
    print("╚" + "═" * 68 + "╝\n")

def update_profile_interactive(profile: CandidateProfile, catalog: List[CourseRecord]) -> CandidateProfile:
    """Provides console prompts to update student criteria."""
    print("\n" + "─" * 60)
    print("  UPDATE STUDENT TARGET CHARACTERISTICS")
    print("─" * 60)
    
    # 1. Update CGPA
    try:
        cgpa_in = input(f"  Enter Cumulative CGPA [current: {profile.cgpa}]: ").strip()
        if cgpa_in:
            val = float(cgpa_in)
            if 0.0 <= val <= 10.0:
                profile.cgpa = val
            else:
                print("  [Error] CGPA must be between 0.0 and 10.0. Skipping.")
    except ValueError:
        print("  [Error] Invalid float. Skipping.")

    # 2. Update Career Goal
    goal_in = input(f"  Enter Career Goal [current: '{profile.career_goal}']: ").strip()
    if goal_in:
        profile.career_goal = goal_in

    # 3. Update Completed Courses
    all_codes = {c.code for c in catalog}
    comp_in = input(f"  Enter completed courses (comma-separated) [current: {', '.join(profile.completed)}]: ").strip()
    if comp_in:
        codes = [c.strip().upper() for c in comp_in.split(",")]
        valid_codes = [c for c in codes if c in all_codes]
        profile.completed = valid_codes
        print(f"  [Update] Completed list set to: {valid_codes}")

    # 4. Update Interests
    int_in = input(f"  Enter academic interest keywords (comma-separated) [current: {', '.join(profile.interests)}]: ").strip()
    if int_in:
        interests = [i.strip() for i in int_in.split(",")]
        profile.interests = interests

    # 5. Update Target Skills
    skills_in = input(f"  Enter target skills to learn (comma-separated) [current: {', '.join(profile.skills_to_learn)}]: ").strip()
    if skills_in:
        skills = [s.strip() for s in skills_in.split(",")]
        profile.skills_to_learn = skills

    print("\n  [Success] Student characteristics updated successfully.")
    display_profile(profile)
    return profile
