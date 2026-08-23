import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

def create_pdf():
    pdf_filename = "STEP_BY_STEP_RUNBOOK.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    PRIMARY = colors.HexColor("#1e1b4b")       # Dark Indigo
    SECONDARY = colors.HexColor("#4338ca")     # Indigo Accent
    TEXT_COLOR = colors.HexColor("#1e293b")    # Slate 800
    BG_LIGHT = colors.HexColor("#f8fafc")      # Slate 50
    CARD_BG = colors.HexColor("#f1f5f9")       # Slate 100
    BORDER_COLOR = colors.HexColor("#cbd5e1")  # Slate 300
    SUCCESS_COLOR = colors.HexColor("#059669") # Emerald 600

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=PRIMARY,
        alignment=TA_CENTER,
        spaceAfter=15
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=SECONDARY,
        alignment=TA_CENTER,
        spaceAfter=25
    )

    h1_style = ParagraphStyle(
        'Heading1Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=SECONDARY,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=TEXT_COLOR,
        spaceAfter=6
    )

    code_style = ParagraphStyle(
        'CodeStyleCustom',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#0f172a"),
        backColor=CARD_BG,
        borderColor=BORDER_COLOR,
        borderWidth=1,
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=8
    )

    story = []

    # Title & Header Banner
    story.append(Spacer(1, 10))
    story.append(Paragraph("Containerized Monitoring & ML Anomaly System", title_style))
    story.append(Paragraph("Complete Step-by-Step VS Code Runbook & Architecture Verification Guide", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=SECONDARY, spaceBefore=0, spaceAfter=15))

    # Section 1: System Overview & Architecture
    story.append(Paragraph("1. System Architecture & Overview", h1_style))
    story.append(Paragraph(
        "This project implements an end-to-end predictive error detection layer on top of a containerized application monitoring stack. "
        "Locust generates synthetic user traffic (Normal, Ramp, Spike, Heavy Load), Prometheus collects system metrics, an Isolation Forest ML service "
        "evaluates metric vectors to produce real-time anomaly scores, Alertmanager triggers predictive alerts, and a React Developer Dashboard displays live health scores.",
        body_style
    ))

    # Architecture Flow Diagram Table
    arch_flow = [
        ["Locust Traffic Generator", "→", "Flask Web Application", "→", "Prometheus Metrics"],
        ["Prometheus Metrics", "→", "ML Isolation Forest", "→", "Predictive Anomaly Score"],
        ["Anomaly Score (0.0-1.0)", "→", "Alertmanager Warnings", "→", "React / Grafana Dashboard"]
    ]
    t_arch = Table(arch_flow, colWidths=[150, 20, 150, 20, 150])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
        ('TEXTCOLOR', (0,0), (-1,-1), PRIMARY),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 12))

    # Section 2: Prerequisites
    story.append(Paragraph("2. Prerequisites & Tools Required", h1_style))
    prereqs = [
        ["Tool", "Required Version", "Purpose"],
        ["VS Code", "Latest", "Development & Terminal Execution"],
        ["Python", "3.10+", "Flask App & Isolation Forest ML Service"],
        ["Node.js / npm", "18+", "React Developer Dashboard (Vite)"],
        ["Docker Desktop", "Latest", "Containerized Multi-Service Deployment"],
        ["Git", "Latest", "Version Control & GitHub Sync"]
    ]
    t_prereq = Table(prereqs, colWidths=[120, 120, 280])
    t_prereq.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_prereq)
    story.append(Spacer(1, 14))

    # Section 3: Step-by-Step Execution Guide
    story.append(Paragraph("3. Step-by-Step Execution Guide in VS Code", h1_style))

    steps = [
        ("Step 1: Open Project in VS Code", [
            "1. Open VS Code.",
            "2. Select File > Open Folder... and choose: c:\\Users\\aksha\\Downloads\\containerized-monitoring-system-main",
            "3. Open integrated terminal using Ctrl + ~."
        ]),
        ("Step 2: Train Model & Launch ML Microservice (Port 5001)", [
            "1. In VS Code terminal, navigate to ml_service:  cd ml_service",
            "2. Install dependencies:  pip install -r requirements.txt",
            "3. Train Isolation Forest model:  python train.py",
            "4. Start ML prediction service:  python app.py",
            "   → ML Service listens at http://localhost:5001"
        ]),
        ("Step 3: Start Application Backend (Port 5000)", [
            "1. Open a new terminal tab in VS Code (Ctrl + Shift + ~).",
            "2. Run Flask application:  python app/src/app.py",
            "   → Backend API listens at http://localhost:5000"
        ]),
        ("Step 4: Launch React Developer Dashboard (Port 5173)", [
            "1. Open a new terminal tab in VS Code.",
            "2. Navigate to frontend folder:  cd frontend",
            "3. Install node packages:  npm install",
            "4. Start Vite dev server:  npm run dev",
            "   → Open browser at http://localhost:5173"
        ]),
        ("Step 5: Run Full Docker Monitoring Stack", [
            "1. Ensure Docker Desktop is running.",
            "2. In root terminal, execute:  docker-compose up --build",
            "   → Builds and starts Flask App, ML Service, Prometheus, Alertmanager, Grafana."
        ]),
        ("Step 6: Run Locust Load Testing", [
            "1. In a new terminal tab, navigate to load-testing/locust/scripts:  cd load-testing/locust/scripts",
            "2. Launch Locust:  locust -f locustfile.py --host=http://localhost:5000",
            "3. Open http://localhost:8089, set 50 Users, spawn rate 5, and click Start Swarm."
        ])
    ]

    for title, details in steps:
        story.append(Paragraph(title, h2_style))
        for line in details:
            if line.startswith("   →") or "cd " in line or "python " in line or "npm " in line or "docker-compose" in line:
                story.append(Paragraph(f"<code>{line}</code>", code_style))
            else:
                story.append(Paragraph(line, body_style))

    story.append(Spacer(1, 10))

    # Section 4: Dashboard Verification & Cheat Sheet
    story.append(Paragraph("4. Port & Service Directory Cheat Sheet", h1_style))
    ports = [
        ["Service", "Port", "URL", "Description"],
        ["Flask App", "5000", "http://localhost:5000", "Backend API & Prometheus Metrics"],
        ["ML Service", "5001", "http://localhost:5001", "Isolation Forest ML Prediction Microservice"],
        ["React Dashboard", "5173", "http://localhost:5173", "ML Intelligence Dashboard & Simulator"],
        ["Prometheus", "9090", "http://localhost:9090", "Time-series Metrics & Alert Evaluation"],
        ["Alertmanager", "9093", "http://localhost:9093", "Predictive Alert Notifications"],
        ["Grafana", "3000", "http://localhost:3000", "Visual Infrastructure Dashboards"],
        ["Locust UI", "8089", "http://localhost:8089", "Synthetic Load Testing Controller"]
    ]
    t_ports = Table(ports, colWidths=[100, 45, 145, 230])
    t_ports.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), SECONDARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_ports)

    # Build Document
    doc.build(story)
    print(f"PDF successfully generated: {os.path.abspath(pdf_filename)}")

if __name__ == "__main__":
    create_pdf()
