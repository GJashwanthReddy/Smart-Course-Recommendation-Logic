"""
=============================================================
FORMULATION: AI Problem Formulation & Representation
=============================================================
Defines:
  - PEAS Agent Model for Course Planning
  - AI Environment Classification Taxonomy
  - Dataclasses representing courses, student profile, and advisor state
  - Transition models and cost functions
  - Directed prerequisite graphs
=============================================================
"""

from dataclasses import dataclass
from typing import List, Set, Dict

# PEAS Model Representation
def show_peas_formulation():
    """Prints the PEAS model characteristics of the advising agent."""
    print("\n" + "#" * 60)
    # Changed header style and spacing
    print("  AGENT SPECIFICATION: PEAS DESCRIPTIVE MATRIX")
    print("#" * 60)
    print("""
  [Performance Criteria]
  - Graduation / Completion Speed (Fewer semesters)
  - Interest-Match Utility Maximization
  - Prerequisite Ordering Compliance
  - Credit Allocation Efficiency (Credit load <= 8/sem)

  [Environment Features]
  - Course curriculum records
  - Prerequisite graphs
  - Student CGPA and completed list
  - Difficulty indexes and learning categories

  [Actuators (Outputs)]
  - Recommending course nodes
  - Creating semester schedules
  - Resolving academic path conflicts

  [Sensors (Inputs)]
  - Student interests list (input text)
  - Completed courses records
  - CGPA and targeted skills
    """)

# Environment Types Classification
def show_environment_dimensions():
    """Prints the environmental properties classification table."""
    print("\n" + "=" * 60)
    print("  ACADEMIC ENVIRONMENT PROPERTIES CLASSIFICATION")
    print("=" * 60)
    dimensions = [
        ("Observable Scope",    "Partially Observable", "The agent has no vision of future elective catalog changes"),
        ("Determinism",         "Stochastic",           "Predicting grade outcomes based on difficulty has uncertainty"),
        ("Temporality",         "Sequential",           "Selecting a course now impacts prerequisite state later"),
        ("Dynamism",            "Static",               "Catalog rules are fixed; student profile is modified"),
        ("Continuity",          "Discrete",             "Distinct course choices, semesters, and credits"),
        ("Agent Count",         "Single/Multi-Agent",   "Advising runs individually but competes for course capacity"),
    ]
    print(f"  {'Dimension':<20} | {'Classification':<22} | {'Brief rationale'}")
    print(f"  {'-'*20} | {'-'*22} | {'-'*25}")
    for dim, cls, desc in dimensions:
        print(f"  {dim:<20} | {cls:<22} | {desc}")
    print()

# Dataclasses
@dataclass
class CourseRecord:
    """Represents a curriculum course offering."""
    code: str
    title: str
    category: str
    credits: int
    difficulty: float
    skills: List[str]
    prereqs: List[str]
    description: str

@dataclass
class CandidateProfile:
    """Represents the student profile inputs."""
    cgpa: float
    completed: List[str]
    interests: List[str]
    skills_to_learn: List[str]
    career_goal: str

class AdvisorState:
    """Represents the search node state in graph planning."""
    def __init__(self, completed: Set[str] = None, skills: Set[str] = None, cgpa: float = 8.0, credits: int = 0):
        self.completed = completed if completed else set()
        self.skills = skills if skills else set()
        self.cgpa = float(cgpa)
        self.credits = int(credits)

    def replicate(self):
        """Creates a deep copy of the advisor state."""
        return AdvisorState(set(self.completed), set(self.skills), self.cgpa, self.credits)

    def extract_dict(self):
        """Formats the state into a dictionary for traces."""
        return {
            "completed": list(self.completed),
            "skills": list(self.skills),
            "cgpa": round(self.cgpa, 2),
            "credits": self.credits
        }

# Transition Model & Cost Function
def transition_state(current: AdvisorState, course: CourseRecord) -> AdvisorState:
    """Transition function: applies taking a course to the current state."""
    nxt = current.replicate()
    nxt.completed.add(course.code)
    for s in course.skills:
        nxt.skills.add(s)
    nxt.credits += course.credits
    
    # Recalculate CGPA (simulate penalty based on course difficulty)
    predicted_grade = 8.5
    penalty = max(0.0, (course.difficulty - 2.5) * 0.4)
    predicted_grade = max(5.0, min(10.0, predicted_grade - penalty))
    
    nxt.cgpa = (current.cgpa * current.credits + predicted_grade * course.credits) / nxt.credits
    return nxt

def get_difficulty_cost(course: CourseRecord) -> float:
    """Cost function: returns difficulty-based path cost."""
    return float(course.difficulty)

# Graph representation
class PrereqGraph:
    """Builds and logs a directed prerequisite graph representation."""
    def __init__(self, catalog: List[CourseRecord]):
        self.adj_list: Dict[str, List[str]] = {}
        for c in catalog:
            self.adj_list[c.code] = []
            
        for c in catalog:
            for p in c.prereqs:
                if p in self.adj_list:
                    # Edge goes from Prerequisite -> Course
                    self.adj_list[p].append(c.code)

    def render_graph(self):
        """Displays directed graph dependencies to console."""
        print("\n" + "-" * 60)
        print("  GRAPH STRUCTURE: CURRICULUM PREREQUISITE EDGES")
        print("-" * 60)
        edge_count = 0
        for node, targets in self.adj_list.items():
            if targets:
                print(f"  [{node}] ──> {', '.join(targets)}")
                edge_count += len(targets)
            else:
                print(f"  [{node}] ──> (No successor courses)")
        print(f"\n  Total Course Vertices: {len(self.adj_list)}")
        print(f"  Total Prerequisite Edges: {edge_count}\n")
