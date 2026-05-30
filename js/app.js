/**
 * Frontend Controller (app.js)
 * Manages form submissions, user sessions, UI rendering, 
 * and handles database updates using local storage.
 */

// Global App State
let appState = {
    currentUser: null,
    courses: []
};

document.addEventListener('DOMContentLoaded', () => {
    // Event Listeners
    setupEventListeners();

    // Load Initial Course List
    loadCourses();
});

function setupEventListeners() {
    // Student profile form submission
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', handleProfileSubmit);
    }

    // Admin login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    // Add/Edit Course form (Admin Dashboard)
    const courseForm = document.getElementById('courseForm');
    if (courseForm) {
        courseForm.addEventListener('submit', handleCourseSubmit);
    }

    // Logout
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
}

// 2. Fetch & Render Courses
async function loadCourses() {
    const listContainer = document.getElementById('allCoursesList');
    if (!listContainer) return;

    listContainer.innerHTML = `<div class="col-12 text-center text-secondary py-4">Loading courses...</div>`;
    
    try {
        appState.courses = LocalDb.getCourses();
        renderCoursesTable(appState.courses);
        renderCoursesCatalog(appState.courses);
    } catch (err) {
        listContainer.innerHTML = `<div class="col-12 text-center text-danger py-4">Error loading courses: ${err.message}</div>`;
    }
}

function renderCoursesCatalog(courses) {
    const catalogContainer = document.getElementById('coursesCatalog');
    if (!catalogContainer) return;

    if (courses.length === 0) {
        catalogContainer.innerHTML = `<p class="text-secondary text-center">No courses catalogued yet.</p>`;
        return;
    }

    let html = '';
    courses.forEach(c => {
        const difficultyClass = c.difficulty >= 3.5 ? 'diff-hard' : (c.difficulty >= 2.5 ? 'diff-medium' : 'diff-easy');
        const diffText = c.difficulty >= 3.5 ? 'Hard' : (c.difficulty >= 2.5 ? 'Medium' : 'Easy');
        const prereqs = c.prerequisites ? c.prerequisites : 'None';
        const skills = c.skills_taught.split(',').map(s => `<span class="skill-tag">${s.trim()}</span>`).join('');

        html += `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="glass-panel course-card">
                    <div class="course-card-header">
                        <span class="course-badge">${c.code}</span>
                        <span class="difficulty-badge ${difficultyClass}">${diffText} (${c.difficulty})</span>
                    </div>
                    <h5 class="fw-bold mb-2">${c.title}</h5>
                    <p class="text-secondary small mb-3 flex-grow-1">${c.description}</p>
                    <div class="mb-3">
                        <span class="d-block text-secondary small fw-bold">Prerequisites:</span>
                        <span class="small text-light">${prereqs}</span>
                    </div>
                    <div class="mb-3">
                        <span class="d-block text-secondary small fw-bold mb-1">Skills Taught:</span>
                        <div class="skills-list">${skills}</div>
                    </div>
                    <div class="d-flex justify-content-between text-secondary small mt-auto border-top pt-2">
                        <span>Category: ${c.category}</span>
                        <span>Credits: ${c.credits}</span>
                    </div>
                </div>
            </div>
        `;
    });
    catalogContainer.innerHTML = html;
}

// 3. Handle Recommendation Logic
async function handleProfileSubmit(e) {
    e.preventDefault();
    
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Computing...`;
    submitBtn.disabled = true;

    // Collect profile data
    const profile = {
        cgpa: parseFloat(document.getElementById('cgpa').value),
        interests: document.getElementById('interests').value.trim(),
        skills_to_learn: document.getElementById('skills_to_learn').value.trim(),
        career_goal: document.getElementById('career_goal').value,
        completed_courses: document.getElementById('completed_courses').value.trim()
    };

    try {
        // Run client-side JavaScript engine
        const results = OfflineAI.runPipeline(profile);

        // Show Results Section
        document.getElementById('resultsSection').style.display = 'block';
        document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });

        // Render Results UI
        renderRecommendations(results.recommended_courses);
        renderTimeline(results.csp_schedule, results.recommended_courses);
        renderDecisionDetails(results.minimax_game);
        renderXaiTraces(results.pipeline_trace);

        // Draw Chart.js Visualizations
        setTimeout(() => {
            ChartsManager.drawSearchComparison(results.search_comparisons);
            ChartsManager.drawUtilityBreakdown(results.recommended_courses);
            if (results.recommended_courses.length > 0) {
                ChartsManager.drawBayesianDistribution(results.recommended_courses[0]);
            }
        }, 100);

    } catch (err) {
        alert('Engine Failure: ' + err.message);
    } finally {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

function renderRecommendations(recs) {
    const container = document.getElementById('recommendedList');
    if (!container) return;

    if (recs.length === 0) {
        container.innerHTML = `<div class="col-12 text-center text-secondary py-4">No matching courses found. Try expanding your profile parameters.</div>`;
        return;
    }

    let html = '';
    recs.forEach((r, idx) => {
        const difficultyClass = r.difficulty >= 3.5 ? 'diff-hard' : (r.difficulty >= 2.5 ? 'diff-medium' : 'diff-easy');
        const diffText = r.difficulty >= 3.5 ? 'Hard' : (r.difficulty >= 2.5 ? 'Medium' : 'Easy');
        
        // Match percentage maps to MAUT utility
        const matchPercent = Math.round(r.utility * 100);

        html += `
            <div class="col-md-6 mb-4">
                <div class="glass-panel course-card">
                    <div class="course-card-header">
                        <span class="course-badge">${r.code}</span>
                        <span class="difficulty-badge ${difficultyClass}">${diffText} (${r.difficulty})</span>
                    </div>
                    <h5 class="fw-bold mb-2">${r.title}</h5>
                    <p class="text-secondary small mb-3 flex-grow-1">${r.description}</p>
                    
                    <div class="mb-3 small text-secondary">
                        <span class="fw-bold text-light">Prerequisites:</span> ${r.prerequisites || 'None'}
                    </div>

                    <div class="mb-3">
                        <p class="text-accent small mb-1"><i class="bi bi-robot"></i> <strong>AI Recommendation Explanation:</strong></p>
                        <p class="small text-secondary-light bg-dark-50 p-2 rounded border border-light-10">${r.explanation}</p>
                    </div>

                    <div class="match-gpa-container">
                        <div class="metric-box">
                            <div class="metric-label">Match Rank</div>
                            <div class="metric-value text-gradient">#${idx + 1}</div>
                        </div>
                        <div class="metric-box">
                            <div class="metric-label">Utility Score</div>
                            <div class="metric-value" style="color: #6366f1;">${matchPercent}%</div>
                        </div>
                        <div class="metric-box">
                            <div class="metric-label">Bayesian success</div>
                            <div class="metric-value" style="color: #a855f7;">${r.confidence_score}%</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    container.innerHTML = html;
}

function renderTimeline(schedule, recommended) {
    const container = document.getElementById('timelineContainer');
    if (!container) return;

    if (!schedule) {
        container.innerHTML = `
            <div class="col-12 text-center text-warning p-4">
                <strong>Semester Scheduling Failure:</strong> No semester schedule could be constructed that satisfies all credits (<= 8 per sem) and prerequisites constraints. Try selecting courses with fewer dependencies.
            </div>`;
        return;
    }

    // Build course map for details
    const courseMap = {};
    recommended.forEach(r => { courseMap[r.code] = r; });

    let html = '';
    for (let sem = 1; sem <= 4; sem++) {
        const codes = schedule[sem] || [];
        let coursesHtml = '';
        let totalCredits = 0;

        codes.forEach(code => {
            const name = courseMap[code] ? courseMap[code].title : 'Recommended Course';
            const cred = courseMap[code] ? parseInt(courseMap[code].credits) : 3;
            totalCredits += cred;
            
            coursesHtml += `
                <div class="semester-course-item">
                    <strong>${code}</strong><br>
                    <span class="small text-secondary">${name}</span><br>
                    <span class="badge bg-secondary-light small text-secondary mt-1">${cred} Credits</span>
                </div>
            `;
        });

        if (codes.length === 0) {
            coursesHtml = `<p class="text-secondary small text-center my-4">No courses scheduled</p>`;
        }

        html += `
            <div class="semester-bucket">
                <div class="semester-title d-flex justify-content-between">
                    <span>Semester ${sem}</span>
                    <span class="badge bg-purple-light text-accent">${totalCredits} Credits</span>
                </div>
                ${coursesHtml}
            </div>
        `;
    }
    container.innerHTML = html;
}

function renderDecisionDetails(game) {
    const titleEl = document.getElementById('minimaxTitle');
    const descEl = document.getElementById('minimaxDesc');
    
    if (titleEl && descEl && game) {
        titleEl.innerHTML = `Best Target Course Track: ${game.best_track}`;
        descEl.innerHTML = `${game.explanation} Under bounded depth (depth = 3), the alpha-beta pruning algorithm evaluated ${game.nodes_evaluated} states and pruned ${game.nodes_pruned} subtrees.`;
    }
}

function renderXaiTraces(trace) {
    const stateTrace = document.getElementById('stateTrace');
    const searchTrace = document.getElementById('searchTrace');
    const cspTrace = document.getElementById('cspTrace');
    const decisionTrace = document.getElementById('decisionTrace');

    if (stateTrace && trace) {
        stateTrace.innerText = JSON.stringify(trace.co1_state_formulation, null, 2);
        searchTrace.innerText = JSON.stringify(trace.co2_search_comparison, null, 2);
        cspTrace.innerText = JSON.stringify(trace.co3_csp_scheduler, null, 2);
        decisionTrace.innerText = JSON.stringify(trace.co4_decision_making, null, 2);
    }
}

// 4. Admin Authentication
async function handleLogin(e) {
    e.preventDefault();
    const user = document.getElementById('username').value.trim();
    const pass = document.getElementById('password').value;

    const errorEl = document.getElementById('loginError');
    errorEl.style.display = 'none';

    try {
        if (user === 'admin' && pass === 'admin123') {
            loginSuccess('admin', 'admin');
        } else if (user === 'student' && pass === 'student123') {
            loginSuccess('student', 'student');
        } else {
            throw new Error('Invalid credentials.');
        }
    } catch (err) {
        errorEl.innerText = err.message;
        errorEl.style.display = 'block';
    }
}

function loginSuccess(username, role) {
    appState.currentUser = { username, role };
    document.getElementById('loginSection').style.display = 'none';
    
    if (role === 'admin') {
        document.getElementById('adminDashboard').style.display = 'block';
    } else {
        alert(`Welcome, ${username}! You have student privileges. Recommendations can be run from the homepage.`);
    }
    
    // Clear forms
    document.getElementById('loginForm').reset();
}

function handleLogout() {
    appState.currentUser = null;
    document.getElementById('adminDashboard').style.display = 'none';
    document.getElementById('loginSection').style.display = 'block';
}

// 5. Admin CRUD operations
async function handleCourseSubmit(e) {
    e.preventDefault();
    
    const courseId = document.getElementById('courseId').value;
    const courseData = {
        code: document.getElementById('courseCode').value.trim().toUpperCase(),
        title: document.getElementById('courseTitle').value.trim(),
        category: document.getElementById('courseCategory').value,
        credits: parseInt(document.getElementById('courseCredits').value),
        difficulty: parseFloat(document.getElementById('courseDifficulty').value),
        skills_taught: document.getElementById('courseSkills').value.trim(),
        prerequisites: document.getElementById('coursePrerequisites').value.trim().toUpperCase(),
        description: document.getElementById('courseDescription').value.trim()
    };

    try {
        if (courseId) {
            // Update
            LocalDb.updateCourse(courseId, courseData);
        } else {
            // Add
            const success = LocalDb.addCourse(courseData);
            if (!success) throw new Error('Course code already exists.');
        }

        // Reset Form & Close Modal
        document.getElementById('courseForm').reset();
        document.getElementById('courseId').value = '';
        
        // Hide modal
        const modalEl = document.getElementById('courseModal');
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();
        
        // Reload course list
        loadCourses();
        alert('Course saved successfully.');

    } catch (err) {
        alert('Action Failed: ' + err.message);
    }
}

function renderCoursesTable(courses) {
    const tableBody = document.getElementById('adminCoursesTable');
    if (!tableBody) return;

    if (courses.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="7" class="text-center text-secondary">No courses found.</td></tr>`;
        return;
    }

    let html = '';
    courses.forEach(c => {
        html += `
            <tr>
                <td><strong>${c.code}</strong></td>
                <td>${c.title}</td>
                <td><span class="badge bg-secondary">${c.category}</span></td>
                <td>${c.credits}</td>
                <td>${c.difficulty}</td>
                <td><span class="text-secondary small">${c.prerequisites || 'None'}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="editCourse(${c.id})"><i class="bi bi-pencil"></i></button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteCourse(${c.id})"><i class="bi bi-trash"></i></button>
                </td>
            </tr>
        `;
    });
    tableBody.innerHTML = html;
}

window.editCourse = function(id) {
    const course = appState.courses.find(c => c.id === id);
    if (!course) return;

    document.getElementById('courseId').value = course.id;
    document.getElementById('courseCode').value = course.code;
    document.getElementById('courseTitle').value = course.title;
    document.getElementById('courseCategory').value = course.category;
    document.getElementById('courseCredits').value = course.credits;
    document.getElementById('courseDifficulty').value = course.difficulty;
    document.getElementById('courseSkills').value = course.skills_taught;
    document.getElementById('coursePrerequisites').value = course.prerequisites || '';
    document.getElementById('courseDescription').value = course.description || '';

    // Show Modal
    const modalEl = document.getElementById('courseModal');
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
};

window.deleteCourse = async function(id) {
    if (!confirm('Are you sure you want to delete this course? This action cannot be undone.')) return;

    try {
        LocalDb.deleteCourse(id);
        loadCourses();
        alert('Course deleted successfully.');
    } catch (err) {
        alert('Delete Failed: ' + err.message);
    }
};