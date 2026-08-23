import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

def create_rookie_pdf():
    pdf_filename = "ROOKIE_GUIDE_AND_OVERVIEW.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Color Palette
    PRIMARY = colors.HexColor("#0f172a")       # Slate 900
    ACCENT = colors.HexColor("#4f46e5")        # Indigo 600
    TEXT_MAIN = colors.HexColor("#334155")     # Slate 700
    BG_CARD = colors.HexColor("#f8fafc")       # Slate 50
    BG_CODE = colors.HexColor("#1e293b")       # Slate 800
    BORDER_COLOR = colors.HexColor("#e2e8f0")  # Slate 200
    SUCCESS_COLOR = colors.HexColor("#10b981") # Emerald 500
    WARNING_COLOR = colors.HexColor("#f59e0b") # Amber 500
    DANGER_COLOR = colors.HexColor("#ef4444")  # Red 500

    title_style = ParagraphStyle(
        'RookieTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=PRIMARY,
        alignment=TA_CENTER,
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        'RookieSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=ACCENT,
        alignment=TA_CENTER,
        spaceAfter=20
    )

    h1_style = ParagraphStyle(
        'RookieH1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'RookieH2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=ACCENT,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'RookieBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=TEXT_MAIN,
        spaceAfter=6
    )

    code_style = ParagraphStyle(
        'RookieCode',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#38bdf8"),
        backColor=BG_CODE,
        borderColor=colors.HexColor("#334155"),
        borderWidth=1,
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=6
    )

    story = []

    # Title Banner
    story.append(Spacer(1, 10))
    story.append(Paragraph("Containerized Monitoring & ML Anomaly Detection", title_style))
    story.append(Paragraph("A Rookie's Complete Guide: Architecture, How it Works & Step-by-Step Usage", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=ACCENT, spaceBefore=0, spaceAfter=15))

    # 1. High Level Overview (What is this project?)
    story.append(Paragraph("1. What is this Project? (High-Level Overview)", h1_style))
    story.append(Paragraph(
        "Imagine you run a popular online website. Thousands of users click buttons, load pages, and checkout every minute. "
        "Normally, if your server gets overloaded or crashes, traditional monitoring alerts you <b>after</b> the outage happens. "
        "This project builds an <b>intelligent monitoring and predictive anomaly detection system</b>. "
        "It continuously measures live performance metrics (request rates, error rates, latency) and uses an <b>AI / Machine Learning model (Isolation Forest)</b> "
        "to score system health in real-time, predicting risk levels (<b>Normal 🟢</b>, <b>Medium Risk 🟡</b>, <b>High Risk 🔴</b>) before a total failure occurs.",
        body_style
    ))

    # 2. System Components (The 7 Pillars)
    story.append(Paragraph("2. The 7 Key Components of the Architecture", h1_style))
    components = [
        ["Component", "Port / Location", "What it Does (Beginner Explanation)"],
        ["Flask App Backend", "Port 5000", "The core web server processing API requests & generating Prometheus metrics."],
        ["ML Prediction Service", "Port 5001", "The AI microservice running Isolation Forest model to evaluate live anomaly scores."],
        ["React Dashboard", "Port 5173", "The developer Web UI with interactive sliders, presets, and live risk meters."],
        ["Prometheus", "Port 9090", "The monitoring database that scrapes metrics every 10-15 seconds."],
        ["Alertmanager", "Port 9093", "The notification engine triggering alerts when ML risk score exceeds thresholds."],
        ["Grafana", "Port 3000", "The visual analytics interface rendering charts for latency, traffic, and error rates."],
        ["Locust Load Tester", "Port 8089", "A tool to simulate 50+ fake users pounding the API to test stress limits."]
    ]
    t_comp = Table(components, colWidths=[120, 90, 290])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_CARD]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 10))

    # 3. How Machine Learning Anomaly Detection Works
    story.append(Paragraph("3. How the AI / ML Anomaly Detection Works", h1_style))
    story.append(Paragraph(
        "The system evaluates <b>4 key features</b> simultaneously:<br/>"
        "• <b>Request Rate (req/s)</b>: How many incoming requests hit the server per second.<br/>"
        "• <b>HTTP Error Rate (err/s)</b>: How many 500 Server Errors occur per second.<br/>"
        "• <b>P90 Latency (seconds)</b>: The response time for 90% of requests (e.g. 0.21s baseline).<br/>"
        "• <b>Requests In-Progress</b>: Active requests currently being handled concurrently.<br/><br/>"
        "The <b>Isolation Forest ML Model</b> evaluates these 4 metrics together against normal baseline data. "
        "Instead of simple rules, it outputs a continuous <b>Anomaly Score (0.0 to 1.0)</b>:<br/>"
        "• <b>0.00 to 0.49</b> $\\rightarrow$ <b>Normal (Code 0)</b>: System operating safely.<br/>"
        "• <b>0.50 to 0.74</b> $\\rightarrow$ <b>Medium Risk (Code 1)</b>: Traffic load or error rate drifting from baseline.<br/>"
        "• <b>0.75 to 1.00</b> $\\rightarrow$ <b>High Risk (Code 2)</b>: Severe metric anomaly detected!",
        body_style
    ))

    story.append(Spacer(1, 10))

    # 4. How to Run the Project (Step-by-Step for Rookies)
    story.append(Paragraph("4. How to Run the Project (Step-by-Step)", h1_style))

    story.append(Paragraph("Option A: Running Locally (Fastest & Easiest for Development)", h2_style))
    story.append(Paragraph("Open 3 separate terminals in VS Code and run the following commands:", body_style))

    run_steps = [
        ("Terminal 1 (Flask App Backend)", "python app/src/app.py", "Starts backend API on http://localhost:5000"),
        ("Terminal 2 (ML Prediction Service)", "python ml_service/app.py", "Starts ML AI Engine on http://localhost:5001"),
        ("Terminal 3 (React Developer Dashboard)", "cd frontend\nnpm run dev", "Launches Developer UI on http://localhost:5173")
    ]
    for term, cmd, desc in run_steps:
        story.append(Paragraph(f"<b>{term}</b> — <i>{desc}</i>", body_style))
        story.append(Paragraph(cmd.replace("\n", "<br/>"), code_style))

    story.append(Paragraph("Option B: Running Containerized with Docker Compose", h2_style))
    story.append(Paragraph("Make sure Docker Desktop is running, open a terminal at project root, and execute:", body_style))
    story.append(Paragraph("docker-compose up --build", code_style))

    story.append(Spacer(1, 10))

    # 5. How to Use the React Dashboard (User Guide)
    story.append(Paragraph("5. How to Use the React Developer Dashboard", h1_style))
    story.append(Paragraph(
        "Open <b>http://localhost:5173/</b> in your browser. You will see two main tabs:",
        body_style
    ))

    story.append(Paragraph("Tab 1: ML Intelligence (Anomaly Simulator)", h2_style))
    story.append(Paragraph(
        "• <b>Header Status Indicators</b>: Shows if API is <code>Online</code> and ML Engine is <code>Active</code>.<br/>"
        "• <b>Status Card</b>: Displays the large live status (<b>Normal</b>, <b>Medium Risk</b>, or <b>High Risk</b>).<br/>"
        "• <b>Anomaly Score Meter</b>: A continuous progress bar showing the raw score between 0.00 and 1.00.<br/>"
        "• <b>Preset Cards</b>: Click <i>Normal Baseline</i>, <i>Ramp Up Load</i>, <i>Traffic Spike</i>, or <i>Heavy Error Storm</i> to test instant load profiles.<br/>"
        "• <b>Interactive Sliders</b>: Move sliders to test custom numbers. <b>Crucial Note</b>: After moving sliders, click the <b>'Evaluate Custom Inputs'</b> button to send values to the ML service!",
        body_style
    ))

    story.append(Paragraph("Tab 2: API Tester", h2_style))
    story.append(Paragraph(
        "Click endpoint buttons to test live HTTP responses:<br/>"
        "• <code>/health</code>: Returns 200 OK (Healthy).<br/>"
        "• <code>/process</code>: Simulates short data processing task.<br/>"
        "• <code>/slow</code>: Simulates delayed 2-second response (used to test latency graphs).<br/>"
        "• <code>/error</code>: Deliberately triggers a 500 server error (used to test error alerts).<br/>"
        "• <code>/metrics</code>: Returns raw Prometheus metric exposition text.",
        body_style
    ))

    story.append(Spacer(1, 10))

    # 6. How to Trigger High Risk & Test Load Swarms
    story.append(Paragraph("6. Rookie Experiments to Try Right Now!", h1_style))
    
    experiments = [
        ("Experiment 1: How to Trigger HIGH RISK Status in Dashboard", [
            "1. Go to ML Intelligence tab in http://localhost:5173.",
            "2. Set all 4 sliders to zero (Request Rate = 0, Error Rate = 0, P90 Latency = 0.01s, In-Progress = 0).",
            "3. Click 'Evaluate Custom Inputs'.",
            "4. Result: Anomaly Score jumps to ~0.98 - 1.00 (HIGH RISK 🔴) because zero activity is extreme out-of-distribution anomaly!"
        ]),
        ("Experiment 2: Simulate 50 Fake Users with Locust", [
            "1. Open a new terminal:  cd load-testing/locust/scripts",
            "2. Run Locust:  locust -f locustfile.py --host=http://localhost:5000",
            "3. Open http://localhost:8089 in browser, set 50 Users, spawn rate 5, and click Start Swarm.",
            "4. Watch live request metrics flow through Flask, ML service, and Prometheus!"
        ])
    ]
    for title, steps_list in experiments:
        story.append(Paragraph(title, h2_style))
        for step in steps_list:
            if "cd " in step or "locust " in step:
                story.append(Paragraph(f"<code>{step}</code>", code_style))
            else:
                story.append(Paragraph(step, body_style))

    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER_COLOR, spaceBefore=10, spaceAfter=10))
    story.append(Paragraph("<b>Containerized Monitoring & ML Anomaly System — Complete Rookie Guide</b>", ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor("#64748b"))))

    doc.build(story)
    print(f"Rookie PDF generated: {os.path.abspath(pdf_filename)}")

if __name__ == "__main__":
    create_rookie_pdf()
