# utils/report_generator.py
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from io import BytesIO
import base64
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os


def generate_pdf_report(result):
    """Generate a PDF report with charts and detailed analysis"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Try to register a font that supports the Naira symbol
    # You might need to adjust this path or use a different font
    try:
        # Try to use DejaVu Sans font if available (it supports more Unicode characters)
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # Common Linux path
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
            normal_font = 'DejaVuSans'
        else:
            # Fallback to Helvetica
            normal_font = 'Helvetica'
    except:
        normal_font = 'Helvetica'

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center aligned
    )
    title = Paragraph(f"Traffic Analysis Report - {result['location']}", title_style)
    elements.append(title)

    # Date range
    date_range = Paragraph(
        f"Date Range: {result['date_range_start']} to {result['date_range_end']}",
        styles['Normal']
    )
    elements.append(date_range)
    elements.append(Spacer(1, 12))

    # Executive Summary
    exec_summary_style = ParagraphStyle(
        'ExecutiveSummary',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=12,
        leading=14
    )

    # Use HTML entities for special characters to ensure they display correctly
    executive_summary = (
        f"This comprehensive analysis examines traffic congestion patterns in {result['location']} during "
        f"the period from {result['date_range_start']} to {result['date_range_end']}. The findings reveal substantial economic and "
        f"environmental consequences resulting from traffic congestion. The analysis indicates that {result['total_excess_fuel']:.2f} "
        f"liters of additional fuel were consumed due to congestion conditions, resulting in an estimated "
        f"cost of N{result['total_excess_fuel_cost']:,.2f}. This excessive fuel consumption contributed to {result['total_co2_emissions']:.2f} kg "
        f"of avoidable CO&#8322; emissions, representing a significant environmental impact. From a socioeconomic perspective, "
        f"productivity losses amounted to N{result['total_productivity_loss']:,.2f}, calculated based on a value of time of "
        f"N{result['value_of_time']:,.2f}/hour. The comprehensive Total Economic Cost of congestion for this timeframe and "
        f"location is estimated at N{result['total_economic_cost']:,.2f}. These findings underscore the multifaceted costs "
        f"associated with traffic congestion, highlighting the urgent need for strategic interventions to "
        f"mitigate both economic losses and environmental damage."
    )

    elements.append(Paragraph("Executive Summary", styles['Heading2']))
    elements.append(Paragraph(executive_summary, exec_summary_style))
    elements.append(Spacer(1, 20))

    # Summary table - use 'N' instead of the symbol for better compatibility
    summary_data = [
        ['Metric', 'Value'],
        ['Total Excess Fuel', f"{result['total_excess_fuel']:.2f} liters"],
        ['Excess Fuel Cost', f"N{result['total_excess_fuel_cost']:,.2f}"],
        ['CO2 Emissions', f"{result['total_co2_emissions']:.2f} kg"],
        ['Productivity Loss', f"N{result['total_productivity_loss']:,.2f}"],
        ['Total Economic Cost', f"N{result['total_economic_cost']:,.2f}"],
        ['Total Vehicles Analyzed', f"{result['total_vehicles']}"]
    ]

    summary_table = Table(summary_data, colWidths=[2.5 * inch, 2 * inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    # Add cost distribution chart if available
    if result.get('cost_chart'):
        try:
            elements.append(Paragraph("Cost Distribution", styles['Heading2']))

            # Chart interpretation
            fuel_percentage = (result['total_excess_fuel_cost'] / result['total_economic_cost'] * 100) if result[
                                                                                                              'total_economic_cost'] > 0 else 0
            productivity_percentage = (result['total_productivity_loss'] / result['total_economic_cost'] * 100) if \
            result['total_economic_cost'] > 0 else 0

            chart_interpretation = (
                f"The cost distribution analysis reveals that productivity losses account for {productivity_percentage:.1f}% "
                f"of the total economic cost (N{result['total_productivity_loss']:,.2f}), while fuel costs represent {fuel_percentage:.1f}% "
                f"(N{result['total_excess_fuel_cost']:,.2f}). This indicates that the primary economic impact of congestion "
                f"is through lost productivity rather than direct fuel expenses."
            )
            elements.append(Paragraph(chart_interpretation, exec_summary_style))
            elements.append(Spacer(1, 12))

            # Decode the base64 chart image
            chart_data = result['cost_chart'].split(',')[1] if ',' in result['cost_chart'] else result['cost_chart']
            chart_img = Image(BytesIO(base64.b64decode(chart_data)), width=5 * inch, height=3 * inch)
            elements.append(chart_img)
            elements.append(Spacer(1, 12))
        except Exception as e:
            print(f"Error adding cost chart to PDF: {e}")

    # Add emission chart if available
    if result.get('emission_chart'):
        try:
            elements.append(Paragraph("CO2 Emissions Impact", styles['Heading2']))

            # Emission interpretation
            emission_interpretation = (
                f"The traffic congestion during the analyzed period resulted in {result['total_co2_emissions']:.2f} kg "
                f"of additional CO&#8322; emissions. This environmental impact represents the carbon footprint equivalent "
                f"of the excess fuel consumption caused by congestion conditions."
            )
            elements.append(Paragraph(emission_interpretation, exec_summary_style))
            elements.append(Spacer(1, 12))

            # Decode the base64 chart image
            chart_data = result['emission_chart'].split(',')[1] if ',' in result['emission_chart'] else result[
                'emission_chart']
            chart_img = Image(BytesIO(base64.b64decode(chart_data)), width=5 * inch, height=3 * inch)
            elements.append(chart_img)
        except Exception as e:
            print(f"Error adding emission chart to PDF: {e}")

    # Add detailed breakdown
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Detailed Breakdown", styles['Heading2']))

    detailed_data = [
        ['Fuel Type', 'Excess Fuel (L)', 'Cost (N)', 'CO2 Emissions (kg)'],
        ['Petrol', f"{result['excess_fuel_petrol']:.2f}", f"{result['fuel_cost_petrol']:,.2f}",
         f"{result['co2_emissions_petrol']:.2f}"],
        ['Diesel', f"{result['excess_fuel_diesel']:.2f}", f"{result['fuel_cost_diesel']:,.2f}",
         f"{result['co2_emissions_diesel']:.2f}"],
        ['Total', f"{result['total_excess_fuel']:.2f}", f"{result['total_excess_fuel_cost']:,.2f}",
         f"{result['total_co2_emissions']:.2f}"]
    ]

    detailed_table = Table(detailed_data, colWidths=[1.5 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch])
    detailed_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(detailed_table)

    # Add analysis parameters
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Analysis Parameters", styles['Heading2']))

    params_data = [
        ['Parameter', 'Value'],
        ['Value of Time (N/hour)', f"{result['value_of_time']:,.2f}"],
        ['Petrol Price (N/liter)', f"{result['petrol_price']:,.2f}"],
        ['Diesel Price (N/liter)', f"{result['diesel_price']:,.2f}"],
        ['Free Flow Speed (km/h)', f"{result['free_flow_speed']:,.1f}"],
        ['Analysis Date', result['analysis_date']]
    ]

    params_table = Table(params_data, colWidths=[2 * inch, 2 * inch])
    params_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(params_table)

    # Add footer with copyright
    elements.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        alignment=1,  # Center aligned
        textColor=colors.grey
    )
    footer = Paragraph(
        "© 2025 Traffic Management Portal. Powered by Oladotun Ajakaiye, Service Manager & Data Analyst, Opygoal Technology Ltd.",
        footer_style
    )
    elements.append(footer)

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_rich_pdf_report(result):
    """Alias for generate_pdf_report for backward compatibility"""
    return generate_pdf_report(result)