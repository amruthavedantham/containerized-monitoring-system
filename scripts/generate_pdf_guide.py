import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Canvas that computes total pages dynamically for clean page numbering."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(36, 11 * inch - 26, "Containerized Monitoring & Alerting System • Quick-Start Runbook")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(36, 11 * inch - 30, 8.5 * inch - 36, 11 * inch - 30)

        # Footer (all pages)
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(36, 32, 8.5 * inch - 36, 32)

        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawString(36, 20, "Containerized DevOps System • Verified for Windows, Docker & Linux")
        self.drawRightString(8.5 * inch - 36, 20, page_str)
        self.restoreState()


def build_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=40,
        bottomMargin=42
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a")
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#64748b")
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1e1b4b"),
        spaceBefore=12,
        spaceAfter=4
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#334155"),
        spaceBefore=6,
        spaceAfter=2
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#1e293b")
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=12,
        bulletIndent=4,
        spaceAfter=2
    )

    code_style = ParagraphStyle(
        'CodeBlock',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#f8fafc")
    )

    callout_style = ParagraphStyle(
        'Callout',
        parent=body_style,
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#1e293b")
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=body_style,
        fontSize=7.8,
        leading=10
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=body_style,
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#1e293b")
    )

    def code_box(code_text):
        p = Paragraph(code_text.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style)
        t = Table([[p]], colWidths=[7.5 * inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#0f172a")),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('CORNERPAD', (0, 0), (-1, -1), 4),
        ]))
        return t

    def callout_box(text, bg_color="#f8fafc", bar_color="#4f46e5"):
        p = Paragraph(text, callout_style)
        t = Table([[p]], colWidths=[7.5 * inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(bg_color)),
            ('LINEBEFORE', (0, 0), (0, -1), 3.5, colors.HexColor(bar_color)),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        return t

    story = []

    # Title block
    story.append(Paragraph("Containerized Monitoring & Alerting System", title_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph("System Run Sheet & Quick-Reference Guide • Docker Compose, Local Run, Locust Demos & ML Dashboard", subtitle_style))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#4f46e5"), spaceBefore=2, spaceAfter=8))

    # 1. Services Table
    story.append(Paragraph("1. System Services & Access URLs", h1_style))
    services_data = [
        [Paragraph("Service", table_header), Paragraph("Container", table_header), Paragraph("Port", table_header), Paragraph("Access URL", table_header), Paragraph("Key Role", table_header)],
        [Paragraph("<b>React Frontend</b>", table_cell), Paragraph("<code>react_frontend</code>", table_cell), Paragraph("<b>5173</b>", table_cell), Paragraph("<code>http://localhost:5173</code>", table_cell), Paragraph("ML Intelligence, Live Input Graph & Locust Demo Runner", table_cell)],
        [Paragraph("<b>Flask App</b>", table_cell), Paragraph("<code>flask_app</code>", table_cell), Paragraph("<b>5000</b>", table_cell), Paragraph("<code>http://localhost:5000</code>", table_cell), Paragraph("Instrumented REST API, Prometheus /metrics & Demo API", table_cell)],
        [Paragraph("<b>ML Service</b>", table_cell), Paragraph("<code>ml_service</code>", table_cell), Paragraph("<b>5001</b>", table_cell), Paragraph("<code>http://localhost:5001</code>", table_cell), Paragraph("Isolation Forest Anomaly Engine (/predict & metrics)", table_cell)],
        [Paragraph("<b>Locust UI</b>", table_cell), Paragraph("<code>locust</code>", table_cell), Paragraph("<b>8089</b>", table_cell), Paragraph("<code>http://localhost:8089</code>", table_cell), Paragraph("Load generator & scenario execution web UI", table_cell)],
        [Paragraph("<b>Prometheus</b>", table_cell), Paragraph("<code>prometheus</code>", table_cell), Paragraph("<b>9090</b>", table_cell), Paragraph("<code>http://localhost:9090</code>", table_cell), Paragraph("TSDB scraping <code>flask_app</code> & <code>ml_service</code>, alert rules", table_cell)],
        [Paragraph("<b>Grafana</b>", table_cell), Paragraph("<code>grafana</code>", table_cell), Paragraph("<b>3000</b>", table_cell), Paragraph("<code>http://localhost:3000</code>", table_cell), Paragraph("Pre-provisioned dashboards (login: <code>admin / admin</code>)", table_cell)],
        [Paragraph("<b>Alertmanager</b>", table_cell), Paragraph("<code>alertmanager</code>", table_cell), Paragraph("<b>9093</b>", table_cell), Paragraph("<code>http://localhost:9093</code>", table_cell), Paragraph("Receives, groups and manages Prometheus alert triggers", table_cell)],
    ]
    srv_table = Table(services_data, colWidths=[1.1 * inch, 1.1 * inch, 0.55 * inch, 1.75 * inch, 3.0 * inch])
    srv_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e0e7ff")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ]))
    story.append(srv_table)
    story.append(Spacer(1, 6))

    # 2. Docker Compose Section
    story.append(Paragraph("2. Method 1: Running with Docker Compose (Recommended)", h1_style))
    story.append(Paragraph("Builds, provisions, and networks all 7 services in containers via the <code>monitoring_net</code> bridge network:", body_style))
    story.append(Spacer(1, 2))
    story.append(code_box("# From project root:\ndocker compose down\ndocker compose up --build\n\n# Or run in detached background mode:\ndocker compose up --build -d"))
    story.append(Spacer(1, 3))
    story.append(callout_box("<b>Verification:</b> Open <code>http://localhost:5173</code> in your browser. The API badge will show <b>Online</b> and ML Engine will show <b>Active</b>. Open <code>http://localhost:9090/targets</code> to confirm both <code>flask_app</code> and <code>ml_service</code> are UP.", "#f0fdf4", "#10b981"))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>To Stop All Containers:</b> <code>docker compose down</code>", body_style))
    story.append(Spacer(1, 6))

    # 3. Local Development Mode Section
    story.append(Paragraph("3. Method 2: Running Locally (Development Mode)", h1_style))
    story.append(Paragraph("If developing or testing without Docker Desktop, launch each service in its own terminal:", body_style))
    story.append(Spacer(1, 2))

    local_steps = [
        [Paragraph("<b>Terminal 1: Flask Backend (5000)</b><br/><code>python app/src/app.py</code><br/><font color='#64748b'>Listens on :5000 with metrics & demo endpoints.</font>", table_cell),
         Paragraph("<b>Terminal 2: ML Service (5001)</b><br/><code>python ml_service/app.py</code><br/><font color='#64748b'>Loads Isolation Forest model & serves /predict.</font>", table_cell)],
        [Paragraph("<b>Terminal 3: React Frontend (5173)</b><br/><code>cd frontend &amp;&amp; npm run dev</code><br/><font color='#64748b'>Vite dev server with proxies to :5000 and :5001.</font>", table_cell),
         Paragraph("<b>Terminal 4: Locust (Optional Web UI)</b><br/><code>cd load-testing\\locust\\scripts &amp;&amp; locust -f locustfile.py</code><br/><font color='#64748b'>Locust web UI at http://localhost:8089.</font>", table_cell)],
    ]
    local_table = Table(local_steps, colWidths=[3.75 * inch, 3.75 * inch])
    local_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(local_table)

    # Page Break for clean multi-page PDF layout
    story.append(PageBreak())

    # 4. Locust 1-Minute Demos Section
    story.append(Paragraph("4. Locust 1-Minute Demonstration Scenarios", h1_style))
    story.append(Paragraph("Two specialized 60-second automated scenarios generate realistic traffic patterns for live alerting demonstration:", body_style))
    story.append(Spacer(1, 3))

    scenarios_data = [
        [Paragraph("Scenario", table_header), Paragraph("Traffic Profile & 3 Phases", table_header), Paragraph("Observed Effects", table_header)],
        [
            Paragraph("<b>demo_latency</b><br/><font color='#b45309'>60 Seconds</font>", table_cell),
            Paragraph("• <b>0–20s:</b> Baseline normal traffic (/process)<br/>• <b>20–40s Spike:</b> Heavy /slow delayed requests surge (40 users)<br/>• <b>40–60s:</b> Normal recovery traffic", table_cell),
            Paragraph("<b>Latency surges to ~2.0s</b> during middle spike.<br/><b>Errors stay at 0%.</b><br/>Demonstrates pure latency degradation.", table_cell)
        ],
        [
            Paragraph("<b>demo_errors</b><br/><font color='#be123c'>60 Seconds</font>", table_cell),
            Paragraph("• <b>0–20s:</b> Baseline normal traffic (/process)<br/>• <b>20–40s Spike:</b> Both /slow AND intentional 500 /error requests surge<br/>• <b>40–60s:</b> Normal recovery traffic", table_cell),
            Paragraph("<b>Latency surges to ~2.0s.</b><br/><b>Errors spike to ~35–45%.</b><br/>Triggers High Risk ML state & critical alerts.", table_cell)
        ],
    ]
    scen_table = Table(scenarios_data, colWidths=[1.2 * inch, 3.8 * inch, 2.5 * inch])
    scen_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e0e7ff")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#fffbeb"), colors.HexColor("#fff1f2")]),
    ]))
    story.append(scen_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph("How to Trigger the Demos:", h2_style))
    story.append(Paragraph("<b>Option A: One-Click from Frontend (Recommended)</b>", body_style))
    story.append(Paragraph("Open <code>http://localhost:5173</code> &rarr; In the <b>Interactive Locust Demo Scenarios</b> card, click either:", bullet_style))
    story.append(Paragraph("• <b>Run Latency Demo</b> (triggers <code>demo_latency</code>)", bullet_style))
    story.append(Paragraph("• <b>Run Latency + Errors Demo</b> (triggers <code>demo_errors</code>)", bullet_style))
    story.append(Paragraph("The UI displays an animated <b>60s countdown</b>, progress bar, real-time KPI metrics, and streams data directly into the Live Metrics Graph.", bullet_style))
    story.append(Spacer(1, 3))

    story.append(Paragraph("<b>Option B: Run via PowerShell CLI</b>", body_style))
    story.append(code_box("cd load-testing\\locust\\scripts\n.\\collect_dataset.ps1 -Scenario demo_latency\n# OR\n.\\collect_dataset.ps1 -Scenario demo_errors"))
    story.append(Spacer(1, 3))

    story.append(Paragraph("<b>Option C: Run via REST API</b>", body_style))
    story.append(code_box("# Trigger demo:\ncurl -X POST http://localhost:5000/api/demos/start -H \"Content-Type: application/json\" -d '{\"scenario\": \"demo_latency\"}'\n\n# Poll live status:\ncurl http://localhost:5000/api/demos/active"))
    story.append(Spacer(1, 3))
    story.append(callout_box("<b>Concurrency Protection:</b> Only 1 demo can run at a time. Trying to start a second demo returns an <code>HTTP 409 Conflict</code> error stating the active demo name and remaining seconds.", "#fffbeb", "#f59e0b"))
    story.append(Spacer(1, 6))

    # 5. Frontend & Observability Features
    story.append(Paragraph("5. Frontend Features & Verification Checklist", h1_style))
    story.append(Paragraph("<b>A. Live Input Metrics Graph (Traffic, Latency, Errors):</b>", h2_style))
    story.append(Paragraph("• Renders real-time SVG curves for Traffic (req/s), Latency (s), and Errors (err/s or %).", bullet_style))
    story.append(Paragraph("• Hover over any point on the chart to view the exact timestamp and values.", bullet_style))
    story.append(Paragraph("• Toggle series pills to isolate or compare individual metrics.", bullet_style))

    story.append(Paragraph("<b>B. Anomaly Simulator & Custom Input Evaluation:</b>", h2_style))
    story.append(Paragraph("• Adjust sliders for Request Rate, Error Rate, Latency, or Concurrency.", bullet_style))
    story.append(Paragraph("• Click <b>Evaluate Custom Inputs</b> &rarr; Status immediately updates to <code>High Risk</code>, <code>Medium Risk</code>, or <code>Normal</code>.", bullet_style))
    story.append(Paragraph("• Click <b>Reset Live</b> to restore real-time background metrics polling.", bullet_style))

    story.append(Paragraph("<b>C. API Offline Red Banner Test:</b>", h2_style))
    story.append(Paragraph("• Stop the Flask backend: <code>docker stop flask_app</code> (or press <code>Ctrl+C</code> in Terminal 1).", bullet_style))
    story.append(Paragraph("• The Status Banner turns <b>RED</b> with <b>Status: App is Down</b>, an <code>OFFLINE</code> badge, and clear downtime alerts.", bullet_style))
    story.append(Paragraph("• Restart the backend &rarr; The card automatically recovers to green/normal.", bullet_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully built: {filename}")

if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_root = os.path.join(out_dir, "HOW_TO_RUN_GUIDE.pdf")
    target_docs = os.path.join(out_dir, "docs", "HOW_TO_RUN_GUIDE.pdf")
    build_pdf(target_root)
    build_pdf(target_docs)
