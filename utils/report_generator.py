from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO
import matplotlib.pyplot as plt
import base64


def generate_rich_pdf_report(result, cost_chart, emission_chart):
    # ... (existing code)

    # Add footer with copyright
    story.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.gray,
        alignment=1  # Center aligned
    )
    story.append(Paragraph(
        "&copy; 2025 Traffic Management Portal. Powered by Oladotun Ajakaiye, Service Manager and Data Analyst, Opygoal Technology Ltd.",
        footer_style))

    # Build PDF
    doc.build(story)
    # ... (rest of existing code)


def generate_pdf_report(result):
    # ... (existing code)

    # Add footer with copyright
    elements.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.gray,
        alignment=1  # Center aligned
    )
    elements.append(Paragraph(
        "&copy; 2025 Traffic Management Portal. Powered by Oladotun Ajakaiye, Service Manager and Data Analyst, Opygoal Technology Ltd.",
        footer_style))

    doc.build(elements)
    # ... (rest of existing code)


def generate_rich_pdf_report(result, cost_chart, emission_chart):
    """
    Generate a rich PDF report that matches the web interface
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)

    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center aligned
    )
    story.append(Paragraph("Traffic Congestion Economic Cost Report", title_style))

    # Summary section
    summary_style = ParagraphStyle(
        'Summary',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12
    )

    story.append(Paragraph(f"<b>Location:</b> {result['location']}", summary_style))
    story.append(
        Paragraph(f"<b>Date Range:</b> {result['date_range_start']} to {result['date_range_end']}", summary_style))
    story.append(Paragraph(f"<b>Analysis Date:</b> {result['analysis_date']}", summary_style))
    story.append(Paragraph(f"<b>Value of Time:</b> ₦{result['value_of_time']}/hour", summary_style))
    story.append(Paragraph(f"<b>Fuel Cost:</b> ₦{result['fuel_cost_per_liter']}/liter", summary_style))

    story.append(Spacer(1, 20))

    # Economic Costs Table
    story.append(Paragraph("<b>Economic Costs</b>", styles['Heading2']))

    cost_data = [
        ['Metric', 'Value', 'Unit'],
        ['Excess Fuel Consumption', f"{result['total_excess_fuel']:,.2f}", 'Liters'],
        ['Excess Fuel Cost', f"₦{result['total_excess_fuel_cost']:,.2f}", 'Naira'],
        ['CO2 Emissions', f"{result['total_co2_emissions']:,.2f}", 'kg'],
        ['Productivity Loss', f"₦{result['total_productivity_loss']:,.2f}", 'Naira'],
        ['Total Economic Cost', f"<b>₦{result['total_economic_cost']:,.2f}</b>", 'Naira']
    ]

    table = Table(cost_data, colWidths=[2.5 * inch, 1.5 * inch, 1 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#343a40')),  # Dark background for header
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#f8f9fa')),  # Light background for data
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e9ecef')),  # Different background for total
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 12),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
    ]))

    story.append(table)
    story.append(Spacer(1, 20))

    # Cost Distribution Chart
    story.append(Paragraph("<b>Cost Distribution</b>", styles['Heading2']))

    # Convert base64 chart to image for PDF
    cost_chart_data = cost_chart.split(',')[1]  # Remove the data:image/png;base64, part
    cost_img_data = BytesIO(base64.b64decode(cost_chart_data))

    # Create a matplotlib figure from the image data
    cost_img = plt.imread(cost_img_data)
    plt.figure(figsize=(6, 4))
    plt.imshow(cost_img)
    plt.axis('off')

    # Save as a temporary image file
    temp_cost_path = "temp_cost_chart.png"
    plt.savefig(temp_cost_path, bbox_inches='tight', pad_inches=0.1)
    plt.close()

    # Add image to PDF
    cost_image = Image(temp_cost_path, width=4 * inch, height=3 * inch)
    cost_image.hAlign = 'CENTER'
    story.append(cost_image)
    story.append(Spacer(1, 15))

    # CO2 Emissions Chart
    story.append(Paragraph("<b>CO2 Emissions</b>", styles['Heading2']))

    # Convert base64 chart to image for PDF
    emission_chart_data = emission_chart.split(',')[1]  # Remove the data:image/png;base64, part
    emission_img_data = BytesIO(base64.b64decode(emission_chart_data))

    # Create a matplotlib figure from the image data
    emission_img = plt.imread(emission_img_data)
    plt.figure(figsize=(6, 4))
    plt.imshow(emission_img)
    plt.axis('off')

    # Save as a temporary image file
    temp_emission_path = "temp_emission_chart.png"
    plt.savefig(temp_emission_path, bbox_inches='tight', pad_inches=0.1)
    plt.close()

    # Add image to PDF
    emission_image = Image(temp_emission_path, width=4 * inch, height=3 * inch)
    emission_image.hAlign = 'CENTER'
    story.append(emission_image)

    # Build PDF
    doc.build(story)

    buffer.seek(0)
    return buffer


def generate_pdf_report(result):
    """
    Original basic PDF report (fallback)
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph("Traffic Congestion Economic Cost Report", styles['Title']))
    elements.append(Paragraph(f"Location: {result['location']}", styles['Normal']))
    elements.append(
        Paragraph(f"Date Range: {result['date_range_start']} to {result['date_range_end']}", styles['Normal']))
    elements.append(Paragraph(f"Analysis Date: {result['analysis_date']}", styles['Normal']))

    # Add a table with the results
    data = [
        ['Metric', 'Value', 'Unit'],
        ['Excess Fuel Consumption', f"{result['total_excess_fuel']:,.2f}", 'Liters'],
        ['Excess Fuel Cost', f"₦{result['total_excess_fuel_cost']:,.2f}", 'Naira'],
        ['CO2 Emissions', f"{result['total_co2_emissions']:,.2f}", 'kg'],
        ['Productivity Loss', f"₦{result['total_productivity_loss']:,.2f}", 'Naira'],
        ['Total Economic Cost', f"₦{result['total_economic_cost']:,.2f}", 'Naira']
    ]

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 12),
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    return buffer