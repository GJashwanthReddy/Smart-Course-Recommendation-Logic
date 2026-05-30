/**
 * Client-Side Offline AI Engine (mock_engine.js)
 * Mirrors the Python/SQLite backend implementation to enable fully decoupled operation.
 */

// Initial Seed Courses Dataset (Matches the database exactly)
const SEED_COURSES = [
    {id: 1, code: 'CS101', title: 'Introduction to Computer Science', category: 'Software Engineering', credits: 3, difficulty: 1.5, skills_taught: 'programming,python,logic', prerequisites: '', description: 'Fundamentals of programming and logical reasoning using Python.'},
    {id: 2, code: 'CS201', title: 'Data Structures & Algorithms', category: 'Software Engineering', credits: 4, difficulty: 3.5, skills_taught: 'algorithms,data_structures,java', prerequisites: 'CS101', description: 'Advanced data organization techniques, search, sorting, and complexity analysis.'},
    {id: 3, code: 'CS301', title: 'Database Management Systems', category: 'Software Engineering', credits: 3, difficulty: 2.5, skills_taught: 'sql,databases,schema_design', prerequisites: 'CS101', description: 'Relational databases, SQL queries, transaction management, and database normalization.'},
    {id: 4, code: 'CS401', title: 'Advanced Software Engineering', category: 'Software Engineering', credits: 3, difficulty: 3.0, skills_taught: 'design_patterns,git,testing', prerequisites: 'CS201', description: 'Software development lifecycle, design patterns, and agile testing methodologies.'},
    {id: 5, code: 'AI101', title: 'Artificial Intelligence Foundations', category: 'Artificial Intelligence', credits: 3, difficulty: 2.0, skills_taught: 'ai,search_algorithms,heuristics', prerequisites: 'CS101', description: 'Introduction to AI state space representation, search algorithms, and intelligent agents.'},
    {id: 6, code: 'AI201', title: 'Machine Learning Basics', category: 'Artificial Intelligence', credits: 4, difficulty: 4.0, skills_taught: 'machine_learning,regression,classification', prerequisites: 'CS201', description: 'Supervised and unsupervised machine learning algorithms, model training, and evaluation.'},
    {id: 7, code: 'AI301', title: 'Deep Learning & Neural Networks', category: 'Artificial Intelligence', credits: 4, difficulty: 4.5, skills_taught: 'deep_learning,neural_networks,pytorch', prerequisites: 'AI201', description: 'Training deep neural networks, CNNs, RNNs, and deployment of computer vision models.'},
    {id: 8, code: 'AI401', title: 'Natural Language Processing', category: 'Artificial Intelligence', credits: 3, difficulty: 4.0, skills_taught: 'nlp,transformers,text_processing', prerequisites: 'AI201', description: 'Computational methods for processing text, sequence models, and modern transformers.'},
    {id: 9, code: 'SYS101', title: 'Computer Organization & Systems', category: 'Systems & Networks', credits: 3, difficulty: 2.5, skills_taught: 'assembly,c,architecture', prerequisites: 'CS101', description: 'Hardware-software interface, instruction sets, CPU pipeline, and assembly programming.'},
    {id: 10, code: 'SYS201', title: 'Operating Systems', category: 'Systems & Networks', credits: 4, difficulty: 3.8, skills_taught: 'concurrency,memory_management,threads', prerequisites: 'CS201,SYS101', description: 'Process management, thread safety, virtual memory, filesystems, and device drivers.'},
    {id: 11, code: 'SYS301', title: 'Computer Networks', category: 'Systems & Networks', credits: 3, difficulty: 3.0, skills_taught: 'networking,tcp_ip,security', prerequisites: 'SYS101', description: 'ISO OSI model layers, TCP/UDP sockets, routing protocols, and network design.'},
    {id: 12, code: 'THEO101', title: 'Discrete Mathematics', category: 'Theoretical CS', credits: 3, difficulty: 2.5, skills_taught: 'math,graphs,combinatorics', prerequisites: '', description: 'Sets, graphs, relations, proof techniques, combinatorics, and discrete math structures.'},
    {id: 13, code: 'THEO201', title: 'Theory of Computation', category: 'Theoretical CS', credits: 3, difficulty: 4.2, skills_taught: 'automata,computability,complexity', prerequisites: 'THEO101', description: 'Regular expressions, context-free grammars, Turing machines, and NP-completeness.'}
];

// Initialize LocalStorage Data Store
const LocalDb = {
    getCourses: function() {
        let courses = localStorage.getItem('smart_courses');
        if (!courses) {
            localStorage.setItem('smart_courses', JSON.stringify(SEED_COURSES));
            return SEED_COURSES;
        }
        return JSON.parse(courses);
    },
    saveCourses: function(courses) {
        localStorage.setItem('smart_courses', JSON.stringify(courses));
    },
    addCourse: function(course) {
        let courses = this.getCourses();
        if (courses.some(c => c.code.toUpperCase() === course.code.toUpperCase())) {
            return false;
        }
        course.id = courses.length ? Math.max(...courses.map(c => c.id)) + 1 : 1;
        courses.push(course);
        this.saveCourses(courses);
        return true;
    },
    updateCourse: function(id, updatedCourse) {
        let courses = this.getCourses();
        let idx = courses.findIndex(c => c.id === parseInt(id));
        if (idx !== -1) {
            updatedCourse.id = parseInt(id);
            courses[idx] = updatedCourse;
            this.saveCourses(courses);
            return true;
        }
        return false;
    },
    deleteCourse: function(id) {
        let courses = this.getCourses();
        courses = courses.filter(c => c.id !== parseInt(id));
        this.saveCourses(courses);
    }
};

// --- CO1: Knowledge Representation ---
class ClientState {
    constructor(completed = [], skills = [], cgpa = 8.0, credits = 0) {
        this.completed_courses = new Set(completed);
        this.acquired_skills = new Set(skills);
        this.current_cgpa = parseFloat(cgpa);
        this.total_credits = parseInt(credits);
    }

    copy() {
        return new ClientState(
            Array.from(this.completed_courses),
            Array.from(this.acquired_skills),
            this.current_cgpa,
            this.total_credits
        );
    }
    
    toDict() {
        return {
            completed_courses: Array.from(this.completed_courses),
            acquired_skills: Array.from(this.acquired_skills),
            current_cgpa: this.current_cgpa,
            total_credits: this.total_credits
        };
    }
}

// --- CO2: Search Algorithms & Heuristics ---
class SearchNode {
    constructor(state, path = [], pathCost = 0.0) {
        this.state = state;
        this.path = path;
        this.path_cost = pathCost;
    }
}

class ClientSearchEngine {
    static getHeuristic(state, targetSkills, maxSkills, minCost) {
        const missing = Array.from(targetSkills).filter(s => !state.acquired_skills.has(s));
        if (missing.length === 0 || maxSkills === 0) return 0.0;
        return (missing.length / maxSkills) * minCost;
    }

    static runBFS(initialState, targetSkills, courses) {
        let start = performance.now();
        let queue = [new SearchNode(initialState, [])];
        let visited = new Set();
        let expanded = 0;

        while (queue.length > 0) {
            let node = queue.shift();
            
            // Check Goal
            let satisfied = Array.from(targetSkills).every(s => node.state.acquired_skills.has(s));
            if (satisfied) {
                return {
                    algorithm: "BFS (Breadth-First)",
                    path: node.path,
                    cost: node.path.reduce((sum, c) => sum + parseFloat(c.difficulty), 0),
                    nodes_expanded: expanded,
                    execution_time_ms: performance.now() - start,
                    status: "Success"
                };
            }

            let key = Array.from(node.state.completed_courses).sort().join(',');
            if (visited.has(key)) continue;
            visited.add(key);
            expanded++;

            if (expanded > 500) break;

            for (let c of courses) {
                if (ClientSearchEngine.isValidAction(node.state, c)) {
                    let nextState = ClientSearchEngine.transition(node.state, c);
                    let nextPath = [...node.path, c];
                    queue.push(new SearchNode(nextState, nextPath));
                }
            }
        }
        return {
            algorithm: "BFS (Breadth-First)",
            path: [],
            cost: 0.0,
            nodes_expanded: expanded,
            execution_time_ms: performance.now() - start,
            status: "No Path Found / Bounded"
        };
    }

    static runDFS(initialState, targetSkills, courses) {
        let start = performance.now();
        let stack = [new SearchNode(initialState, [])];
        let visited = new Set();
        let expanded = 0;

        while (stack.length > 0) {
            let node = stack.pop();
            
            let satisfied = Array.from(targetSkills).every(s => node.state.acquired_skills.has(s));
            if (satisfied) {
                return {
                    algorithm: "DFS (Depth-First)",
                    path: node.path,
                    cost: node.path.reduce((sum, c) => sum + parseFloat(c.difficulty), 0),
                    nodes_expanded: expanded,
                    execution_time_ms: performance.now() - start,
                    status: "Success"
                };
            }

            let key = Array.from(node.state.completed_courses).sort().join(',');
            if (visited.has(key)) continue;
            visited.add(key);
            expanded++;

            if (expanded > 500) break;

            // Iterate backwards to match typical stack traversal ordering
            for (let i = courses.length - 1; i >= 0; i--) {
                let c = courses[i];
                if (ClientSearchEngine.isValidAction(node.state, c)) {
                    let nextState = ClientSearchEngine.transition(node.state, c);
                    let nextPath = [...node.path, c];
                    stack.push(new SearchNode(nextState, nextPath));
                }
            }
        }
        return {
            algorithm: "DFS (Depth-First)",
            path: [],
            cost: 0.0,
            nodes_expanded: expanded,
            execution_time_ms: performance.now() - start,
            status: "No Path Found / Bounded"
        };
    }

    static runUCS(initialState, targetSkills, courses) {
        let start = performance.now();
        let openList = [new SearchNode(initialState, [], 0.0)];
        let visited = new Set();
        let expanded = 0;

        while (openList.length > 0) {
            // Sort by cost ascending (priority queue emulation)
            openList.sort((a, b) => a.path_cost - b.path_cost);
            let node = openList.shift();

            let satisfied = Array.from(targetSkills).every(s => node.state.acquired_skills.has(s));
            if (satisfied) {
                return {
                    algorithm: "UCS (Uniform Cost / Dijkstra)",
                    path: node.path,
                    cost: node.path_cost,
                    nodes_expanded: expanded,
                    execution_time_ms: performance.now() - start,
                    status: "Success"
                };
            }

            let key = Array.from(node.state.completed_courses).sort().join(',');
            if (visited.has(key)) continue;
            visited.add(key);
            expanded++;

            if (expanded > 500) break;

            for (let c of courses) {
                if (ClientSearchEngine.isValidAction(node.state, c)) {
                    let nextState = ClientSearchEngine.transition(node.state, c);
                    let cost = parseFloat(c.difficulty);
                    let nextPath = [...node.path, c];
                    openList.push(new SearchNode(nextState, nextPath, node.path_cost + cost));
                }
            }
        }
        return {
            algorithm: "UCS (Uniform Cost / Dijkstra)",
            path: [],
            cost: 0.0,
            nodes_expanded: expanded,
            execution_time_ms: performance.now() - start,
            status: "No Path Found / Bounded"
        };
    }

    static runAStar(initialState, targetSkills, courses) {
        let start = performance.now();
        
        let maxSkills = 1;
        let minCost = 5.0;
        for (let c of courses) {
            let s_count = c.skills_taught.split(',').length;
            if (s_count > maxSkills) maxSkills = s_count;
            let diff = parseFloat(c.difficulty);
            if (diff < minCost) minCost = diff;
        }

        let openList = [{
            f: ClientSearchEngine.getHeuristic(initialState, targetSkills, maxSkills, minCost),
            g: 0.0,
            node: new SearchNode(initialState, [], 0.0)
        }];
        let visited = new Set();
        let expanded = 0;

        while (openList.length > 0) {
            openList.sort((a, b) => a.f - b.f);
            let item = openList.shift();
            let node = item.node;

            let satisfied = Array.from(targetSkills).every(s => node.state.acquired_skills.has(s));
            if (satisfied) {
                return {
                    algorithm: "A* Search (Heuristic)",
                    path: node.path,
                    cost: node.path_cost,
                    nodes_expanded: expanded,
                    execution_time_ms: performance.now() - start,
                    status: "Success"
                };
            }

            let key = Array.from(node.state.completed_courses).sort().join(',');
            if (visited.has(key)) continue;
            visited.add(key);
            expanded++;

            if (expanded > 500) break;

            for (let c of courses) {
                if (ClientSearchEngine.isValidAction(node.state, c)) {
                    let nextState = ClientSearchEngine.transition(node.state, c);
                    let cost = parseFloat(c.difficulty);
                    let g_next = node.path_cost + cost;
                    let h_next = ClientSearchEngine.getHeuristic(nextState, targetSkills, maxSkills, minCost);
                    let f_next = g_next + h_next;
                    let nextPath = [...node.path, c];
                    openList.push({
                        f: f_next,
                        g: g_next,
                        node: new SearchNode(nextState, nextPath, g_next)
                    });
                }
            }
        }
        return {
            algorithm: "A* Search (Heuristic)",
            path: [],
            cost: 0.0,
            nodes_expanded: expanded,
            execution_time_ms: performance.now() - start,
            status: "No Path Found / Bounded"
        };
    }

    static isValidAction(state, course) {
        if (state.completed_courses.has(course.code)) return false;
        
        let prereqs = course.prerequisites ? course.prerequisites.split(',').map(p => p.trim()) : [];
        for (let p of prereqs) {
            if (p && !state.completed_courses.has(p)) return false;
        }
        return true;
    }

    static transition(state, course) {
        let next = state.copy();
        next.completed_courses.add(course.code);
        
        course.skills_taught.split(',').forEach(s => {
            if (s.trim()) next.acquired_skills.add(s.trim());
        });
        next.total_credits += parseInt(course.credits);
        
        let predicted_grade = 8.5; // Baseline
        let difficulty = parseFloat(course.difficulty);
        let pen = Math.max(0.0, (difficulty - 2.5) * 0.4);
        predicted_grade = Math.max(5.0, Math.min(10.0, predicted_grade - pen));
        
        next.current_cgpa = (state.current_cgpa * state.total_credits + predicted_grade * parseInt(course.credits)) / next.total_credits;
        return next;
    }
}

// --- CO3: Constraint Satisfaction Course Scheduler (CSP) ---
class ClientCSPScheduler {
    constructor(codes, dataset, maxCredits = 8, maxCourses = 3) {
        this.variables = [...codes];
        this.course_data = {};
        dataset.forEach(c => {
            if (this.variables.includes(c.code)) {
                this.course_data[c.code] = c;
            }
        });
        this.max_credits = maxCredits;
        this.max_courses = maxCourses;

        // Init domains: sem 1-4
        this.domains = {};
        this.variables.forEach(v => {
            this.domains[v] = [1, 2, 3, 4];
        });

        // Dependencies
        this.successors = {};
        this.predecessors = {};
        this.variables.forEach(v => {
            this.successors[v] = [];
            this.predecessors[v] = [];
        });

        this.variables.forEach(v => {
            let prereqs = this.course_data[v].prerequisites ? this.course_data[v].prerequisites.split(',').map(p => p.trim()) : [];
            prereqs.forEach(p => {
                if (this.variables.includes(p)) {
                    this.successors[p].push(v);
                    this.predecessors[v].push(p);
                }
            });
        });
    }

    isConsistent(assignment, varName, semValue) {
        // Prereq check
        for (let pred of this.predecessors[varName]) {
            if (pred in assignment && assignment[pred] >= semValue) return false;
        }
        for (let succ of this.successors[varName]) {
            if (succ in assignment && assignment[succ] <= semValue) return false;
        }

        // Credit check
        let credits = parseInt(this.course_data[varName].credits);
        let count = 1;
        for (let v in assignment) {
            if (assignment[v] === semValue) {
                credits += parseInt(this.course_data[v].credits);
                count++;
            }
        }
        if (credits > this.max_credits || count > this.max_courses) return false;

        return true;
    }

    selectUnassignedVariable(assignment) {
        let unassigned = this.variables.filter(v => !(v in assignment));
        if (unassigned.length === 0) return null;

        // MRV
        let mrvVars = [];
        let minDom = Infinity;
        unassigned.forEach(v => {
            let sz = this.domains[v].length;
            if (sz < minDom) {
                minDom = sz;
                mrvVars = [v];
            } else if (sz === minDom) {
                mrvVars.push(v);
            }
        });

        if (mrvVars.length === 1) return mrvVars[0];

        // Degree
        let bestVar = mrvVars[0];
        let maxDegree = -1;
        mrvVars.forEach(v => {
            let deg = 0;
            let neighbors = [...this.successors[v], ...this.predecessors[v]];
            neighbors.forEach(n => {
                if (!(n in assignment)) deg++;
            });
            if (deg > maxDegree) {
                maxDegree = deg;
                bestVar = v;
            }
        });
        return bestVar;
    }

    forwardCheck(assignment, varName, semValue) {
        let pruned = {};
        for (let v of this.variables) {
            pruned[v] = [...this.domains[v]];
        }

        // Prune successors (must be > semValue)
        for (let succ of this.successors[varName]) {
            if (!(succ in assignment)) {
                pruned[succ] = pruned[succ].filter(s => s > semValue);
                if (pruned[succ].length === 0) return null;
            }
        }

        // Prune predecessors (must be < semValue)
        for (let pred of this.predecessors[varName]) {
            if (!(pred in assignment)) {
                pruned[pred] = pruned[pred].filter(p => p < semValue);
                if (pruned[pred].length === 0) return null;
            }
        }

        // Prune semesters exceeding credit capacity
        for (let sem = 1; sem <= 4; sem++) {
            let sem_credits = 0;
            let sem_courses = 0;
            for (let av in assignment) {
                if (assignment[av] === sem) {
                    sem_credits += parseInt(this.course_data[av].credits);
                    sem_courses += 1;
                }
            }

            if (sem_credits >= this.max_credits || sem_courses >= this.max_courses) {
                for (let uv of this.variables) {
                    if (!(uv in assignment) && uv !== varName) {
                        pruned[uv] = pruned[uv].filter(s => s !== sem);
                        if (pruned[uv].length === 0) return null;
                    }
                }
            } else {
                let remaining = this.max_credits - sem_credits;
                for (let uv of this.variables) {
                    if (!(uv in assignment) && uv !== varName) {
                        let req = parseInt(this.course_data[uv].credits);
                        if (req > remaining) {
                            pruned[uv] = pruned[uv].filter(s => s !== sem);
                            if (pruned[uv].length === 0) return null;
                        }
                    }
                }
            }
        }
        return pruned;
    }

    backtrack(assignment) {
        if (Object.keys(assignment).length === this.variables.length) {
            return assignment;
        }

        let varName = this.selectUnassignedVariable(assignment);
        let vals = [...this.domains[varName]];

        for (let val of vals) {
            if (this.isConsistent(assignment, varName, val)) {
                assignment[varName] = val;

                let savedDomains = this.domains;
                let pruned = this.forwardCheck(assignment, varName, val);

                if (pruned !== null) {
                    this.domains = pruned;
                    let res = this.backtrack(assignment);
                    if (res !== null) return res;
                }

                delete assignment[varName];
                this.domains = savedDomains;
            }
        }
        return null;
    }

    solve() {
        let assignment = this.backtrack({});
        if (assignment) {
            let schedule = {1: [], 2: [], 3: [], 4: []};
            for (let code in assignment) {
                schedule[assignment[code]].push(code);
            }
            return { success: true, assignments: assignment, schedule: schedule };
        }
        return { success: false, assignments: {}, schedule: {1: [], 2: [], 3: [], 4: []} };
    }
}

// --- CO4: MAUT & Minimax ---
class ClientDecisionEngine {
    static calculateUtility(course, profile) {
        // Interest match
        let interests = profile.interests.split(',').map(i => i.trim().toLowerCase()).filter(i => i);
        let desc = course.description.toLowerCase();
        let title = course.title.toLowerCase();
        let cat = course.category.toLowerCase();
        
        let intMatches = 0;
        interests.forEach(i => {
            if (desc.includes(i) || title.includes(i) || cat.includes(i)) intMatches++;
        });
        let u_int = interests.length ? (intMatches / interests.length) : 0.5;
        u_int = Math.min(1.0, u_int);

        // Skill match
        let skills = profile.skills_to_learn.split(',').map(s => s.trim().toLowerCase()).filter(s => s);
        let courseSkills = course.skills_taught.split(',').map(s => s.trim().toLowerCase()).filter(s => s);
        let skillMatches = 0;
        courseSkills.forEach(s => {
            if (skills.includes(s)) skillMatches++;
        });
        let u_skill = skills.length ? (skillMatches / skills.length) : 0.5;
        u_skill = Math.min(1.0, u_skill);

        // Career Match
        let career = profile.career_goal.toLowerCase();
        let u_career = 0.0;
        if (career) {
            let kws = career.replace('engineer','').replace('developer','').split(/\s+/).filter(k => k.length > 2);
            let matches = 0;
            kws.forEach(k => {
                if (desc.includes(k) || title.includes(k) || cat.includes(k)) matches++;
            });
            if (matches > 0 && kws.length > 0) {
                u_career = Math.min(1.0, 0.5 + 0.5 * (matches / kws.length));
            }
        }

        // Difficulty alignment
        let cgpa = parseFloat(profile.cgpa);
        let diff = parseFloat(course.difficulty);
        let u_diff = 0.5;
        if (cgpa >= 8.5) {
            u_diff = diff / 5.0;
        } else if (cgpa < 7.0) {
            u_diff = 1.0 - (diff - 1.0) / 4.0;
        } else {
            u_diff = 1.0 - Math.abs(3.0 - diff) / 2.0;
        }
        u_diff = Math.max(0.0, Math.min(1.0, u_diff));

        let total = (0.4 * u_int) + (0.25 * u_skill) + (0.25 * u_career) + (0.1 * u_diff);
        return {
            total_utility: parseFloat(total.toFixed(3)),
            breakdown: {
                interest: u_int,
                skills: u_skill,
                career: u_career,
                difficulty: u_diff
            }
        };
    }

    static runAdvisorGame(profile, courses) {
        let utilities = {};
        courses.forEach(c => {
            utilities[c.code] = ClientDecisionEngine.calculateUtility(c, profile).total_utility;
        });

        // Categorize tracks
        let tracks = {};
        courses.forEach(c => {
            if (!tracks[c.category]) tracks[c.category] = [];
            tracks[c.category].push(c);
        });

        let evals = 0;
        let prunes = 0;

        function minimax(node, depth, alpha, beta, isMax) {
            evals++;
            if (depth === 0 || (node && !Array.isArray(node) && typeof node === 'object')) {
                if (node && node.code) return { val: utilities[node.code] || 0.0, item: node };
                return { val: 0.0, item: null };
            }

            if (isMax) {
                let maxEval = -Infinity;
                let choice = null;
                if (depth === 3) { // Tracks
                    for (let tr in tracks) {
                        let score = minimax(tracks[tr], depth - 1, alpha, beta, false).val;
                        if (score > maxEval) {
                            maxEval = score;
                            choice = tr;
                        }
                        alpha = Math.max(alpha, score);
                        if (beta <= alpha) { prunes++; break; }
                    }
                    return { val: maxEval, item: choice };
                } else { // Course list
                    for (let c of node) {
                        let score = minimax(c, depth - 1, alpha, beta, false).val;
                        if (score > maxEval) {
                            maxEval = score;
                            choice = c;
                        }
                        alpha = Math.max(alpha, score);
                        if (beta <= alpha) { prunes++; break; }
                    }
                    return { val: maxEval, item: choice };
                }
            } else {
                let minEval = Infinity;
                let choice = null;

                let left = node.filter(c => parseFloat(c.difficulty) <= 3.0);
                let right = node.filter(c => parseFloat(c.difficulty) > 3.0);
                let branches = [];
                if (left.length) branches.push(left);
                if (right.length) branches.push(right);

                for (let b of branches) {
                    let score = minimax(b, depth - 1, alpha, beta, true).val;
                    if (score < minEval) {
                        minEval = score;
                        choice = b;
                    }
                    beta = Math.min(beta, score);
                    if (beta <= alpha) { prunes++; break; }
                }
                return { val: minEval, item: choice };
            }
        }

        let res = minimax(null, 3, -Infinity, Infinity, true);
        return {
            best_track: res.item,
            expected_utility: parseFloat(res.val.toFixed(2)),
            nodes_evaluated: evals,
            nodes_pruned: prunes,
            explanation: `The decision engine ran a 3-depth Minimax search. The student (MAX) chose the ${res.item} track. The academic advisor (MIN) balanced the track by separating courses by difficulty. The final selected sub-branch yielded an expected utility of ${res.val.toFixed(2)}.`
        };
    }
}

// --- CO5: Bayesian Inference Network ---
class ClientBayesianConfidence {
    static getPriors(course, profile) {
        let interests = profile.interests.split(',').map(i => i.trim().toLowerCase()).filter(i => i);
        let hasInterest = interests.some(i => 
            course.description.toLowerCase().includes(i) ||
            course.title.toLowerCase().includes(i) ||
            course.category.toLowerCase().includes(i)
        );
        let p_I1 = hasInterest ? 0.90 : 0.15;

        // Background Check (completed prereqs & gpa)
        let cgpa = parseFloat(profile.cgpa);
        let completed = profile.completed_courses.split(',').map(c => c.trim().toUpperCase()).filter(c => c);
        let prereqs = course.prerequisites ? course.prerequisites.split(',').map(p => p.trim().toUpperCase()).filter(p => p) : [];
        let met = prereqs.every(p => completed.includes(p));

        let p_B1 = 0.15;
        if (met && cgpa >= 8.5) p_B1 = 0.95;
        else if (met && cgpa >= 7.0) p_B1 = 0.80;
        else if (!met && cgpa >= 8.5) p_B1 = 0.40;

        // Difficulty High
        let diff = parseFloat(course.difficulty);
        let p_D1 = diff >= 3.5 ? 0.85 : 0.20;

        return { I: p_I1, B: p_B1, D: p_D1 };
    }

    static calculateConfidence(course, profile) {
        let priors = this.getPriors(course, profile);
        
        // P(S=1 | I, B, D)
        const CPT = {
            '1,1,0': 0.95,
            '1,1,1': 0.85,
            '1,0,0': 0.70,
            '1,0,1': 0.50,
            '0,1,0': 0.60,
            '0,1,1': 0.40,
            '0,0,0': 0.30,
            '0,0,1': 0.10
        };

        let p_success = 0.0;
        let trace = [];

        for (let i of [0, 1]) {
            for (let b of [0, 1]) {
                for (let d of [0, 1]) {
                    let term = (i === 1 ? priors.I : 1 - priors.I) *
                               (b === 1 ? priors.B : 1 - priors.B) *
                               (d === 1 ? priors.D : 1 - priors.D);
                    let cond = CPT[`${i},${b},${d}`];
                    let contr = cond * term;
                    p_success += contr;
                    trace.push({
                        combination: `I=${i}, B=${b}, D=${d}`,
                        prior_prob: term,
                        cpt_prob: cond,
                        contribution: contr
                    });
                }
            }
        }

        return {
            confidence_score: parseFloat((p_success * 100).toFixed(1)),
            evidence_priors: {
                interest_fit: parseFloat((priors.I * 100).toFixed(1)),
                background_pass: parseFloat((priors.B * 100).toFixed(1)),
                difficulty_high: parseFloat((priors.D * 100).toFixed(1))
            },
            inference_trace: trace,
            explanation: `Bayesian confidence is ${(p_success*100).toFixed(1)}%. Prior probabilities calculated from profile: interest match likelihood = ${(priors.I*100).toFixed(0)}%, academic background strength = ${(priors.B*100).toFixed(0)}%, and course difficulty high chance = ${(priors.D*100).toFixed(0)}%.`
        };
    }
}

// --- CO6: Integrated Pipeline ---
const OfflineAI = {
    runPipeline: function(profile) {
        let courses = LocalDb.getCourses();
        let completed = profile.completed_courses.split(',').map(c => c.trim().toUpperCase()).filter(c => c);

        // State formulation
        let initial_skills = new Set();
        courses.forEach(c => {
            if (completed.includes(c.code)) {
                c.skills_taught.split(',').forEach(s => {
                    if (s.trim()) initial_skills.add(s.trim());
                });
            }
        });
        
        let initial_state = new ClientState(
            completed,
            Array.from(initial_skills),
            parseFloat(profile.cgpa),
            courses.filter(c => completed.includes(c.code)).reduce((sum, c) => sum + parseInt(c.credits), 0)
        );

        // Goal setup
        const career_map = {
            "artificial intelligence engineer": ["programming", "python", "algorithms", "ai", "search_algorithms", "machine_learning", "neural_networks"],
            "ai engineer": ["programming", "python", "algorithms", "ai", "search_algorithms", "machine_learning", "neural_networks"],
            "data scientist": ["programming", "python", "algorithms", "sql", "databases", "machine_learning"],
            "software engineer": ["programming", "python", "algorithms", "data_structures", "sql", "databases", "design_patterns"],
            "software developer": ["programming", "python", "algorithms", "data_structures", "sql", "databases", "design_patterns"],
            "systems engineer": ["programming", "assembly", "c", "concurrency", "memory_management", "networking"],
            "network architect": ["programming", "c", "networking", "tcp_ip", "security"]
        };
        let goal_career = profile.career_goal.toLowerCase().trim();
        let req_skills = new Set();
        if (career_map[goal_career]) {
            career_map[goal_career].forEach(s => req_skills.add(s));
        }
        profile.skills_to_learn.split(',').forEach(s => {
            if (s.trim()) req_skills.add(s.trim().toLowerCase());
        });

        // Intersect goal skills with all taught skills
        let all_taught = new Set();
        courses.forEach(c => c.skills_taught.split(',').forEach(s => {
            if (s.trim()) all_taught.add(s.trim().toLowerCase());
        }));
        let matched_skills = Array.from(req_skills).filter(s => all_taught.has(s));
        if (matched_skills.length === 0) matched_skills = ["programming", "algorithms"];
        let targetSkillsSet = new Set(matched_skills);

        // MAUT calculation for remaining courses
        let candidates = [];
        courses.forEach(c => {
            if (!initial_state.completed_courses.has(c.code)) {
                let u = ClientDecisionEngine.calculateUtility(c, profile);
                candidates.push({
                    course: c,
                    utility: u.total_utility,
                    breakdown: u.breakdown
                });
            }
        });
        candidates.sort((a, b) => {
            if (b.breakdown.interest !== a.breakdown.interest) {
                return b.breakdown.interest - a.breakdown.interest;
            }
            return b.utility - a.utility;
        });

        let topCandidates = candidates.slice(0, 6);

        // Bayesian Confidences
        let recommended_courses = [];
        topCandidates.forEach(cand => {
            let c = cand.course;
            let conf = ClientBayesianConfidence.calculateConfidence(c, profile);
            let interests = profile.interests.split(',').map(i => i.trim().toLowerCase()).filter(i => i);
            let matching = interests.filter(i => c.description.toLowerCase().includes(i) || c.title.toLowerCase().includes(i) || c.category.toLowerCase().includes(i));
            
            let intReason = matching.length 
                ? `Suggested directly because of your active interests: '${matching.join(', ')}'.` 
                : `Suggested as a foundational course to bridge prerequisites, though it does not directly match your active interests ('${interests.join(', ')}').`;
            
            let explanation = `${intReason} This course yields a utility score of ${cand.utility.toFixed(2)} (Interest Match: ${(cand.breakdown.interest*100).toFixed(0)}%, Skill Match: ${(cand.breakdown.skills*100).toFixed(0)}%, Career Match: ${(cand.breakdown.career*100).toFixed(0)}%). The Bayesian confidence engine calculates a ${conf.confidence_score}% probability of success, based on your current CGPA of ${profile.cgpa} and prerequisite fulfillment status.`;

            recommended_courses.push({
                code: c.code,
                title: c.title,
                category: c.category,
                credits: c.credits,
                difficulty: c.difficulty,
                skills_taught: c.skills_taught,
                prerequisites: c.prerequisites,
                description: c.description,
                utility: cand.utility,
                utility_breakdown: cand.breakdown,
                confidence_score: conf.confidence_score,
                evidence_priors: conf.evidence_priors,
                inference_trace: conf.inference_trace,
                explanation: explanation
            });
        });

        // Minimax selection
        let minimax_game = ClientDecisionEngine.runAdvisorGame(profile, courses);

        // Search comparison
        let search_comparisons = [
            ClientSearchEngine.runBFS(initial_state, targetSkillsSet, courses),
            ClientSearchEngine.runDFS(initial_state, targetSkillsSet, courses),
            ClientSearchEngine.runUCS(initial_state, targetSkillsSet, courses),
            ClientSearchEngine.runAStar(initial_state, targetSkillsSet, courses)
        ];

        // CSP Scheduler
        let codes = recommended_courses.map(r => r.code);
        let csp = new ClientCSPScheduler(codes, courses);
        let csp_results = csp.solve();

        // Trace outputs
        let pipeline_trace = {
            co1_state_formulation: {
                initial_state: initial_state.toDict(),
                goal_career_path: profile.career_goal,
                goal_required_skills: matched_skills,
                trace: `[CLIENT-SIDE ENGINE] Formulated State containing completed courses and skills. Target skills set established: ${matched_skills.join(', ')}.`
            },
            co2_search_comparison: {
                results: search_comparisons,
                trace: `[CLIENT-SIDE ENGINE] Graph searches BFS, DFS, UCS, A* evaluated in browser context. Admissible heuristic h(n) = (missing_skills / max_skills) * min_cost calculated.`
            },
            co3_csp_scheduler: {
                success: csp_results.success,
                assignments: csp_results.assignments,
                schedule: csp_results.schedule,
                trace: `[CLIENT-SIDE ENGINE] CSP scheduler ran backtracking in JavaScript. Assigned variables: ${codes.join(', ')} to semesters 1-4 satisfying constraint parameters.`
            },
            co4_decision_making: {
                minimax_game: minimax_game,
                trace: `[CLIENT-SIDE ENGINE] Ranked courses using MAUT equations. Executed advisor-student selection game tree up to depth 3 with Alpha-Beta parameters.`
            },
            co5_uncertainty_handling: {
                trace: `[CLIENT-SIDE ENGINE] Bayesian inference network computed conditional outcomes over variables.`
            }
        };

        return {
            recommended_courses: recommended_courses,
            search_comparisons: search_comparisons,
            csp_schedule: csp_results.success ? csp_results.schedule : null,
            minimax_game: minimax_game,
            pipeline_trace: pipeline_trace
        };
    }
};