import matplotlib.pyplot as plt
from io import BytesIO
import base64


def calculate_excess_fuel(vehicle_type, distance, delay_time_hours):
    """
    Calculate excess fuel consumption due to congestion
    """
    # Time-based calculation
    excess_fuel_time = (vehicle_type['fuel_congested'] -
                        vehicle_type['fuel_free_flow']) * delay_time_hours

    return excess_fuel_time


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
    Generate a pie chart and return as base64 encoded image
    """
    plt.figure(figsize=(8, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title(title)

    # Save chart to a bytes buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Encode the image for HTML display
    chart_url = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f'data:image/png;base64,{chart_url}'