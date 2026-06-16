"""
=============================================================
SEARCH_LOGIC: Optimal Prerequisite Pathfinding
=============================================================
Implements:
  - PathNode wrapping advisor state and path transitions
  - Graph search comparison engines (BFS, DFS, UCS, A*)
  - Admissible heuristic function guided by missing target skills
  - Performance comparison analysis outputting execution time and node counts
=============================================================
"""

import time
from typing import List, Set, Dict, Tuple
from .formulation import AdvisorState, CourseRecord, transition_state, get_difficulty_cost

class PathNode:
    """Wraps State and the path of CourseRecord transitions taken to reach it."""
    def __init__(self, state: AdvisorState, path: List[CourseRecord] = None, cost: float = 0.0):
        self.state = state
        self.path = path if path else []
        self.cost = cost

class CourseSearcher:
    @staticmethod
    def get_skill_heuristic(state: AdvisorState, goal_skills: Set[str], max_skills: int, min_cost: float) -> float:
        """Admissible heuristic: h(n) = (missing skills / max skills) * minimum course difficulty."""
        missing = [s for s in goal_skills if s not in state.skills]
        if not missing or max_skills == 0:
            return 0.0
        return (len(missing) / max_skills) * min_cost

    @staticmethod
    def is_eligible(state: AdvisorState, course: CourseRecord) -> bool:
        """Verifies if prerequisites are met and course has not already been completed."""
        if course.code in state.completed:
            return False
        for p in course.prereqs:
            if p not in state.completed:
                return False
        return True

    @staticmethod
    def run_bfs(start_state: AdvisorState, target_skills: Set[str], catalog: List[CourseRecord]) -> Dict:
        start_time = time.perf_counter()
        queue = [PathNode(start_state, [])]
        visited = set()
        nodes_expanded = 0

        while queue:
            node = queue.pop(0)
            goal_met = all(s in node.state.skills for s in target_skills)
            if goal_met:
                return {
                    "method": "BFS (Breadth-First)",
                    "path": [c.code for c in node.path],
                    "total_cost": sum(c.difficulty for c in node.path),
                    "expanded": nodes_expanded,
                    "runtime_ms": (time.perf_counter() - start_time) * 1000.0,
                    "outcome": "Success"
                }

            state_key = ",".join(sorted(list(node.state.completed)))
            if state_key in visited:
                continue
            visited.add(state_key)
            nodes_expanded += 1

            if nodes_expanded > 500:
                break

            for c in catalog:
                if CourseSearcher.is_eligible(node.state, c):
                    next_state = transition_state(node.state, c)
                    queue.append(PathNode(next_state, node.path + [c]))

        return {
            "method": "BFS (Breadth-First)",
            "path": [],
            "total_cost": 0.0,
            "expanded": nodes_expanded,
            "runtime_ms": (time.perf_counter() - start_time) * 1000.0,
            "outcome": "No Path Found"
        }

    @staticmethod
    def run_dfs(start_state: AdvisorState, target_skills: Set[str], catalog: List[CourseRecord]) -> Dict:
        start_time = time.perf_counter()
        stack = [PathNode(start_state, [])]
        visited = set()
        nodes_expanded = 0

        while stack:
            node = stack.pop()
            goal_met = all(s in node.state.skills for s in target_skills)
            if goal_met:
                return {
                    "method": "DFS (Depth-First)",
                    "path": [c.code for c in node.path],
                    "total_cost": sum(c.difficulty for c in node.path),
                    "expanded": nodes_expanded,
                    "runtime_ms": (time.perf_counter() - start_time) * 1000.0,
                    "outcome": "Success"
                }

            state_key = ",".join(sorted(list(node.state.completed)))
            if state_key in visited:
                continue
            visited.add(state_key)
            nodes_expanded += 1

            if nodes_expanded > 500:
                break

            # Process reverse to expand first listed course first in stack
            for c in reversed(catalog):
                if CourseSearcher.is_eligible(node.state, c):
                    next_state = transition_state(node.state, c)
                    stack.append(PathNode(next_state, node.path + [c]))

        return {
            "method": "DFS (Depth-First)",
            "path": [],
            "total_cost": 0.0,
            "expanded": nodes_expanded,
            "runtime_ms": (time.perf_counter() - start_time) * 1000.0,
            "outcome": "No Path Found"
        }

    @staticmethod
    def run_ucs(start_state: AdvisorState, target_skills: Set[str], catalog: List[CourseRecord]) -> Dict:
        start_time = time.perf_counter()
        open_list = [PathNode(start_state, [], 0.0)]
        visited = set()
        nodes_expanded = 0

        while open_list:
            open_list.sort(key=lambda x: x.cost)
            node = open_list.pop(0)

            goal_met = all(s in node.state.skills for s in target_skills)
            if goal_met:
                return {
                    "method": "UCS (Uniform Cost / Dijkstra)",
                    "path": [c.code for c in node.path],
                    "total_cost": node.cost,
                    "expanded": nodes_expanded,
                    "runtime_ms": (time.perf_counter() - start_time) * 1000.0,
                    "outcome": "Success"
                }

            state_key = ",".join(sorted(list(node.state.completed)))
            if state_key in visited:
                continue
            visited.add(state_key)
            nodes_expanded += 1

            if nodes_expanded > 500:
                break

            for c in catalog:
                if CourseSearcher.is_eligible(node.state, c):
                    next_state = transition_state(node.state, c)
                    step_cost = get_difficulty_cost(c)
                    open_list.append(PathNode(next_state, node.path + [c], node.cost + step_cost))

        return {
            "method": "UCS (Uniform Cost / Dijkstra)",
            "path": [],
            "total_cost": 0.0,
            "expanded": nodes_expanded,
            "runtime_ms": (time.perf_counter() - start_time) * 1000.0,
            "outcome": "No Path Found"
        }

    @staticmethod
    def run_astar(start_state: AdvisorState, target_skills: Set[str], catalog: List[CourseRecord]) -> Dict:
        start_time = time.perf_counter()
        
        max_skills = 1
        min_cost = 5.0
        for c in catalog:
            s_count = len(c.skills)
            if s_count > max_skills:
                max_skills = s_count
            if c.difficulty < min_cost:
                min_cost = c.difficulty

        h_init = CourseSearcher.get_skill_heuristic(start_state, target_skills, max_skills, min_cost)
        open_list = [(h_init, 0.0, PathNode(start_state, [], 0.0))]
        visited = set()
        nodes_expanded = 0

        while open_list:
            open_list.sort(key=lambda x: x[0])
            f_val, g_val, node = open_list.pop(0)

            goal_met = all(s in node.state.skills for s in target_skills)
            if goal_met:
                return {
                    "method": "A* Search (Heuristic)",
                    "path": [c.code for c in node.path],
                    "total_cost": node.cost,
                    "expanded": nodes_expanded,
                    "runtime_ms": (time.perf_counter() - start_time) * 1000.0,
                    "outcome": "Success"
                }

            state_key = ",".join(sorted(list(node.state.completed)))
            if state_key in visited:
                continue
            visited.add(state_key)
            nodes_expanded += 1

            if nodes_expanded > 500:
                break

            for c in catalog:
                if CourseSearcher.is_eligible(node.state, c):
                    next_state = transition_state(node.state, c)
                    step_cost = get_difficulty_cost(c)
                    g_next = node.cost + step_cost
                    h_next = CourseSearcher.get_skill_heuristic(next_state, target_skills, max_skills, min_cost)
                    f_next = g_next + h_next
                    open_list.append((f_next, g_next, PathNode(next_state, node.path + [c], g_next)))

        return {
            "method": "A* Search (Heuristic)",
            "path": [],
            "total_cost": 0.0,
            "expanded": nodes_expanded,
            "runtime_ms": (time.perf_counter() - start_time) * 1000.0,
            "outcome": "No Path Found"
        }

def compare_search_methods(start_state: AdvisorState, target_skills: Set[str], catalog: List[CourseRecord]):
    """Runs all searches and prints performance comparisons side-by-side."""
    print("\n" + "=" * 70)
    print("  SEARCH COMPARATIVE METRICS (Pathfinding to Skill Goal)")
    print("=" * 70)
    print(f"  Target Goal Skills: {', '.join(target_skills)}")
    print("-" * 70)
    
    runs = [
        CourseSearcher.run_bfs(start_state, target_skills, catalog),
        CourseSearcher.run_dfs(start_state, target_skills, catalog),
        CourseSearcher.run_ucs(start_state, target_skills, catalog),
        CourseSearcher.run_astar(start_state, target_skills, catalog)
    ]
    
    print(f"  {'Algorithm':<28} | {'Status':<10} | {'Nodes':<5} | {'Cost':<6} | {'Time (ms)'}")
    print(f"  {'-'*28} | {'-'*10} | {'-'*5} | {'-'*6} | {'-'*9}")
    
    for r in runs:
        print(f"  {r['method']:<28} | {r['outcome']:<10} | {r['expanded']:<5} | {r['total_cost']:<6.1f} | {r['runtime_ms']:.3f} ms")
    print()
    
    # Print path trace of A*
    astar_res = runs[3]
    if astar_res["path"]:
        print(f"  A* Optimal Course Chain: {' ──> '.join(astar_res['path'])}")
    else:
        print("  A* pathfinder could not construct a valid sequence.")
    print()
