from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = REPO_ROOT / "output" / "pdf" / "k8s-autoguard-final-report.pdf"

NAVY = colors.HexColor("#102A43")
TEAL = colors.HexColor("#007C7A")
CYAN = colors.HexColor("#D9F3F0")
BLUE = colors.HexColor("#DCEBFA")
INK = colors.HexColor("#243B53")
MUTED = colors.HexColor("#627D98")
WHITE = colors.white


def paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def page_chrome(canvas, document) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(NAVY)
    canvas.rect(0, height - 13 * mm, width, 13 * mm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(18 * mm, height - 8.5 * mm, "K8s AutoGuard | DevSecOps Final Report")
    canvas.setStrokeColor(colors.HexColor("#BCCCDC"))
    canvas.line(18 * mm, 13 * mm, width - 18 * mm, 13 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(18 * mm, 8 * mm, "Portfolio artifact - verified evidence is distinguished from pending live validation.")
    canvas.drawRightString(width - 18 * mm, 8 * mm, f"Page {document.page}")
    canvas.restoreState()


def build_report() -> Path:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    document = BaseDocTemplate(
        str(OUTPUT_PATH),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=22 * mm,
        bottomMargin=20 * mm,
        title="K8s AutoGuard Final Project Report",
        author="Chaabi Nour El Houda",
    )
    frame = Frame(
        document.leftMargin,
        document.bottomMargin,
        document.width,
        document.height,
        id="body",
    )
    document.addPageTemplates(
        [PageTemplate(id="report", frames=[frame], onPage=page_chrome, onPageEnd=page_chrome)]
    )
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=28,
        leading=34,
        textColor=NAVY,
        alignment=TA_LEFT,
        spaceAfter=8,
    )
    subtitle = ParagraphStyle(
        "Subtitle",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=13,
        leading=19,
        textColor=MUTED,
        spaceAfter=16,
    )
    heading = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=20,
        textColor=TEAL,
        spaceBefore=10,
        spaceAfter=7,
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=INK,
        spaceAfter=7,
    )
    small = ParagraphStyle(
        "Small",
        parent=body,
        fontSize=8.2,
        leading=11,
        spaceAfter=0,
    )
    small_header = ParagraphStyle(
        "SmallHeader",
        parent=small,
        fontName="Helvetica-Bold",
        textColor=WHITE,
    )
    callout = ParagraphStyle(
        "Callout",
        parent=body,
        fontName="Helvetica-Bold",
        textColor=NAVY,
        alignment=TA_CENTER,
        spaceAfter=0,
    )

    story = [
        Spacer(1, 18 * mm),
        paragraph("K8s AutoGuard", title),
        paragraph("Local Kubernetes DevSecOps platform for prevention, detection, guarded remediation, and observable evidence.", subtitle),
    ]
    summary = Table(
        [
            [paragraph("Project focus", small), paragraph("Kubernetes security automation and operational evidence", small)],
            [paragraph("Delivery model", small), paragraph("Protected GitHub pull requests and reproducible local infrastructure", small)],
            [paragraph("Author", small), paragraph("Chaabi Nour El Houda", small)],
            [paragraph("Report date", small), paragraph("22 August 2026", small)],
        ],
        colWidths=[43 * mm, 116 * mm],
    )
    summary.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), CYAN),
                ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#F7FBFF")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#9FB3C8")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#BCCCDC")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.extend([summary, Spacer(1, 13 * mm)])
    status = Table(
        [[paragraph("Evidence status", callout)], [paragraph("Repository, policy, model, and CI evidence is verified. Final runtime observability screenshots and video recording remain intentionally pending until Docker Desktop WSL integration is restored.", body)]],
        colWidths=[159 * mm],
    )
    status.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), BLUE),
                ("BACKGROUND", (0, 1), (0, 1), colors.HexColor("#F7FBFF")),
                ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#829AB1")),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    story.extend([status, Spacer(1, 15 * mm), paragraph("Executive Summary", heading)])
    story.append(paragraph("K8s AutoGuard joins identity-aware network policy, admission control, runtime detection, anomaly classification, and narrowly scoped response. The project is designed for learning and portfolio review: every control is versioned, reproducible, and paired with a validation command.", body))
    story.append(PageBreak())

    story.append(paragraph("Architecture and Safety", heading))
    architecture = Table(
        [[paragraph("GitHub PR", small)], [paragraph("Kyverno + Trivy gates", small)], [paragraph("KIND + Cilium + Hubble", small)], [paragraph("Falco runtime event", small)], [paragraph("ML classification", small)], [paragraph("Guarded remediation", small)], [paragraph("Prometheus + Loki + Grafana", small)]],
        colWidths=[159 * mm],
    )
    architecture.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F0F4F8")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#9FB3C8")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#BCCCDC")),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.extend([architecture, Spacer(1, 9 * mm)])
    story.append(paragraph("The response path defaults to dry run. A Cilium isolation policy can be created only for an anomalous, high-risk, high-severity event in the permitted demo namespace. Kubernetes RBAC permits only create, get, and list access to CiliumNetworkPolicies in that namespace.", body))
    story.append(paragraph("Implemented Controls", heading))
    controls = [
        ["Layer", "Implementation", "Evidence"],
        ["Infrastructure", "Two-node KIND, Terraform, Ansible", "Cilium-ready cluster workflow"],
        ["Network", "Cilium + Hubble policy demo", "77 applicable tests, trusted/denied flow"],
        ["Runtime", "Falco modern eBPF", "Controlled event and shell detection"],
        ["Prevention", "Kyverno + Trivy", "Secure allowed, insecure denied, CI gates"],
        ["Detection", "Isolation Forest dataset + API", "520 labelled events, recall 1.00, FPR 0.08"],
        ["Response", "Guarded remediation", "Scoped Cilium policy construction tests"],
        ["Observability", "Prometheus, Loki, Grafana", "Metrics tests, Helm rendering, dashboard config"],
    ]
    control_table = Table(
        [
            [paragraph(cell, small_header if row_index == 0 else small) for cell in row]
            for row_index, row in enumerate(controls)
        ],
        colWidths=[30 * mm, 60 * mm, 69 * mm],
        repeatRows=1,
    )
    control_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F7FBFF")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#9FB3C8")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.extend([control_table, PageBreak()])

    story.append(paragraph("Verified Results", heading))
    for result in [
        "Cilium connectivity validation completed 77 applicable tests and 320 actions.",
        "Falco detected a controlled file operation and an interactive container shell.",
        "Kyverno admitted a Restricted-profile Pod fixture and denied an insecure fixture.",
        "Trivy security gates and Python quality tests passed on protected pull requests.",
        "The synthetic development benchmark measured recall 1.00, false-positive rate 0.08, and P95 in-process classification latency 38.69 ms.",
        "Prometheus metric tests, Grafana dashboard JSON, Kubernetes resource YAML, and pinned Helm templates validated locally.",
    ]:
        story.append(paragraph(f"- {result}", body))
    story.append(paragraph("Limitations", heading))
    story.append(paragraph("The benchmark uses deterministic synthetic security scenarios and is not a production MTTD or MTTR claim. Loki uses disposable local storage and a test schema. Promtail is included for the project brief but is deprecated; Grafana Alloy is the production-oriented successor.", body))
    story.append(paragraph("Final Runtime Acceptance", heading))
    acceptance = [
        ["Step", "Command", "Evidence to capture"],
        ["Deploy APIs", "./scripts/deploy-autoguard-platform.sh", "Healthy ML and remediation Pods"],
        ["Install observability", "./scripts/install-observability.sh", "Healthy monitoring and Loki Pods"],
        ["Run demo", "./scripts/run-final-project-demo.sh --interactive", "Metrics, alerts, Grafana, Loki logs"],
        ["Record video", "Follow docs/demo/final-project-demo.md", "6-8 minute current-session recording"],
    ]
    acceptance_table = Table(
        [
            [paragraph(cell, small_header if row_index == 0 else small) for cell in row]
            for row_index, row in enumerate(acceptance)
        ],
        colWidths=[35 * mm, 70 * mm, 54 * mm],
        repeatRows=1,
    )
    acceptance_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), TEAL),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F0F4F8")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#9FB3C8")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.extend([acceptance_table, Spacer(1, 8 * mm)])
    story.append(paragraph("Repository: github.com/chaabi8noor/k8s-autoguard", body))
    document.build(story)
    return OUTPUT_PATH


if __name__ == "__main__":
    print(build_report())
