import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

# Import session & config
from app.core.config import settings
from app.database.session import engine
from app.database.base import Base

# Prepopulate models to ensure they register on Base
from app.models.entity import Entity
from app.models.alert import Alert
from app.models.patrol import PatrolUnit
from app.models.risk import InvestigationLog, LearningHistory, SystemAnalytics

# Import API routes
from app.api.routes import camera, state

# Initialize database tables on startup
Base.metadata.create_all(bind=engine)

# Create FastAPI instance
app = FastAPI(
    title="SentinelAI — Agentic Urban Safety Network",
    description="Collaborative surveillance and patrol dispatch MVP",
    version="1.0.0"
)

# CORS middleware config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(camera.router)
app.include_router(state.router)


@app.get("/", response_class=HTMLResponse)
def serve_dashboard(request: Request):
    """Serves a premium, interactive SentinelAI dashboard UI (glassmorphism/dark mode)."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SentinelAI — Safety Network Control Panel</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;700&display=swap" rel="stylesheet">
        <!-- FontAwesome for Premium Icons -->
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <!-- Leaflet.js for Interactive City Map -->
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        
        <style>
            :root {
                --bg-color: #030712;
                --card-bg: rgba(17, 24, 39, 0.7);
                --card-border: rgba(255, 255, 255, 0.06);
                --text-primary: #f9fafb;
                --text-secondary: #9ca3af;
                --accent-blue: #3b82f6;
                --accent-cyan: #06b6d4;
                --accent-red: #f43f5e;
                --accent-amber: #f59e0b;
                --accent-emerald: #10b981;
                
                --glow-cyan: rgba(6, 182, 212, 0.15);
                --glow-red: rgba(244, 63, 94, 0.15);
                --glow-amber: rgba(245, 158, 11, 0.15);
                --glow-emerald: rgba(16, 185, 129, 0.15);
            }

            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }

            body {
                background-color: var(--bg-color);
                background-image: 
                    radial-gradient(circle at 50% 0%, rgba(59, 130, 246, 0.12) 0%, transparent 50%),
                    radial-gradient(circle at 0% 100%, rgba(6, 182, 212, 0.05) 0%, transparent 40%);
                color: var(--text-primary);
                font-family: 'Outfit', sans-serif;
                min-height: 100vh;
                overflow-x: hidden;
            }

            header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 1.25rem 2.5rem;
                background: rgba(3, 7, 18, 0.6);
                backdrop-filter: blur(16px);
                border-bottom: 1px solid var(--card-border);
                position: sticky;
                top: 0;
                z-index: 1000;
            }

            .logo-container {
                display: flex;
                align-items: center;
                gap: 0.875rem;
            }

            .logo-icon {
                width: 2.25rem;
                height: 2.25rem;
                background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 0 15px rgba(6, 182, 212, 0.4);
            }

            .logo-icon i {
                font-size: 1.125rem;
                color: white;
            }

            header h1 {
                font-family: 'Space Grotesk', sans-serif;
                font-size: 1.375rem;
                font-weight: 700;
                letter-spacing: -0.03em;
                background: linear-gradient(135deg, #ffffff 30%, #9ca3af 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }

            .btn {
                background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
                color: white;
                border: none;
                padding: 0.625rem 1.25rem;
                font-weight: 600;
                font-size: 0.875rem;
                font-family: 'Outfit', sans-serif;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3);
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }

            .btn:hover {
                transform: translateY(-1px);
                box-shadow: 0 6px 16px rgba(6, 182, 212, 0.5);
                filter: brightness(1.1);
            }

            .btn i {
                font-size: 0.875rem;
            }

            /* Main Layout Grid */
            .main-content {
                max-width: 1600px;
                margin: 2rem auto;
                padding: 0 2rem;
                display: flex;
                flex-direction: column;
                gap: 2rem;
            }

            /* Top Metrics Strip */
            .metrics-row {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 1.5rem;
            }

            .metric-card {
                background: var(--card-bg);
                border: 1px solid var(--card-border);
                border-radius: 14px;
                padding: 1.25rem 1.5rem;
                display: flex;
                align-items: center;
                justify-content: space-between;
                backdrop-filter: blur(12px);
                transition: all 0.3s;
            }

            .metric-card:hover {
                border-color: rgba(255, 255, 255, 0.12);
                transform: translateY(-2px);
            }

            .metric-info {
                display: flex;
                flex-direction: column;
                gap: 0.25rem;
            }

            .metric-info label {
                font-size: 0.75rem;
                color: var(--text-secondary);
                text-transform: uppercase;
                letter-spacing: 0.05em;
                font-weight: 600;
            }

            .metric-info .value {
                font-size: 1.5rem;
                font-weight: 700;
                font-family: 'Space Grotesk', sans-serif;
            }

            .metric-icon {
                width: 2.75rem;
                height: 2.75rem;
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.25rem;
            }

            /* Core Columns: Map & Panels */
            .columns-grid {
                display: grid;
                grid-template-columns: 1.2fr 0.8fr;
                gap: 2rem;
                align-items: start;
            }

            @media(max-width: 1200px) {
                .columns-grid {
                    grid-template-columns: 1fr;
                }
            }

            .card {
                background: var(--card-bg);
                border: 1px solid var(--card-border);
                backdrop-filter: blur(20px);
                border-radius: 16px;
                padding: 1.75rem;
                display: flex;
                flex-direction: column;
                gap: 1.5rem;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            }

            .card-title {
                font-family: 'Space Grotesk', sans-serif;
                font-size: 1.125rem;
                font-weight: 700;
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
                padding-bottom: 0.75rem;
            }

            /* Leaflet Map Customizing */
            #map {
                height: 500px;
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.05);
                background-color: #0b0f19;
                z-index: 1;
            }

            /* Custom Leaflet Marker Styling */
            .custom-marker {
                background: none !important;
                border: none !important;
            }

            .marker-dot {
                width: 14px;
                height: 14px;
                border-radius: 50%;
                border: 2.5px solid #ffffff;
                position: relative;
                box-shadow: 0 0 12px rgba(0,0,0,0.8);
                transition: all 0.3s ease;
            }

            .marker-label {
                position: absolute;
                top: -24px;
                left: 50%;
                transform: translateX(-50%);
                white-space: nowrap;
                font-size: 0.65rem;
                font-weight: 700;
                color: var(--text-primary);
                background: rgba(11, 15, 25, 0.95);
                padding: 2px 6px;
                border-radius: 4px;
                border: 1px solid var(--card-border);
                font-family: 'Space Grotesk', sans-serif;
                box-shadow: 0 2px 8px rgba(0,0,0,0.5);
                pointer-events: none;
            }

            .marker-pulse {
                position: absolute;
                top: -6px;
                left: -6px;
                width: 22px;
                height: 22px;
                border-radius: 50%;
                opacity: 0;
                pointer-events: none;
            }

            @keyframes markerPulse {
                0% { transform: scale(0.5); opacity: 0.8; }
                100% { transform: scale(2.5); opacity: 0; }
            }

            .marker-pulse-cyan { border: 2.5px solid var(--accent-cyan); animation: markerPulse 1.6s infinite; }
            .marker-pulse-amber { border: 2.5px solid var(--accent-amber); animation: markerPulse 1.6s infinite; }
            .marker-pulse-red { border: 2.5px solid var(--accent-red); animation: markerPulse 1.1s infinite; }
            .marker-pulse-blue { border: 2.5px solid var(--accent-blue); animation: markerPulse 1.6s infinite; }

            /* Animated flows on polyline connections */
            @keyframes flow {
                to {
                    stroke-dashoffset: -20;
                }
            }
            .active-path {
                stroke-dasharray: 6, 8;
                animation: flow 1.2s linear infinite;
                stroke: var(--accent-cyan) !important;
            }

            /* Timeline Panel Styling */
            .timeline-panel {
                display: flex;
                flex-direction: column;
                gap: 1.25rem;
                position: relative;
            }

            .timeline-panel::before {
                content: '';
                position: absolute;
                left: 17px;
                top: 8px;
                bottom: 8px;
                width: 2px;
                background: rgba(255, 255, 255, 0.05);
            }

            .timeline-item {
                display: flex;
                gap: 1.25rem;
                align-items: flex-start;
                opacity: 0.4;
                transition: all 0.3s;
            }

            .timeline-item.active {
                opacity: 1;
            }

            .timeline-icon {
                width: 36px;
                height: 36px;
                border-radius: 50%;
                background: #1f2937;
                border: 2px solid rgba(255, 255, 255, 0.1);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 0.875rem;
                z-index: 10;
                transition: all 0.3s;
            }

            .timeline-item.active .timeline-icon {
                background: var(--accent-blue);
                border-color: rgba(255, 255, 255, 0.2);
                box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
            }

            .timeline-item.active.completed .timeline-icon {
                background: var(--accent-emerald);
                box-shadow: 0 0 10px rgba(16, 185, 129, 0.3);
            }

            .timeline-item.active.danger .timeline-icon {
                background: var(--accent-red);
                box-shadow: 0 0 10px rgba(244, 63, 94, 0.3);
            }

            .timeline-item.active.warning .timeline-icon {
                background: var(--accent-amber);
                box-shadow: 0 0 10px rgba(245, 158, 11, 0.3);
            }

            .timeline-info {
                display: flex;
                flex-direction: column;
                gap: 0.125rem;
            }

            .timeline-info h4 {
                font-family: 'Space Grotesk', sans-serif;
                font-size: 0.937rem;
                font-weight: 700;
            }

            .timeline-info p {
                font-size: 0.812rem;
                color: var(--text-secondary);
            }

            /* Live Terminal */
            .terminal-container {
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            }

            .terminal-header {
                display: flex;
                justify-content: space-between;
                font-size: 0.75rem;
                color: var(--text-secondary);
                text-transform: uppercase;
                font-weight: 600;
                letter-spacing: 0.05em;
            }

            .terminal {
                background: #020617;
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                font-family: 'Space Grotesk', monospace;
                padding: 1.25rem;
                height: 250px;
                overflow-y: auto;
                white-space: pre-wrap;
                font-size: 0.812rem;
                line-height: 1.6;
                box-shadow: inset 0 2px 8px rgba(0,0,0,0.8);
            }

            /* Grid fields */
            .grid-list {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
                gap: 1rem;
            }

            .list-item {
                display: flex;
                flex-direction: column;
                gap: 0.125rem;
                background: rgba(255, 255, 255, 0.015);
                padding: 0.625rem 0.875rem;
                border-radius: 8px;
                border-left: 3px solid var(--accent-blue);
                backdrop-filter: blur(8px);
                border-top: 1px solid rgba(255,255,255,0.01);
                border-right: 1px solid rgba(255,255,255,0.01);
                border-bottom: 1px solid rgba(255,255,255,0.01);
            }

            .list-item label {
                font-size: 0.65rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                color: var(--text-secondary);
                font-weight: 600;
            }

            .list-item span {
                font-weight: 600;
                font-size: 0.875rem;
            }

            /* Leaflet custom dark theme fixes */
            .leaflet-bar {
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
                box-shadow: none !important;
            }
            .leaflet-bar a {
                background-color: rgba(17, 24, 39, 0.9) !important;
                color: var(--text-primary) !important;
                border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
            }
            .leaflet-bar a:hover {
                background-color: var(--accent-blue) !important;
            }
        </style>
    </head>
    <body>
        <header>
            <div class="logo-container">
                <div class="logo-icon">
                    <i class="fa-solid fa-shield-halved"></i>
                </div>
                <h1>SentinelAI — Agentic Safety Network</h1>
            </div>
            <div style="display: flex; gap: 1rem; align-items: center;">
                <select id="scenario-selector" style="background: rgba(17, 24, 39, 0.95); border: 1px solid var(--card-border); color: var(--text-primary); padding: 0.625rem 1rem; border-radius: 8px; font-family: inherit; font-size: 0.875rem; font-weight: 600; cursor: pointer; outline: none; transition: border 0.3s; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
                    <option value="suspicious_following">Scenario 1: Suspicious Following</option>
                    <option value="normal_movement">Scenario 2: Normal Movement</option>
                    <option value="blind_spot_disappearance">Scenario 3: Blind Spot Disappearance</option>
                    <option value="crowd_anomaly">Scenario 4: Crowd Anomaly</option>
                    <option value="false_alarm">Scenario 5: False Alarm</option>
                    <option value="video_feed_sync">Scenario 6: Video Feed Sync (CV Detection)</option>
                    <option value="video_feed_suspicious_following">Scenario 7: Video Feed - Suspicious Follow & Disappearance</option>
                </select>
                <button class="btn" onclick="startSimulation()">
                    <i class="fa-solid fa-play"></i> Run Scenario
                </button>
            </div>
        </header>

        <div class="main-content">
            <!-- Row 1: Live Metrics Cards -->
            <div class="metrics-row">
                <div class="metric-card">
                    <div class="metric-info">
                        <label>Risk Level</label>
                        <div class="value" id="risk-score">0.0</div>
                    </div>
                    <div class="metric-icon" id="risk-icon" style="background: var(--glow-emerald); color: var(--accent-emerald);">
                        <i class="fa-solid fa-triangle-exclamation"></i>
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-info">
                        <label>Prediction Accuracy</label>
                        <div class="value" id="accuracy-val">92.4%</div>
                    </div>
                    <div class="metric-icon" style="background: var(--glow-cyan); color: var(--accent-cyan);">
                        <i class="fa-solid fa-chart-line"></i>
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-info">
                        <label>Emergency Dispatch</label>
                        <div class="value" id="dispatched-patrol">None</div>
                    </div>
                    <div class="metric-icon" id="patrol-icon" style="background: rgba(255,255,255,0.03); color: var(--text-secondary);">
                        <i class="fa-solid fa-truck-medical"></i>
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-info">
                        <label>Sweep Coverage</label>
                        <div class="value" id="coverage-val">Idle</div>
                    </div>
                    <div class="metric-icon" id="coverage-icon" style="background: rgba(255,255,255,0.03); color: var(--text-secondary);">
                        <i class="fa-solid fa-radar"></i>
                    </div>
                </div>
            </div>

            <!-- Row 2: Columns Grid -->
            <div class="columns-grid">
                <!-- Column Left: Map & Entity Metadata -->
                <div style="display:flex; flex-direction:column; gap:2rem;">
                    <div class="card">
                        <div class="card-title">
                            <span>Target Tracking State</span>
                            <span id="state-badge" class="badge badge-success">Standby</span>
                        </div>
                        <div class="grid-list">
                            <div class="list-item"><label>Tracked ID</label><span id="entity-id">None</span></div>
                            <div class="list-item"><label>Last Seen Camera</label><span id="last-camera">None</span></div>
                            <div class="list-item"><label>Clothing Color</label><span id="clothing">None</span></div>
                            <div class="list-item"><label>Movement Pattern</label><span id="pattern">None</span></div>
                        </div>
                    </div>
                    <div class="card">
                        <div class="card-title">Live City Surveillance Map</div>
                        <div id="map"></div>
                    </div>
                    <div class="card">
                        <div class="card-title">Live Video Surveillance Streams</div>
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
                            <div style="background:#0b0f19; border: 1px solid var(--card-border); border-radius: 8px; padding: 0.5rem; text-align: center;">
                                <div style="font-size: 0.7rem; color: var(--text-secondary); margin-bottom: 0.25rem; font-weight: 700;">CAM A</div>
                                <img src="/video_feed/Camera_A" style="width: 100%; height: auto; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05); transition: all 0.3s; opacity: 0.5;" id="stream-A" />
                            </div>
                            <div style="background:#0b0f19; border: 1px solid var(--card-border); border-radius: 8px; padding: 0.5rem; text-align: center;">
                                <div style="font-size: 0.7rem; color: var(--text-secondary); margin-bottom: 0.25rem; font-weight: 700;">CAM B</div>
                                <img src="/video_feed/Camera_B" style="width: 100%; height: auto; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05); transition: all 0.3s; opacity: 0.5;" id="stream-B" />
                            </div>
                            <div style="background:#0b0f19; border: 1px solid var(--card-border); border-radius: 8px; padding: 0.5rem; text-align: center;">
                                <div style="font-size: 0.7rem; color: var(--text-secondary); margin-bottom: 0.25rem; font-weight: 700;">CAM C</div>
                                <img src="/video_feed/Camera_C" style="width: 100%; height: auto; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05); transition: all 0.3s; opacity: 0.5;" id="stream-C" />
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Column Right: Incident Timeline, Analytics & Logs -->
                <div style="display:flex; flex-direction:column; gap:2rem;">
                    <!-- Timeline Card -->
                    <div class="card">
                        <div class="card-title">Safety Incident Timeline</div>
                        <div class="timeline-panel">
                            <div class="timeline-item" id="step-detect">
                                <div class="timeline-icon"><i class="fa-solid fa-camera"></i></div>
                                <div class="timeline-info">
                                    <h4>Detection</h4>
                                    <p id="step-detect-desc">Waiting for target sighting...</p>
                                </div>
                            </div>
                            <div class="timeline-item" id="step-predict">
                                <div class="timeline-icon"><i class="fa-solid fa-arrow-trend-up"></i></div>
                                <div class="timeline-info">
                                    <h4>Path Prediction</h4>
                                    <p id="step-predict-desc">Pending trajectory initialization...</p>
                                </div>
                            </div>
                            <div class="timeline-item" id="step-investigate">
                                <div class="timeline-icon"><i class="fa-solid fa-magnifying-glass"></i></div>
                                <div class="timeline-info">
                                    <h4>Anomalous Investigation</h4>
                                    <p id="step-investigate-desc">Active sweep on blind spots...</p>
                                </div>
                            </div>
                            <div class="timeline-item" id="step-risk">
                                <div class="timeline-icon"><i class="fa-solid fa-calculator"></i></div>
                                <div class="timeline-info">
                                    <h4>Dynamic Risk Assessment</h4>
                                    <p id="step-risk-desc">Evaluating behavioral hazard factors...</p>
                                </div>
                            </div>
                            <div class="timeline-item" id="step-dispatch">
                                <div class="timeline-icon"><i class="fa-solid fa-bullhorn"></i></div>
                                <div class="timeline-info">
                                    <h4>Patrol Dispatch</h4>
                                    <p id="step-dispatch-desc">Awaiting incident deployment threshold...</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- System Analytics Dashboard (Persisted in DB) -->
                    <div class="card">
                        <div class="card-title">Operational Performance Analytics</div>
                        <div class="grid-list" style="grid-template-columns: repeat(2, 1fr);">
                            <div class="list-item" style="border-left-color: var(--accent-cyan);"><label>Incidents Handled</label><span id="analytics-incidents">0</span></div>
                            <div class="list-item" style="border-left-color: var(--accent-amber);"><label>Avg Dispatch Time</label><span id="analytics-dispatch-time">0.0 min</span></div>
                            <div class="list-item" style="border-left-color: var(--accent-emerald);"><label>Investigation Success</label><span id="analytics-investigation-rate">0.0%</span></div>
                            <div class="list-item" style="border-left-color: var(--accent-red);"><label>False Positives</label><span id="analytics-false-positives">0</span></div>
                        </div>
                        <div class="list-item" style="border-left-color: var(--accent-blue); margin-top: 0.5rem;">
                            <label>Patrol Unit Utilization</label>
                            <span id="analytics-utilization">0.0%</span>
                        </div>
                        
                        <!-- Tiny Database Snapshot History -->
                        <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.75rem; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 0.75rem;">
                            <div style="font-weight:700; margin-bottom:0.5rem; text-transform:uppercase; letter-spacing:0.05em;">Persisted DB Snapshots (Last 3 runs)</div>
                            <div id="analytics-history" style="display:flex; flex-direction:column; gap:0.375rem;">
                                <div style="color:var(--text-secondary); font-style:italic;">No records found in database.</div>
                            </div>
                        </div>
                    </div>

                    <!-- Logs Card -->
                    <div class="card terminal-container">
                        <div class="terminal-header">
                            <span>Orchestrator Logs</span>
                            <span id="log-timestamp">Live</span>
                        </div>
                        <div class="terminal" id="terminal-feed">> Awaiting system deployment logs...</div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // Leaflet Camera Node Coordinates
            const cameraCoords = {
                "Camera_A": [40.7580, -73.9855],
                "Camera_B": [40.7595, -73.9835],
                "Camera_C": [40.7610, -73.9820],
                "Camera_D": [40.7585, -73.9810],
                "Camera_E": [40.7620, -73.9800],
                "Blind_Spot_1": [40.7570, -73.9795],
                "Blind_Spot_2": [40.7630, -73.9785]
            };

            const connections = [
                ["Camera_A", "Camera_B"],
                ["Camera_B", "Camera_C"],
                ["Camera_B", "Camera_D"],
                ["Camera_C", "Camera_E"],
                ["Camera_D", "Blind_Spot_1"],
                ["Camera_E", "Blind_Spot_2"]
            ];

            // Initialize Map
            const map = L.map('map', {
                zoomControl: true,
                attributionControl: false
            }).setView([40.7595, -73.9825], 15);

            // Dark Matter tile layer
            L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                maxZoom: 20
            }).addTo(map);

            let markerLayer = L.layerGroup().addTo(map);
            let pathLayer = L.layerGroup().addTo(map);

            function getMarkerIcon(camId, isActive, isPredicted, isMissed, isSearched) {
                let color = '#4b5563';
                let pulseClass = '';
                
                if (isMissed) {
                    color = 'var(--accent-red)';
                    pulseClass = 'marker-pulse-red';
                } else if (isActive) {
                    color = 'var(--accent-cyan)';
                    pulseClass = 'marker-pulse-cyan';
                } else if (isPredicted) {
                    color = 'var(--accent-amber)';
                    pulseClass = 'marker-pulse-amber';
                } else if (isSearched) {
                    color = 'var(--accent-blue)';
                    pulseClass = 'marker-pulse-blue';
                }
                
                return L.divIcon({
                    className: 'custom-marker',
                    html: `
                        <div class="marker-dot" style="background-color: ${color};">
                            <div class="marker-pulse ${pulseClass}"></div>
                            <span class="marker-label">${camId.replace('Camera_', 'CAM ').replace('Blind_Spot_', 'SPOT ')}</span>
                        </div>
                    `,
                    iconSize: [14, 14],
                    iconAnchor: [7, 7]
                });
            }

            function drawMap(state) {
                markerLayer.clearLayers();
                pathLayer.clearLayers();

                const activeCam = state.tracked_entity.last_seen_camera;
                const expectedCam = state.prediction.expected_next_camera;
                const status = state.prediction.status;
                const scanned = state.investigation.scanned_cameras || [];
                const blindSpots = state.investigation.blind_spots_checked || [];

                // Draw base connection paths
                connections.forEach(conn => {
                    const latlngs = [cameraCoords[conn[0]], cameraCoords[conn[1]]];
                    let isFlowing = false;

                    // If path is part of active prediction traversal
                    if (activeCam === conn[0] && expectedCam === conn[1] && status === 'PENDING') {
                        isFlowing = true;
                    }

                    L.polyline(latlngs, {
                        color: isFlowing ? 'var(--accent-cyan)' : 'rgba(255,255,255,0.06)',
                        weight: isFlowing ? 4 : 2.5,
                        dashArray: isFlowing ? '6, 8' : '4, 8',
                        className: isFlowing ? 'active-path' : ''
                    }).addTo(pathLayer);
                });

                // Add Node Markers
                for (let camId in cameraCoords) {
                    const latlng = cameraCoords[camId];
                    let isActive = (activeCam === camId);
                    let isPredicted = (expectedCam === camId && status === 'PENDING');
                    let isMissed = (expectedCam === camId && status === 'MISSED');
                    let isSearched = scanned.includes(camId) || blindSpots.includes(camId);

                    const marker = L.marker(latlng, {
                        icon: getMarkerIcon(camId, isActive, isPredicted, isMissed, isSearched)
                    });
                    marker.addTo(markerLayer);
                }
            }

            async function fetchAccuracy() {
                try {
                    const res = await fetch('/learning');
                    const history = await res.json();
                    let success = 0;
                    let trials = 0;
                    history.forEach(item => {
                        success += item.success_count;
                        trials += (item.success_count + item.failure_count);
                    });
                    if (trials > 0) {
                        const score = (success / trials) * 100;
                        document.getElementById('accuracy-val').innerText = score.toFixed(1) + '%';
                    }
                } catch(e) {
                    console.error("Error reading accuracy:", e);
                }
            }

            async function fetchAnalytics() {
                try {
                    const res = await fetch('/analytics');
                    const data = await res.json();
                    if (data.length > 0) {
                        const latest = data[0];
                        document.getElementById('analytics-incidents').innerText = latest.incidents_handled;
                        document.getElementById('analytics-dispatch-time').innerText = latest.avg_dispatch_time.toFixed(1) + ' min';
                        document.getElementById('analytics-investigation-rate').innerText = latest.investigation_success_rate.toFixed(1) + '%';
                        document.getElementById('analytics-false-positives').innerText = latest.false_positives;
                        document.getElementById('analytics-utilization').innerText = latest.patrol_utilization.toFixed(1) + '%';
                        
                        // History list
                        const historyContainer = document.getElementById('analytics-history');
                        historyContainer.innerHTML = '';
                        data.slice(0, 3).forEach((run) => {
                            historyContainer.innerHTML += `
                                <div style="display:flex; justify-content:space-between; font-family:'Space Grotesk', monospace; font-size:0.7rem; background:rgba(255,255,255,0.02); padding:4px 8px; border-radius:4px; border: 1px solid rgba(255,255,255,0.02);">
                                    <span>Run #${run.id} (${run.timestamp.split(' ')[1]})</span>
                                    <span style="color:var(--accent-cyan);">Acc: ${run.prediction_accuracy}% | Util: ${run.patrol_utilization}%</span>
                                </div>
                            `;
                        });
                    }
                } catch(e) {
                    console.error("Error fetching analytics:", e);
                }
            }

            async function fetchState() {
                try {
                    const response = await fetch('/state');
                    const state = await response.json();
                    
                    // Populate main states
                    document.getElementById('entity-id').innerText = state.tracked_entity.id || 'None';
                    document.getElementById('last-camera').innerText = state.tracked_entity.last_seen_camera || 'None';
                    document.getElementById('clothing').innerText = state.tracked_entity.physical_features.clothing_color || 'None';
                    document.getElementById('pattern').innerText = state.tracked_entity.physical_features.movement_pattern || 'None';
                    
                    const score = state.risk_assessment.risk_score || 0.0;
                    document.getElementById('risk-score').innerText = score.toFixed(1);
                    const severityEl = document.getElementById('severity');
                    if (severityEl) severityEl.innerText = state.risk_assessment.severity || 'LOW';
                    const expectedEl = document.getElementById('expected-cam');
                    if (expectedEl) expectedEl.innerText = state.prediction.expected_next_camera || 'None';
                    
                    const patrolVal = state.dispatch_status.patrol_unit_assigned || 'None';
                    document.getElementById('dispatched-patrol').innerText = patrolVal;

                    // Update Metrics Background Indicators
                    const riskIcon = document.getElementById('risk-icon');
                    if (score >= 80) {
                        riskIcon.style.background = 'var(--glow-red)';
                        riskIcon.style.color = 'var(--accent-red)';
                    } else if (score >= 50) {
                        riskIcon.style.background = 'var(--glow-amber)';
                        riskIcon.style.color = 'var(--accent-amber)';
                    } else {
                        riskIcon.style.background = 'var(--glow-emerald)';
                        riskIcon.style.color = 'var(--accent-emerald)';
                    }

                    const patrolIcon = document.getElementById('patrol-icon');
                    if (patrolVal !== 'None') {
                        patrolIcon.style.background = 'var(--glow-emerald)';
                        patrolIcon.style.color = 'var(--accent-emerald)';
                    } else {
                        patrolIcon.style.background = 'rgba(255,255,255,0.03)';
                        patrolIcon.style.color = 'var(--text-secondary)';
                    }

                    // Update Sweep Coverage Card
                    const coverageCard = document.getElementById('coverage-val');
                    const coverageIcon = document.getElementById('coverage-icon');
                    const scannedNodesCount = state.investigation.scanned_cameras.length + state.investigation.blind_spots_checked.length;
                    if (scannedNodesCount > 0) {
                        coverageCard.innerText = `${scannedNodesCount} Zones Swept`;
                        coverageIcon.style.background = 'var(--glow-cyan)';
                        coverageIcon.style.color = 'var(--accent-cyan)';
                    } else {
                        coverageCard.innerText = 'Idle';
                        coverageIcon.style.background = 'rgba(255,255,255,0.03)';
                        coverageIcon.style.color = 'var(--text-secondary)';
                    }

                    // Update status badge
                    const statusBadge = document.getElementById('state-badge');
                    if (state.dispatch_status.alert_sent) {
                        statusBadge.innerText = 'CRITICAL ALERT';
                        statusBadge.className = 'badge badge-danger';
                    } else if (state.prediction.status === 'MISSED') {
                        statusBadge.innerText = 'TARGET MISSING';
                        statusBadge.className = 'badge badge-warning';
                    } else if (state.tracked_entity.id) {
                        statusBadge.innerText = 'ACTIVE TRACK';
                        statusBadge.className = 'badge badge-success';
                    } else {
                        statusBadge.innerText = 'STANDBY';
                        statusBadge.className = 'badge badge-success';
                    }

                    // Update Map
                    drawMap(state);

                    // Update Dynamic Timeline Panels
                    updateTimeline(state);
                    
                    // Fetch accurate learning metrics
                    await fetchAccuracy();
                    
                    // Fetch database persisted analytics snapshots
                    await fetchAnalytics();

                    // Highlight active camera stream frame
                    const activeCam = state.tracked_entity.last_seen_camera;
                    ['A', 'B', 'C'].forEach(id => {
                        const img = document.getElementById(`stream-${id}`);
                        if (img) {
                            if (activeCam === `Camera_${id}`) {
                                img.style.borderColor = 'var(--accent-cyan)';
                                img.style.boxShadow = '0 0 16px var(--accent-cyan)';
                                img.style.opacity = '1.0';
                            } else {
                                img.style.borderColor = 'rgba(255,255,255,0.05)';
                                img.style.boxShadow = 'none';
                                img.style.opacity = '0.4';
                            }
                        }
                    });
                } catch (e) {
                    console.error("Error fetching state:", e);
                }
            }

            function updateTimeline(state) {
                const detect = document.getElementById('step-detect');
                const predict = document.getElementById('step-predict');
                const investigate = document.getElementById('step-investigate');
                const risk = document.getElementById('step-risk');
                const dispatch = document.getElementById('step-dispatch');

                // Step 1: Detection
                if (state.tracked_entity.id) {
                    detect.classList.add('active', 'completed');
                    document.getElementById('step-detect-desc').innerText = `Target detected at ${state.tracked_entity.last_seen_camera}.`;
                } else {
                    detect.classList.remove('active', 'completed');
                    document.getElementById('step-detect-desc').innerText = 'Waiting for target sighting...';
                }

                // Step 2: Prediction
                if (state.prediction.expected_next_camera) {
                    predict.classList.add('active');
                    if (state.prediction.status === 'COMPLETED') {
                        predict.classList.add('completed');
                        document.getElementById('step-predict-desc').innerText = `Path completed at expected destination ${state.prediction.expected_next_camera}.`;
                    } else if (state.prediction.status === 'MISSED') {
                        predict.classList.add('completed');
                        document.getElementById('step-predict-desc').innerText = `Target missed arrival ETA at expected camera ${state.prediction.expected_next_camera}.`;
                    } else {
                        predict.classList.remove('completed');
                        document.getElementById('step-predict-desc').innerText = `Destination estimated: ${state.prediction.expected_next_camera} (ETA: ${state.prediction.eta_seconds}s).`;
                    }
                } else {
                    predict.classList.remove('active', 'completed');
                    document.getElementById('step-predict-desc').innerText = 'Pending trajectory initialization...';
                }

                // Step 3: Investigation
                if (state.investigation.scanned_cameras.length > 0 || state.investigation.blind_spots_checked.length > 0) {
                    investigate.classList.add('active', 'completed');
                    document.getElementById('step-investigate-desc').innerText = `Swept ${state.investigation.scanned_cameras.length} nodes & ${state.investigation.blind_spots_checked.length} blind spot. Result: EMPTY.`;
                } else {
                    investigate.classList.remove('active', 'completed');
                    document.getElementById('step-investigate-desc').innerText = 'Awaiting prediction status updates...';
                }

                // Step 4: Risk
                if (state.risk_assessment.risk_score > 0) {
                    risk.classList.add('active');
                    if (state.risk_assessment.risk_score >= 80) {
                        risk.classList.add('danger');
                        risk.classList.remove('warning');
                    } else {
                        risk.classList.remove('danger');
                        risk.classList.add('warning');
                    }
                    document.getElementById('step-risk-desc').innerText = `Score evaluated: ${state.risk_assessment.risk_score.toFixed(1)} (${state.risk_assessment.severity}).`;
                } else {
                    risk.classList.remove('active', 'danger', 'warning');
                    document.getElementById('step-risk-desc').innerText = 'Evaluating behavioral hazard factors...';
                }

                // Step 5: Dispatch
                if (state.dispatch_status.alert_sent) {
                    dispatch.classList.add('active', 'danger');
                    document.getElementById('step-dispatch-desc').innerText = `Emergency alert sent! ${state.dispatch_status.patrol_unit_assigned} dispatched.`;
                } else {
                    dispatch.classList.remove('active', 'danger');
                    document.getElementById('step-dispatch-desc').innerText = 'Awaiting incident deployment threshold...';
                }
            }

            async function startSimulation() {
                const term = document.getElementById('terminal-feed');
                const selector = document.getElementById('scenario-selector');
                const scenario = selector.value;
                term.innerHTML = `Initializing simulator scenario: [${scenario.toUpperCase()}]...\\n`;
                
                try {
                    const res = await fetch(`/simulate?scenario_type=${scenario}`, { method: 'POST' });
                    const data = await res.json();
                    
                    term.innerHTML = "";
                    data.logs.forEach(line => {
                        let cls = 'log-info';
                        if (line.includes('[RiskAgent]')) cls = 'log-warning';
                        if (line.includes('[DispatchAgent]')) cls = 'log-danger';
                        if (line.includes('Agent]')) cls = 'log-agent';
                        
                        term.innerHTML += `<div class="log-line ${cls}">${line}</div>`;
                    });
                    
                    // Force state pull immediately
                    await fetchState();
                } catch(e) {
                    term.innerHTML += `\\nError during simulation: ${e.message}`;
                }
            }

            // Poll state every 3 seconds
            setInterval(fetchState, 3000);
            fetchState();
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
