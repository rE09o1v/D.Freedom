import os
import sys
from django.conf import settings
# from django.template.loader import get_template # No longer needed for ReportLab direct generation
from django.utils import timezone
from io import BytesIO
import logging

# ReportLab imports
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, SimpleDocTemplate
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from functools import partial

# ロガーの取得
logger = logging.getLogger(__name__)

# 日本語フォントの登録
FONT_NAME = 'IPAexGothic'
try:
    font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'ipaexg.ttf')
    pdfmetrics.registerFont(TTFont(FONT_NAME, font_path))
    # Attempt to register bold font if it exists
    try:
        bold_font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'ipaexg-bold.ttf') # Assuming bold font file name
        if os.path.exists(bold_font_path):
            pdfmetrics.registerFont(TTFont(FONT_NAME + '-Bold', bold_font_path))
            logger.debug(f"ReportLab Boldフォント登録: {bold_font_path}")
        else:
             pdfmetrics.registerFont(TTFont(FONT_NAME + '-Bold', font_path)) # Fallback to regular if bold not found
             logger.debug("ReportLab Boldフォントが見つからないため、通常フォントを代替として登録")
    except Exception as e_bold:
        logger.error(f"ReportLab Boldフォント登録エラー: {e_bold}, 通常フォントを代替として登録")
        pdfmetrics.registerFont(TTFont(FONT_NAME + '-Bold', font_path)) # Fallback
    logger.debug(f"ReportLabフォント登録: {font_path}")
except Exception as e:
    logger.error(f"ReportLabフォント登録エラー: {e}")

# スタイルの定義
def get_custom_styles():
    styles = getSampleStyleSheet()
    # Base style with Japanese font
    styles.add(ParagraphStyle(name='Normal_JA', parent=styles['Normal'], fontName=FONT_NAME, fontSize=10, leading=14))
    # Heading style
    styles.add(ParagraphStyle(name='Heading1_JA', parent=styles['h1'], fontName=FONT_NAME, fontSize=18, alignment=TA_CENTER, spaceAfter=6*mm))
    # Right aligned text
    styles.add(ParagraphStyle(name='RightAlign_JA', parent=styles['Normal_JA'], alignment=TA_RIGHT))
    # Client Name Style
    styles.add(ParagraphStyle(name='ClientName_JA', parent=styles['Normal_JA'], fontSize=12, spaceAfter=2*mm))
    # Table Header Style (using bold font)
    styles.add(ParagraphStyle(name='TableHeader_JA', parent=styles['Normal_JA'], alignment=TA_CENTER, fontName=FONT_NAME + '-Bold'))
    # Table Cell Style
    styles.add(ParagraphStyle(name='TableCell_JA', parent=styles['Normal_JA']))
    # Table Cell Right Aligned
    styles.add(ParagraphStyle(name='TableCellRight_JA', parent=styles['Normal_JA'], alignment=TA_RIGHT))
    # Total Label Style (right aligned, bold)
    styles.add(ParagraphStyle(name='TotalLabel_JA', parent=styles['TableHeader_JA'], alignment=TA_RIGHT))
    # Total Value Style (right aligned)
    styles.add(ParagraphStyle(name='TotalValue_JA', parent=styles['TableCellRight_JA']))
    # Notes Style
    styles.add(ParagraphStyle(name='Notes_JA', parent=styles['Normal_JA'], fontSize=9))
    # Footer Style
    styles.add(ParagraphStyle(name='Footer_JA', parent=styles['Normal_JA'], alignment=TA_CENTER, fontSize=8, textColor=colors.grey))
    return styles

# 金額フォーマット関数
def format_currency(amount):
    try:
        # Ensure amount is numeric before formatting
        numeric_amount = float(amount) if amount is not None else 0
        return f"¥{numeric_amount:,.0f}" # Format as integer with commas
    except (ValueError, TypeError):
        logger.warning(f"金額のフォーマットに失敗: {amount}")
        return "¥-"

def generate_estimate_pdf(estimate):
    """
    見積書のPDFを生成する関数 (ReportLab Platypus使用)
    """
    buffer = BytesIO()
    # Use A4 paper size and set margins
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                          leftMargin=20*mm, rightMargin=20*mm,
                          topMargin=20*mm, bottomMargin=20*mm)
    styles = get_custom_styles()
    story = []

    # --- Build Story --- 

    # 1. Header Title
    story.append(Paragraph("見積書", styles['Heading1_JA']))
    story.append(Spacer(1, 6 * mm))

    # 2. Company Info (Right aligned Table)
    company_info_data = [
        [Paragraph(f"<strong>個人事業主 D.Freedom</strong>", styles['RightAlign_JA'])],
        [Paragraph("東京都〇〇区〇〇町123-456", styles['RightAlign_JA'])],
        [Paragraph("TEL: 03-1234-5678", styles['RightAlign_JA'])],
        [Paragraph("Email: info@example.com", styles['RightAlign_JA'])]
    ]
    company_table = Table(company_info_data, colWidths=[doc.width]) # Use doc.width for available width
    company_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1), # Minimal padding
        ('TOPPADDING', (0,0), (-1,-1), 1),
    ]))
    story.append(company_table)
    story.append(Spacer(1, 8 * mm))

    # 3. Estimate Info Table
    issue_date_str = estimate.issue_date.strftime("%Y年%m月%d日") if estimate.issue_date else "-"
    expiry_date_str = estimate.expiry_date.strftime("%Y年%m月%d日") if estimate.expiry_date else "-"
    
    estimate_info_data = [
        [Paragraph("見積番号", styles['Normal_JA']), Paragraph(estimate.estimate_number or "-", styles['Normal_JA']), Paragraph("発行日", styles['Normal_JA']), Paragraph(issue_date_str, styles['Normal_JA'])],
        [Paragraph("有効期限", styles['Normal_JA']), Paragraph(expiry_date_str, styles['Normal_JA']), Paragraph("支払条件", styles['Normal_JA']), Paragraph("検収後、請求書発行日より30日以内", styles['Normal_JA'])]
    ]
    estimate_info_table = Table(estimate_info_data, colWidths=[doc.width*0.2, doc.width*0.3, doc.width*0.2, doc.width*0.3])
    estimate_info_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
        ('BACKGROUND', (2,0), (2,-1), colors.whitesmoke),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(estimate_info_table)
    story.append(Spacer(1, 8 * mm))

    # 4. Client Info Section
    client_details = [
        Paragraph(f"<strong>{estimate.client_name} 様</strong>", styles['ClientName_JA']),
        Spacer(1, 2*mm),
        Paragraph(estimate.client_address.replace('\n', '<br/>') if estimate.client_address else "", styles['Normal_JA']),
    ]
    if estimate.client_tel:
        client_details.append(Spacer(1, 1*mm))
        client_details.append(Paragraph(f"TEL: {estimate.client_tel}", styles['Normal_JA']))
    if estimate.client_email:
        client_details.append(Spacer(1, 1*mm))
        client_details.append(Paragraph(f"Email: {estimate.client_email}", styles['Normal_JA']))

    client_table = Table([[client_details]], colWidths=[doc.width])
    client_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, colors.grey),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(client_table)
    story.append(Spacer(1, 8 * mm))

    # 5. Estimate Items Table
    items_header = [Paragraph(h, styles['TableHeader_JA']) for h in ["項目", "数量", "単価", "税率", "金額"]]
    items_data = [items_header]
    
    for item in estimate.items.all():
        item_name_text = item.name
        if item.description:
            item_name_text += f"<br/><font size='8' color='grey'>{item.description}</font>"
        
        items_data.append([
            Paragraph(item_name_text, styles['TableCell_JA']),
            Paragraph(str(item.quantity), styles['TableCell_JA']),
            Paragraph(format_currency(item.unit_price), styles['TableCellRight_JA']),
            Paragraph(f"{item.tax_rate:.0f}%", styles['TableCell_JA']), 
            Paragraph(format_currency(item.subtotal), styles['TableCellRight_JA']),
        ])

    # Footer rows for totals
    items_data.extend([
        [Paragraph("小計（税抜）", styles['TotalLabel_JA']), '', '', '', Paragraph(format_currency(estimate.subtotal), styles['TotalValue_JA'])],
        [Paragraph("消費税", styles['TotalLabel_JA']), '', '', '', Paragraph(format_currency(estimate.tax_amount), styles['TotalValue_JA'])],
        [Paragraph("合計（税込）", styles['TotalLabel_JA']), '', '', '', Paragraph(format_currency(estimate.total), styles['TotalValue_JA'])]
    ])
    
    items_table = Table(items_data, colWidths=[doc.width*0.4, doc.width*0.1, doc.width*0.15, doc.width*0.15, doc.width*0.2])
    items_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-4), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke),
        ('VALIGN', (0,0), (-1,0), 'MIDDLE'), 
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,1), (-1,-4), 'TOP'),
        ('ALIGN', (1,1), (1,-4), 'CENTER'), 
        ('ALIGN', (3,1), (3,-4), 'CENTER'),
        ('LEFTPADDING', (0,1), (-1,-4), 5),
        ('RIGHTPADDING', (0,1), (-1,-4), 5),
        ('TOPPADDING', (0,1), (-1,-4), 3),
        ('BOTTOMPADDING', (0,1), (-1,-4), 3),
        ('SPAN', (0, -3), (3, -3)), 
        ('SPAN', (0, -2), (3, -2)), 
        ('SPAN', (0, -1), (3, -1)),
        ('ALIGN', (0, -3), (3, -1), 'RIGHT'),
        ('GRID', (0,-3), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,-3), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.lightgrey),
        ('FONTNAME', (0, -1), (4, -1), FONT_NAME + '-Bold'),
        ('LEFTPADDING', (0,-3), (-1,-1), 5),
        ('RIGHTPADDING', (0,-3), (-1,-1), 5),
    ]))
    
    story.append(items_table)
    story.append(Spacer(1, 8 * mm))

    # 6. Notes Section (if applicable)
    if estimate.notes:
        notes_table = Table([[
            Paragraph("<strong>備考:</strong>", styles['Normal_JA']),
            Paragraph(estimate.notes.replace('\n', '<br/>'), styles['Notes_JA'])
        ]], colWidths=[doc.width*0.15, doc.width*0.85])
        notes_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('BOX', (0,0), (-1,-1), 0.5, colors.grey), # Add a box around notes
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (1,0), (1,0), 5), # Padding for notes text
        ]))
        story.append(notes_table)
        story.append(Spacer(1, 8 * mm))

    # 7. Footer Text
    footer_text = "本見積書に関するご質問やお問い合わせは、上記の連絡先までお願いいたします。"
    story.append(Paragraph(footer_text, styles['Footer_JA']))

    # --- Build the PDF --- 
    try:
        doc.build(story)
        logger.debug("ReportLab PDF構築完了")
    except Exception as e_build:
        logger.exception(f"ReportLab PDF構築エラー: {e_build}")
        return None
    
    # Return the PDF data
    buffer.seek(0)
    return buffer.getvalue()
