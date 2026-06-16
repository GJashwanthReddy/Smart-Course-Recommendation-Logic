"""
=============================================================
WEB_APP: PyScript Web Interface Controller
=============================================================
Binds DOM elements, runs Python solvers, and updates HTML output panels.
=============================================================
"""

from js import document
from pyscript import when
from modules.formulation import CourseRecord, CandidateProfile, AdvisorState, PrereqGraph
from modules.search_logic import CourseSearcher
from modules.csp_scheduler import CourseCSP
from modules.decision_making import CourseMAUT, GameDecisionMaker, AdvisingGameState
from modules.bayes_network import SuccessNetwork
from modules.integrated_advisor import IntegratedAdvisorPipeline
from modules.console_ui import DEFAULT_CATALOG

catalog = DEFAULT_CATALOG
maut = CourseMAUT()
bayes = SuccessNetwork()
pipeline = IntegratedAdvisorPipeline(catalog)

# Terminal logging helper
def log_terminal(msg: str, msg_type: str = "info"):
    logs_div = document.getElementById("terminal-logs")
    line = document.createElement("div")
    line.className = f"trace-line {msg_type}"
    line.innerText = msg
    logs_div.appendChild(line)
    logs_div.scrollTop = logs_div.scrollHeight

def clear_terminal():
    document.getElementById("terminal-logs").innerHTML = ""

# Read Student Profile from UI inputs
def get_ui_profile() -> CandidateProfile:
    cgpa = float(document.getElementById("student-cgpa").value)
    career_goal = document.getElementById("career-goal").value
    
    # Completed Courses checkboxes
    completed = []
    for cb in document.querySelectorAll("#completed-list input[type='checkbox']"):
        if cb.checked:
            completed.append(cb.value)
            
    # Skills to Acquire checkboxes
    skills = []
    for sb in document.querySelectorAll("#skills-list input[type='checkbox']"):
        if sb.checked:
            skills.append(sb.value)
            
    # Map career goal to interests keywords
    interests = ["Programming", "Algorithms"]
    if "AI" in career_goal or "Intelligence" in career_goal:
        interests += ["Search", "Logic", "Machine Learning"]
    elif "Fullstack" in career_goal or "Web" in career_goal:
        interests += ["Web Development", "Database", "JavaScript"]
    elif "Database" in career_goal:
        interests += ["SQL", "Database Systems", "Modeling"]
    elif "Cloud" in career_goal or "DevOps" in career_goal:
        interests += ["Docker", "Cloud", "CI/CD", "AWS"]

    return CandidateProfile(
        cgpa=cgpa,
        completed=completed,
        interests=interests,
        skills_to_learn=skills,
        career_goal=career_goal
    )

# Event Listeners
@when("input", "#student-cgpa")
def update_cgpa_label(event):
    document.getElementById("cgpa-val").innerText = event.target.value

@when("click", ".tab-btn")
def switch_tab(event):
    target_id = event.target.getAttribute("data-tab")
    
    # Toggle active class on buttons
    for btn in document.querySelectorAll(".tab-btn"):
        btn.classList.remove("active")
    event.target.classList.add("active")
    
    # Toggle active class on content divs
    for content in document.querySelectorAll(".tab-content"):
        content.classList.remove("active")
    document.getElementById(target_id).classList.add("active")

@when("click", "#btn-pipeline")
def run_integrated_pipeline(event):
    clear_terminal()
    log_terminal("[Pipeline] Reading UI student profile...", "info")
    profile = get_ui_profile()
    
    log_terminal(f"[Pipeline] Goal: '{profile.career_goal}', CGPA: {profile.cgpa}", "info")
    log_terminal(f"[Pipeline] Completed: {profile.completed}", "info")
    log_terminal(f"[Pipeline] Target Skills: {profile.skills_to_learn}", "info")
    
    # Execute advisor pipeline
    res = pipeline.execute_pipeline(profile)
    
    # Print pipeline trace to terminal logs
    for line in res["trace"]:
        if "Success" in line or "Completed" in line:
            log_terminal(f" * {line}", "success")
        elif "warning" in line.lower() or "fail" in line.lower():
            log_terminal(f" * {line}", "warning")
        else:
            log_terminal(f" * {line}", "info")
            
    # Render Dashboard HTML results
    container = document.getElementById("dashboard-results")
    
    path_html = ""
    if res["path_found"]:
        steps = [f'<span class="path-step">{code}</span>' for code in res["path_found"]]
        path_html = f"""
        <div style="background: rgba(255,255,255,0.02); padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; border: 1px solid rgba(255,255,255,0.05);">
            <h4 style="font-size: 0.95rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 0.5rem;">A* Pathfinding Sequence to Target Skills:</h4>
            <div class="path-flow">
                {' <span class="path-connector">➔</span> '.join(steps)}
            </div>
        </div>
        """
        
    term_cards_html = ""
    for term in sorted(res["semester_report"].keys()):
        term_courses = res["semester_report"][term]
        total_credits = sum(c['credits'] for c in term_courses)
        
        course_items_html = ""
        for c in term_courses:
            course_items_html += f"""
            <div class="course-item">
                <div class="course-code-title">
                    <span class="course-code">{c['code']}</span>
                    <span style="font-weight: 500;">{c['title']}</span>
                </div>
                <div class="course-meta">
                    <span>{c['credits']} Credits | Diff: {c['difficulty']}</span>
                    <span>Confidence: <span class="confidence-val">{c['success_confidence']:.1%}</span></span>
                </div>
            </div>
            """
            
        term_cards_html += f"""
        <div class="term-card">
            <div class="term-header">
                <span class="term-title">Semester Term {term}</span>
                <span class="term-credits-badge">{total_credits} Credits</span>
            </div>
            <div class="term-course-list">
                {course_items_html}
            </div>
        </div>
        """
        
    recommendation_html = f"""
    <div class="glass-panel" style="margin-top: 1.5rem; border-left: 4px solid var(--accent-cyan); background: rgba(6, 182, 212, 0.03);">
        <h3 style="color: var(--accent-cyan); font-size: 1.15rem; margin-bottom: 0.5rem; font-weight: 600;">Immediate Advisor Recommendation</h3>
        <p style="font-size: 0.95rem; color: var(--text-primary);">
            To optimize your path towards becoming an <b>{profile.career_goal}</b>, your best immediate choice for term enrollment is 
            <span style="background: var(--grad-indigo-purple); padding: 0.2rem 0.6rem; border-radius: 6px; font-weight: 600; color: #fff;">{res['best_immediate_choice']}</span>.
            The predicted choice utility score is <b>{res['estimated_game_utility']:.3f}</b>.
        </p>
    </div>
    """
    
    container.innerHTML = f"""
        <h3 style="margin-bottom: 1rem; font-size: 1.2rem; font-weight: 600; color: #ffffff;">Term-by-Term Recommended Plan</h3>
        {path_html}
        <div class="schedule-grid">
            {term_cards_html}
        </div>
        {recommendation_html}
    """
    log_terminal("[Pipeline] Done. Dashboard results rendered.", "success")

@when("click", "#btn-search")
def run_search_comparer(event):
    clear_terminal()
    log_terminal("[Search] Reading UI student profile...", "info")
    profile = get_ui_profile()
    
    start_state = AdvisorState(
        completed=set(profile.completed),
        skills=set(),
        cgpa=profile.cgpa,
        credits=0
    )
    for code in profile.completed:
        match = next((c for c in catalog if c.code == code), None)
        if match:
            for s in match.skills:
                start_state.skills.add(s)
                
    target_skills = set(profile.skills_to_learn)
    if not target_skills:
        log_terminal("[Search Error] Please select at least one skill to acquire.", "warning")
        document.getElementById("search-results").innerHTML = "<p style='color: var(--accent-rose);'>Error: Please select at least one skill to acquire on the left.</p>"
        return

    log_terminal(f"[Search] Running BFS, DFS, UCS, A* paths to skills: {list(target_skills)}...", "info")
    
    # Runs comparison
    runs = [
        CourseSearcher.run_bfs(start_state, target_skills, catalog),
        CourseSearcher.run_dfs(start_state, target_skills, catalog),
        CourseSearcher.run_ucs(start_state, target_skills, catalog),
        CourseSearcher.run_astar(start_state, target_skills, catalog)
    ]
    
    table_rows = ""
    for r in runs:
        path_str = " ──> ".join(r['path']) if r['path'] else "No Path Found"
        table_rows += f"""
        <tr>
            <td style="font-weight: 600; color: var(--accent-indigo);">{r['method']}</td>
            <td><span style="padding: 0.15rem 0.4rem; border-radius: 4px; font-size: 0.8rem; background: rgba(255,255,255,0.05);">{r['outcome']}</span></td>
            <td>{r['expanded']}</td>
            <td>{r['total_cost']:.1f}</td>
            <td>{r['runtime_ms']:.3f} ms</td>
            <td style="font-family: monospace; font-size: 0.8rem; max-width: 250px; overflow-x: auto;">{path_str}</td>
        </tr>
        """
        log_terminal(f"[{r['method']}] Expanded: {r['expanded']}, Runtime: {r['runtime_ms']:.3f}ms, Cost: {r['total_cost']:.1f}", "info")
        
    html = f"""
    <table class="styled-table">
        <thead>
            <tr>
                <th>Algorithm</th>
                <th>Status</th>
                <th>Nodes Expanded</th>
                <th>Workload Cost</th>
                <th>Time (ms)</th>
                <th>Resolved Path</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    <div style="margin-top: 1.5rem; font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6;">
        <p><b>Heuristic Guidance:</b> A* Search uses an admissible skill utility cost heuristic: <i>h(n) = (missing_skills / max_skills) * min_difficulty</i>. This guarantees finding the path with the lowest overall workload difficulty.</p>
    </div>
    """
    
    document.getElementById("search-results").innerHTML = html
    log_terminal("[Search] Benchmark complete.", "success")

@when("click", "#btn-scheduler")
def run_csp_scheduler(event):
    clear_terminal()
    log_terminal("[CSP] Reading UI completed courses and catalog...", "info")
    profile = get_ui_profile()
    
    # We want to schedule the remaining catalog courses
    remaining_courses = [c for c in catalog if c.code not in profile.completed]
    if not remaining_courses:
        log_terminal("[CSP Error] All catalog courses are already completed.", "warning")
        return
        
    log_terminal(f"[CSP] Scheduling {len(remaining_courses)} courses to 3 semesters...", "info")
    
    scheduler = CourseCSP(remaining_courses, total_terms=3, max_credits=8)
    schedule = scheduler.solve()
    
    for log in scheduler.trace_logs[:15]:
        log_terminal(log, "info")
    if len(scheduler.trace_logs) > 15:
        log_terminal(f"... [Truncated {len(scheduler.trace_logs)-15} lines of backtracking steps] ...", "info")
        log_terminal(scheduler.trace_logs[-1], "success" if schedule else "warning")

@when("click", "#btn-decision")
def run_decision_engine(event):
    clear_terminal()
    log_terminal("[Decision] Running Multi-Attribute Utility scores...", "info")
    profile = get_ui_profile()
    
    # MAUT Scored list
    scored = []
    for c in catalog:
        util, bd = maut.evaluate_course(c, profile)
        scored.append((c, util, bd))
    scored.sort(key=lambda x: x[1], reverse=True)
    
    rows = ""
    for c, util, bd in scored:
        rows += f"""
        <tr>
            <td style="font-weight: 600; color: #ffffff;">{c.code}</td>
            <td>{c.title}</td>
            <td style="font-weight: 600; color: var(--accent-cyan);">{util:.3f}</td>
            <td>{bd['skills']:.2f}</td>
            <td>{bd['interests']:.2f}</td>
            <td>{bd['difficulty']:.2f}</td>
        </tr>
        """
        
    # Minimax Alpha-Beta game simulation
    log_terminal("[Decision] Simulating 3-depth Minimax enrollment choices...", "info")
    game_state = AdvisingGameState(chosen=[], remaining_options=catalog, profile=profile, is_max=True)
    pruner = GameDecisionMaker(maut)
    best_val, best_choice = pruner.minimax_alpha_beta(game_state, depth=3, alpha=-float('inf'), beta=float('inf'), is_max=True)
    
    for log in pruner.pruning_logs[:10]:
        log_terminal(log, "info")
        
    log_terminal(f"[Decision] Optimal recommended enrollment choice: '{best_choice}' (Game Score: {best_val:.3f})", "success")
    
    html = f"""
    <div style="margin-bottom: 2rem;">
        <h4 style="margin-bottom: 0.5rem; font-size: 0.95rem; color: var(--text-secondary);">Course Preference Utility Breakdown (MAUT):</h4>
        <table class="styled-table">
            <thead>
                <tr>
                    <th>Code</th>
                    <th>Course Title</th>
                    <th>Total Utility</th>
                    <th>Skill Match</th>
                    <th>Interest Match</th>
                    <th>Workload Fit</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
    
    <div class="glass-panel" style="border-color: var(--accent-purple); background: rgba(168, 85, 247, 0.03);">
        <h4 style="color: var(--accent-purple); font-weight: 600; margin-bottom: 0.5rem;">Minimax Game-Theoretic Choice</h4>
        <p style="font-size: 0.9rem; line-height: 1.5;">
            The agent models student course priority selection as a game tree against potential enrollment restrictions (MIN player closing sections or shifting syllabus workload). 
            Using Alpha-Beta pruning, the search selected <b>{best_choice}</b> as the optimal course to secure in the upcoming registration window.
        </p>
        <p style="margin-top: 0.5rem; font-size: 0.85rem; color: var(--text-secondary);">
            Nodes Evaluated: {pruner.nodes_evaluated} | Pruning Actions Triggered: {pruner.prune_count}
        </p>
    </div>
    """
    
    document.getElementById("decision-results").innerHTML = html

# Static render helpers
def render_catalog():
    rows = ""
    for c in catalog:
        prereqs = ", ".join(c.prereqs) if c.prereqs else "None"
        skills = ", ".join(c.skills)
        rows += f"""
        <tr>
            <td style="font-weight: 600; color: var(--accent-indigo);">{c.code}</td>
            <td style="font-weight: 500; color: #fff;">{c.title}</td>
            <td>{c.credits}</td>
            <td>{c.difficulty}</td>
            <td>{prereqs}</td>
            <td>{skills}</td>
        </tr>
        """
        
    html = f"""
    <table class="styled-table">
        <thead>
            <tr>
                <th>Code</th>
                <th>Course Title</th>
                <th>Credits</th>
                <th>Difficulty</th>
                <th>Prerequisites</th>
                <th>Skills Taught</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    """
    document.getElementById("catalog-results").innerHTML = html

def render_graph():
    # Simple visual representation of prerequisite linkages
    edges = [
        ("CS101 (Intro to Programming)", "CS102 (Data Structures & Alg)"),
        ("CS101 (Intro to Programming)", "CS201 (Database Systems)"),
        ("CS101 (Intro to Programming)", "CS202 (Web Development)"),
        ("CS102 (Data Structures & Alg)", "CS301 (Artificial Intelligence)"),
        ("CS102 (Data Structures & Alg)", "CS302 (Machine Learning)"),
        ("CS201 (Database Systems)", "CS303 (Cloud Systems & DevOps)"),
    ]
    
    flow_items = ""
    for source, target in edges:
        flow_items += f"""
        <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 0.6rem; display: flex; align-items: center; justify-content: space-between;">
            <span style="font-weight: 500; color: var(--accent-cyan);">{source}</span>
            <span style="color: var(--text-secondary); margin: 0 1rem;">─── Prerequisite For ───▶</span>
            <span style="font-weight: 500; color: var(--accent-purple);">{target}</span>
        </div>
        """
    document.getElementById("graph-results").innerHTML = flow_items

def render_mapping():
    mappings = [
        ("CO1: Problem Formulation", "Models course pathing as a state-space transition graph, defining the PEAS framework and discrete static taxonomy.", "modules/formulation.py"),
        ("CO2: State-Space Search", "Runs comparative benchmarks (BFS, DFS, UCS, A*) to find shortest workload paths, utilizing admissible target skill heuristics.", "modules/search_logic.py"),
        ("CO3: CSP Scheduling", "Distributes courses into semesters using backtracking search with Minimum Remaining Values (MRV) and Forward Checking domain propagation.", "modules/csp_scheduler.py"),
        ("CO4: Decision Utility & Games", "Computes Multi-Attribute utilities (MAUT) and simulates capacity blockages in a 3-depth Minimax game with Alpha-Beta pruning.", "modules/decision_making.py"),
        ("CO5: Bayesian Success Network", "Constructs a success likelihood network, running exact joint probability Inference by Enumeration based on student profile features.", "modules/bayes_network.py"),
        ("CO6: Integrated AI Pipeline", "Coordinates sequential advising flow: A* pathfinding -> CSP semester scheduling -> Bayes success confidence -> Minimax choice validation.", "modules/integrated_advisor.py"),
    ]
    
    cards = ""
    for co, desc, path in mappings:
        cards += f"""
        <div class="course-item" style="margin-bottom: 1rem; padding: 1.2rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <h4 style="color: var(--accent-indigo); font-weight: 600;">{co}</h4>
                <code style="font-size: 0.8rem; background: rgba(0,0,0,0.3); padding: 0.2rem 0.5rem; border-radius: 4px; color: var(--text-secondary);">{path}</code>
            </div>
            <p style="font-size: 0.9rem; color: var(--text-secondary);">{desc}</p>
        </div>
        """
    document.getElementById("mapping-results").innerHTML = cards

# Initialize the layout when PyScript boots up
document.getElementById("loader").style.display = "none"
document.getElementById("main-app").style.display = "grid"

render_catalog()
render_graph()
render_mapping()
log_terminal("[System Initialization] PyScript environment loaded successfully.", "success")
log_terminal("[System Initialization] Dynamic catalog, graph, and mappings populated.", "success")
