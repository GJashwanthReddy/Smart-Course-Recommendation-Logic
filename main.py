"""
=============================================================
MAIN: CLI Entry Point & Course Recommendation System Loop
=============================================================
Usage:
  python main.py
=============================================================
"""

import sys
from modules.formulation import show_peas_formulation, show_environment_dimensions, PrereqGraph
from modules.search_logic import compare_search_methods
from modules.csp_scheduler import run_scheduler_demo
from modules.decision_making import run_decision_demo
from modules.bayes_network import run_bayes_demo
from modules.integrated_advisor import IntegratedAdvisorPipeline, display_integrated_report
from modules.console_ui import (
    DEFAULT_CATALOG, 
    get_default_profile, 
    display_profile, 
    display_catalog, 
    display_ai_mapping, 
    update_profile_interactive
)

def main():
    catalog = DEFAULT_CATALOG
    profile = get_default_profile()
    
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║               SMART COURSE RECOMMENDATION ADVISOR CLI              ║")
    print("║          AI Decision-Support System for Academic Pathing           ║")
    print("╚" + "═" * 68 + "╝")
    
    display_profile(profile)

    while True:
        print("─" * 70)
        print("  MAIN MENU SELECTION")
        print("─" * 70)
        print("  [1] Problem Structuring & Agent PEAS Model (CO1)")
        print("  [2] Optimal Prerequisite Pathfinding Search (CO2)")
        print("  [3] Term-by-Term Scheduler (CO3 - CSP)")
        print("  [4] Priority Ranking & Game-Theoretic Course Matching (CO4)")
        print("  [5] Completion Likelihood Forecasting (CO5 - Bayesian Network)")
        print("  [6] Execute Full Student Advisor Pipeline (CO6)")
        print("  [7] Update Student Target Characteristics / Profile")
        print("  [8] Display Academic Course Catalog Records")
        print("  [9] View AI Theoretical Mapping")
        print("  [0] Exit")
        print("─" * 70)
        
        try:
            choice = input("  Select an option [0-9]: ").strip()
            if not choice:
                continue
            
            if choice == "1":
                show_peas_formulation()
                show_environment_dimensions()
                # Also show directed graph structures
                g = PrereqGraph(catalog)
                g.render_graph()
                
            elif choice == "2":
                print("\n  [optimal pathfinding comparing BFS, DFS, UCS, and A*]")
                target_skills = set(profile.skills_to_learn)
                # Ensure start state completed list matches student profile
                from modules.formulation import AdvisorState
                start_state = AdvisorState(
                    completed=set(profile.completed),
                    skills=set(),
                    cgpa=profile.cgpa,
                    credits=0
                )
                # Add current skills
                for code in profile.completed:
                    match = next((c for c in catalog if c.code == code), None)
                    if match:
                        for s in match.skills:
                            start_state.skills.add(s)
                            
                compare_search_methods(start_state, target_skills, catalog)
                
            elif choice == "3":
                run_scheduler_demo(catalog)
                
            elif choice == "4":
                run_decision_demo(catalog, profile)
                
            elif choice == "5":
                run_bayes_demo(catalog, profile)
                
            elif choice == "6":
                pipeline = IntegratedAdvisorPipeline(catalog)
                results = pipeline.execute_pipeline(profile)
                display_integrated_report(results)
                
            elif choice == "7":
                profile = update_profile_interactive(profile, catalog)
                
            elif choice == "8":
                display_catalog(catalog)
                
            elif choice == "9":
                display_ai_mapping()
                
            elif choice == "0":
                print("\n  Thank you for using the Smart Course Recommendation Advisor! Goodbye.\n")
                sys.exit(0)
                
            else:
                print("\n  [Error] Invalid choice. Please enter a value between 0 and 9.")
                
        except KeyboardInterrupt:
            print("\n\n  Exiting Advisor Application...")
            sys.exit(0)
        except Exception as e:
            print(f"\n  [Error] An unexpected runtime exception occurred: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
