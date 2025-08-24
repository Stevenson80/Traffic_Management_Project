import matplotlib.pyplot as plt
from io import BytesIO
import base64


def calculate_excess_co2(excess_fuel, vehicle_type):
    """
    Calculate excess CO2 emissions based on excess fuel consumption
    """
    return excess_fuel * vehicle_type['co2_factor']


def calculate_productivity_loss(delay_time_hours, vehicle_count,
                                vehicle_type, value_of_time):
    """
    Calculate productivity loss due to congestion
    """
    total_delay_hours = delay_time_hours * vehicle_count
    person_hours_lost = total_delay_hours * vehicle_type['occupancy']
    return person_hours_lost * value_of_time


def generate_chart(labels, sizes, title):
    """
    Generate a pie chart and return both base64 string and data URL
    """
    try:
        plt.figure(figsize=(8, 6))

        # Set colors based on chart type
        if 'Cost' in title:
            colors = ['#FF6B6B', '#4ECDC4']  # Red and teal for cost chart
        else:
            colors = ['#45B7D1', '#F9A602']  # Blue and orange for emission chart

        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.title(title, fontweight='bold')

        # Save chart to a bytes buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)

        # Encode the image for both formats
        chart_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        chart_data_url = f'data:image/png;base64,{chart_base64}'
        plt.close()

        # Return both the base64 string (for PDF) and data URL (for web)
        return {
            'base64': chart_base64,
            'data_url': chart_data_url
        }

    except Exception as e:
        print(f"Error generating chart '{title}': {e}")
        plt.close()
        return None