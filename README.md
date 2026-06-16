# Smart Course Recommendation Logic

An advanced, explainable AI (XAI) course advisor system. This project features two fully operational user interfaces:
1. **Interactive Web Dashboard:** Runs entirely client-side in the browser using **PyScript (WebAssembly/Pyodide)**, executing the core Python algorithms locally on the client machine with **no backend server**.
2. **Interactive CLI Console Application:** A terminal-based option menu to trace and run all Course Outcomes.

---

## 🧠 Course Outcomes (CO) & AI Concepts Implemented

- **Problem Formulation & Knowledge Representation (CO1):**
  - Path planning is modeled as a state-space transition graph where states track completed courses, acquired skills, and cumulative CGPA.
  - Formulated within [modules/formulation.py](file:///c:/Users/G%20Jashwanth%20Reddy/OneDrive/Documents/CFAI-Term-3/CFAI%20PROJECT/Smart%20Course%20Recommendation%20Logic/modules/formulation.py) using the PEAS model and environment classification taxonomy.

- **Optimal Prerequisite Pathfinding Search (CO2):**
  - Compares pathfinders (BFS, DFS, UCS, A*) to find optimal course sequences for target skills.
  - Implements an admissible and consistent heuristic mapping:
    $$h(n) = \frac{|\text{missing\_skills}(n)|}{\max_c |\text{skills}(c)|} \times \min_c \text{cost}(c)$$
  - Formulated in [modules/search_logic.py](file:///c:/Users/G%20Jashwanth%20Reddy/OneDrive/Documents/CFAI-Term-3/CFAI%20PROJECT/Smart%20Course%20Recommendation%20Logic/modules/search_logic.py).

- **Constraint Satisfaction Semester Scheduling (CO3):**
  - Allocates courses to terms using Backtracking Search with the **Minimum Remaining Values (MRV)** heuristic, **Degree** heuristic, and **Forward Checking** domain propagation.
  - Formulated in [modules/csp_scheduler.py](file:///c:/Users/G%20Jashwanth%20Reddy/OneDrive/Documents/CFAI-Term-3/CFAI%20PROJECT/Smart%20Course%20Recommendation%20Logic/modules/csp_scheduler.py).

- **Multi-Attribute Utility & Minimax Enrollment Game (CO4):**
  - Ranks course choices using Multi-Attribute Utility Theory (MAUT) based on interest match, skill matching, and CGPA-workload compatibility.
  - Models enrollment decisions against environmental closed-section constraints using a Minimax Game with **Alpha-Beta Pruning**.
  - Formulated in [modules/decision_making.py](file:///c:/Users/G%20Jashwanth%20Reddy/OneDrive/Documents/CFAI-Term-3/CFAI%20PROJECT/Smart%20Course%20Recommendation%20Logic/modules/decision_making.py).

- **Bayesian Network Success Forecast (CO5):**
  - Performs **Inference by Enumeration** (exact joint probability) on a Bayesian network linking Prerequisite Met, Student Interest, Study Time, and Course Success.
  - Formulated in [modules/bayes_network.py](file:///c:/Users/G%20Jashwanth%20Reddy/OneDrive/Documents/CFAI-Term-3/CFAI%20PROJECT/Smart%20Course%20Recommendation%20Logic/modules/bayes_network.py).

- **Integrated Advising Pipeline (CO6):**
  - Couples all components into a unified execution flow: A* Search finds required courses -> CSP scheduler assigns terms -> Bayesian Net forecasts success -> Minimax selects the optimal first term choice.
  - Formulated in [modules/integrated_advisor.py](file:///c:/Users/G%20Jashwanth%20Reddy/OneDrive/Documents/CFAI-Term-3/CFAI%20PROJECT/Smart%20Course%20Recommendation%20Logic/modules/integrated_advisor.py).

---

## 🛠️ Project Structure

```
Smart Course Recommendation Logic/
│
├── index.html                  # Main Web Dashboard UI powered by PyScript
├── styles.css                  # Premium dark-mode glassmorphic stylesheet
├── web_app.py                  # PyScript dynamic UI event connector
├── main.py                     # Entry point & interactive CLI menu loop
├── README.md                   # Project documentation
│
└── modules/
    ├── __init__.py             # Module initialization
    ├── formulation.py          # PEAS Agent specifications & models
    ├── search_logic.py         # BFS, DFS, UCS, A* searching comparison
    ├── csp_scheduler.py        # Constraint Satisfaction backtracking scheduler
    ├── decision_making.py      # MAUT rankings & Minimax with Alpha-Beta
    ├── bayes_network.py        # Exact Bayesian Inference by Enumeration
    ├── integrated_advisor.py   # Integrated reasoning system pipeline
    └── console_ui.py           # Catalog, profile, and interactive console forms
```

---

## 🚀 Running the Project

### Option A: Web Dashboard (No Backend)
Because PyScript must fetch local Python modules, modern browsers block direct file access (`file:///`) due to CORS security policies. You must run a small static file server locally (which serves files but runs **no backend logic**):

1. **Launch the Static Server in VS Code Terminal:**
   ```powershell
   & "C:\Users\G Jashwanth Reddy\AppData\Local\Python\bin\python.exe" -m http.server 8000
   ```
2. **Access the Web App:**
   Open your browser and navigate to:
   [http://127.0.0.1:8000](http://127.0.0.1:8000)
   *Wait a few seconds for the PyScript environment to mount WebAssembly and load. The visual panels, graphs, and catalog will populate automatically!*

*Alternatively, you can open `index.html` using the **Live Server** extension in VS Code.*

---

### Option B: Terminal CLI Application
If you prefer running directly in your shell terminal:

1. **Start the Console Loop:**
   ```powershell
   & "C:\Users\G Jashwanth Reddy\AppData\Local\Python\bin\python.exe" main.py
   ```
2. **Use Options [0-9]** to interact with the system logic.