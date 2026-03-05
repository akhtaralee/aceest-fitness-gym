# ACEest Fitness & Gym – Deployment Pipeline

A **Flask-based** fitness and gym management web application with a fully automated DevOps pipeline covering version control, unit testing, containerisation, Jenkins CI, and GitHub Actions CI/CD.

---

## 📁 Repository Structure

```
├── app.py                        # Flask web application (source code)
├── test_app.py                   # Pytest test suite
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker image definition
├── Jenkinsfile                   # Jenkins declarative pipeline
├── .github/
│   └── workflows/
│       └── main.yml              # GitHub Actions CI/CD workflow
├── .gitignore
├── README.md                     # ← You are here
└── Aceestver-*.py                # Legacy desktop (Tkinter) versions
```

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| **Programme Catalogue** | Fat Loss, Muscle Gain, Beginner plans with workout & diet info |
| **Calorie Calculator** | `weight × programme factor` estimation |
| **BMI Calculator** | BMI value + category classification |
| **Client CRUD API** | Create / Read / Delete clients via REST |
| **Health Endpoint** | `/health` for Docker & CI readiness probes |

---

## 🛠️ Local Setup & Execution

### Prerequisites

* Python 3.10+ installed
* Docker installed (for containerised runs)

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/aceest-fitness-gym.git
cd aceest-fitness-gym
```

### 2. Create a virtual environment & install dependencies

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Run the application

```bash
python app.py
```

Open **http://localhost:5000** in your browser.

### 4. Run with Docker

```bash
docker build -t aceest-fitness-gym .
docker run -p 5000:5000 aceest-fitness-gym
```

---

## 🧪 Running Tests Manually

```bash
# Activate the virtual environment first, then:
pytest test_app.py -v
```

**What the test suite covers:**

| Area | Tests |
|------|-------|
| `calculate_calories()` | Valid programmes, edge cases, invalid input |
| `calculate_bmi()` | Normal values, zero/negative input |
| `bmi_category()` | All four categories + boundary values |
| `GET /` | Status 200, page title present |
| `GET /health` | Healthy response |
| `GET /api/programs` | All programmes returned |
| `POST /api/calculate_calories` | Valid & invalid payloads |
| `POST /api/bmi` | Valid & invalid payloads |
| `CRUD /api/clients` | Create, read, delete, duplicates, 404s |

---

## 🔧 Jenkins Integration (BUILD Phase)

### Overview

Jenkins acts as the **primary BUILD server** and quality gate. A **Jenkinsfile** (declarative pipeline) is included in the repo.

### Pipeline Stages

```
Checkout → Setup Python Env → Lint (Flake8) → Unit Tests (Pytest) → Build Docker Image → Container Tests
```

### Setup Steps

1. Install **Jenkins** on your build server.
2. Install the **Pipeline** and **Git** plugins.
3. Create a **New Pipeline Project** in Jenkins.
4. Under *Pipeline → Definition*, select **Pipeline script from SCM**.
5. Set the SCM to **Git** and enter the GitHub repository URL.
6. Jenkins will automatically detect the `Jenkinsfile` at the repo root.
7. Click **Build Now** — the pipeline will:
   * Pull the latest code from GitHub
   * Set up a Python virtual environment
   * Lint the code with Flake8
   * Run the Pytest suite
   * Build a Docker image
   * Execute tests inside the container

---

## ⚙️ GitHub Actions CI/CD Pipeline

### Trigger

The workflow (`.github/workflows/main.yml`) runs on every **push** to `main` / `develop` and on every **pull request** targeting `main`.

### Pipeline Stages

| Stage | What it does |
|-------|-------------|
| **Build & Lint** | Installs dependencies, runs Flake8 syntax/style checks |
| **Docker Image Assembly** | Builds the Docker image from the Dockerfile |
| **Automated Testing** | Runs Pytest inside the container + a live health check |

### Flow Diagram

```
push / PR
    │
    ▼
┌──────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ Build & Lint │ ──▶ │ Docker Image     │ ──▶ │ Automated Tests  │
│ (Flake8)     │     │ Assembly         │     │ (Pytest + Health)│
└──────────────┘     └──────────────────┘     └──────────────────┘
```

---

## 🗂️ Version History (Legacy Desktop App)

| Version | Highlights |
|---------|-----------|
| 1.0 | Basic Tkinter UI with programme display |
| 1.1 | Client profile input, calorie estimation |
| 1.1.2 | CSV export, multi-client table, chart |
| 2.0.1 | SQLite database, client persistence |
| 2.1.2 | Load client, progress logging |
| 2.2.1 | Matplotlib progress chart |
| 2.2.4 | Advanced schema, workout/exercise/metrics tracking |
| 3.0.1 | Goals, BMI, analytics tabs |
| 3.1.2 | Role-based login, PDF reports, embedded charts |
| 3.2.4 | Refactored modular architecture, membership billing |

---

## 📜 License

This project is for academic / assignment purposes.

---

> **ACEest Fitness & Gym** — *Your journey to peak performance starts here.*
