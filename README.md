# SentinelAI — Agentic Urban Safety Network

SentinelAI is an Agentic Urban Safety Network built to transform ordinary CCTV infrastructure into a collaborative, intelligent surveillance platform.

This project implements a multi-agent backend orchestrating 7 independent agent roles over a centralized `SharedMemory` state machine.

---

## 🛠️ Tech Stack
- **Backend Framework**: Python 3.12, FastAPI
- **Multi-Agent Orchestration**: LangGraph
- **Database Layer**: SQLAlchemy, SQLite (with PG support)
- **Deployment**: Docker, Docker Compose

---

## 📂 Folder Structure

```text
sentinel-ai/
├── backend/
│   ├── app/
│   │   ├── api/                 # Endpoints & dependencies
│   │   ├── agents/              # The 7 Agent classes
│   │   ├── orchestration/       # LangGraph and event coordination
│   │   ├── core/                # State machine & configuration
│   │   ├── models/              # SQLAlchemy database tables
│   │   ├── database/            # Engines & sessions
│   │   ├── services/            # CV & business interfaces
│   │   ├── utils/               # Time/distance calculations
│   │   ├── simulations/         # Scenario demo loop
│   │   └── main.py              # FastAPI startup script
│   └── Dockerfile
├── tests/                       # Pytest unit testing suite
├── docker/                      # Deployment readmes
├── logs/                        # Application logs
├── docs/                        # Architecture documentation
├── docker-compose.yml
├── requirements.txt
└── .env
```

---

## 🚀 Getting Started

### Prerequisites
Make sure Python 3.12+ and `pip` are installed on your system.

### 1. Installation
Clone or navigate to the workspace and install the python dependencies:
```bash
pip install -r requirements.txt
```

### 2. Run Simulation Scenario
Run the simulation script to execute the 33-minute scenario and view the terminal trace logging:
```bash
python backend/app/simulations/scenario_demo.py
```

### 3. Run Web Server
Start the development server:
```bash
python backend/app/main.py
```
Open [http://localhost:8000](http://localhost:8000) in your browser to view the interactive control panel dashboard!

### 4. Running unit tests
Run test suites using pytest:
```bash
pytest tests/
```
