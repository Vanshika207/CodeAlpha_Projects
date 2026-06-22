"""
export_service.py
------------------
Handles exporting translations to TXT and PDF files using ReportLab.
"""

from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


class ExportError(Exception):
    """Custom exception raised when exporting a file fails."""
    pass


class ExportService:
    """Exports translation results to TXT or PDF formats."""

    @staticmethod
    def export_to_txt(filepath: str, original_text: str, translated_text: str,
                       source_lang: str, target_lang: str) -> None:
        """Save the translation as a plain text file."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("AI Smart Language Translator - Export\n")
                f.write("=" * 45 + "\n")
                f.write(f"Date: {timestamp}\n")
                f.write(f"Source Language: {source_lang}\n")
                f.write(f"Target Language: {target_lang}\n")
                f.write("-" * 45 + "\n\n")
                f.write("Original Text:\n")
                f.write(original_text.strip() + "\n\n")
                f.write("Translated Text:\n")
                f.write(translated_text.strip() + "\n")
        except Exception as exc:
            raise ExportError(f"Could not save TXT file: {exc}") from exc

    @staticmethod
    def export_to_pdf(filepath: str, original_text: str, translated_text: str,
                       source_lang: str, target_lang: str) -> None:
        """Save the translation as a formatted PDF file using ReportLab."""
        try:
            doc = SimpleDocTemplate(
                filepath, pagesize=A4,
                topMargin=2 * cm, bottomMargin=2 * cm,
                leftMargin=2 * cm, rightMargin=2 * cm,
            )
            styles = getSampleStyleSheet()

            title_style = ParagraphStyle(
                "TitleStyle", parent=styles["Title"], textColor=colors.HexColor("#1f6aa5")
            )
            heading_style = ParagraphStyle(
                "HeadingStyle", parent=styles["Heading2"], textColor=colors.HexColor("#2b2b2b")
            )
            body_style = ParagraphStyle(
                "BodyStyle", parent=styles["BodyText"], fontSize=11, leading=16
            )

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            elements = [
                Paragraph("AI Smart Language Translator", title_style),
                Spacer(1, 12),
            ]

            info_table = Table(
                [
                    ["Date:", timestamp],
                    ["Source Language:", source_lang],
                    ["Target Language:", target_lang],
                ],
                colWidths=[4 * cm, 10 * cm],
            )
            info_table.setStyle(
                TableStyle(
                    [
                        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 0), (-1, -1), 10),
                        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#1f6aa5")),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ]
                )
            )
            elements.append(info_table)
            elements.append(Spacer(1, 18))

            elements.append(Paragraph("Original Text", heading_style))
            elements.append(Paragraph(original_text.replace("\n", "<br/>"), body_style))
            elements.append(Spacer(1, 16))

            elements.append(Paragraph("Translated Text", heading_style))
            elements.append(Paragraph(translated_text.replace("\n", "<br/>"), body_style))

            doc.build(elements)
        except Exception as exc:
            raise ExportError(f"Could not save PDF file: {exc}") from exc
