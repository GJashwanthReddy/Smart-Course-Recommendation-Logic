# Smart Course Recommendation Logic

An advanced, explainable AI (XAI) course advisor web application built as a standalone frontend client (**HTML, CSS, JavaScript, and Chart.js**).

The system recommends courses based primarily on user interests, then refines the suggestions using skills, CGPA, career goals, and learning preferences. All AI recommendation, search comparison, constraint scheduling, Bayesian likelihood calculation, and utility ranking logic run entirely in the browser using the client-side JavaScript engine (`mock_engine.js`) and persist customizations via browser `localStorage`.

---

## 🧠 Integrated AI Reasoning Architecture

The application demonstrates six fundamental Artificial Intelligence concepts to solve personalized course path planning:

- **Problem Formulation & Knowledge Representation:** Models course path planning as a state-space planning problem. The planning state consists of completed courses, acquired skills, and CGPA. Enforces course prerequisites and academic constraints.
- **State-Space Search Comparison:** Compares graph search algorithms (BFS, DFS, UCS, A*) to find optimal sequences of courses to reach a target career goal profile. Guarantees optimality using an admissible and consistent heuristic:
  $$h(n) = \frac{|\text{missing\_skills}(n)|}{\max_c |\text{skills}(c)|} \times \min_c \text{cost}(c)$$
- **Constraint Satisfaction Semester Scheduling:** Schedules recommended courses into 4 semesters using a Backtracking search solver equipped with the Minimum Remaining Values (MRV) heuristic, Degree heuristic, and Forward Checking domain propagation under credit (<= 8 per sem) and prerequisite constraints.
- **Decision-Making & Utility Ranking:** Evaluates and ranks courses using Multi-Attribute Utility Theory (MAUT) with priority weighting on interest matching. Simulates advisor-student game-theoretic scheduling decisions using a 3-depth Minimax game with Alpha-Beta pruning.
- **Bayesian Network Uncertainty Inference:** Performs exact joint probability inference on a Bayesian Network (nodes: Interest, Background, Difficulty, Success) to calculate success likelihood (Confidence Scores) for each recommended course.
- **Explainable AI (XAI) Trace Pipeline:** Combines searches, schedules, utility calculations, and Bayesian scores into a single diagnostic pipeline, showing natural-language explanations citing matching interests and exposing step-by-step logic traces in a developer trace panel.

---

## 🛠️ Project Structure

```
Smart Course Recommendation Logic/
│
├── index.html             # Main course advisor dashboard
├── about.html             # AI concepts educational page
├── admin.html             # Admin portal to manage database courses
│
├── css/
│   └── styles.css         # Premium glassmorphic styling (dark-mode)
│
└── js/
    ├── app.js             # Event listeners, local DB synchronization, UI controller
    ├── charts.js          # Chart.js visualization configurations
    └── mock_engine.js     # Standalone AI reasoning & solver engine
```

---

## 🚀 Running the Project

Since this is a **frontend-only client application**, there is no server installation required:

1. **Launch the Application:**
   Simply double-click [index.html](index.html) to open the dashboard directly in any modern web browser (using the `file://` protocol).
   
2. **Review Recommendations:**
   Input a CGPA, select your career goals, type your interests (e.g. `machine learning`, `algorithms`), and click **Compute Optimal Course Path**. The system will instantly calculate and display the recommendation results, semester timeline, comparative metrics charts, and reasoning traces.

3. **Manage Course Database:**
   Click the **Admin Panel** in the navbar and log in with the administrator credentials. You can add, edit, or delete course offerings. Changes will persist inside your browser's local storage database and instantly affect recommendation results on the main page.

---

## 🔐 Credentials (Admin & Mock Data)

To log in to the Course Database Console in `admin.html`:
- **Username:** `admin`
- **Password:** `admin123`
- (For basic student mock login, use: `student`/`student123`)