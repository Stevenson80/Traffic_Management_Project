from utils.report_generator import generate_pdf_report, generate_rich_pdf_report
from flask import Flask, render_template, request, jsonify, send_file
import json
import os
import pandas as pd
from datetime import datetime
from utils.calculations import (
    calculate_excess_fuel, calculate_excess_co2,
    calculate_productivity_loss, generate_chart
)
from utils.report_generator import generate_pdf_report
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Sample vehicle types data
VEHICLE_TYPES = [
    {"id": 1, "name": "Car (Petrol)", "fuel_free_flow": 0.08, "fuel_congested": 0.12,
     "co2_factor": 2.31, "occupancy": 1.5},
    {"id": 2, "name": "SUV (Petrol)", "fuel_free_flow": 0.12, "fuel_congested": 0.18,
     "co2_factor": 2.31, "occupancy": 1.8},
    {"id": 3, "name": "Bus (Diesel)", "fuel_free_flow": 0.25, "fuel_congested": 0.35,
     "co2_factor": 2.68, "occupancy": 25.0},
    {"id": 4, "name": "Truck (Diesel)", "fuel_free_flow": 0.30, "fuel_congested": 0.45,
     "co2_factor": 2.68, "occupancy": 1.2},
    {"id": 5, "name": "Motorcycle (Petrol)", "fuel_free_flow": 0.03, "fuel_congested": 0.04,
     "co2_factor": 2.31, "occupancy": 1.2}
]


# Load data from JSON file
def load_data():
    if os.path.exists('data/database.json'):
        with open('data/database.json', 'r') as f:
            return json.load(f)
    return {"traffic_data": [], "results": []}


# Save data to JSON file
def save_data(data):
    with open('data/database.json', 'w') as f:
        json.dump(data, f, indent=4)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/data-entry', methods=['GET', 'POST'])
def data_entry():
    if request.method == 'POST':
        # Get form data
        traffic_data = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "location": request.form.get('location'),
            "date": request.form.get('date'),
            "time": request.form.get('time'),
            "vehicle_type": int(request.form.get('vehicle_type')),
            "volume": int(request.form.get('volume')),
            "actual_travel_time": float(request.form.get('actual_travel_time')),
            "free_flow_travel_time": float(request.form.get('free_flow_travel_time')),
            "distance": float(request.form.get('distance'))
        }

        # Load existing data, add new entry, and save
        data = load_data()
        data['traffic_data'].append(traffic_data)
        save_data(data)

        return render_template('data_success.html')

    return render_template('data_entry.html', vehicle_types=VEHICLE_TYPES)


@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    if request.method == 'POST':
        location = request.form.get('location')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        value_of_time = float(request.form.get('value_of_time', 50))

        # Load traffic data
        data = load_data()
        traffic_data = data['traffic_data']

        # Filter data by location and date range
        filtered_data = [
            d for d in traffic_data
            if d['location'] == location and start_date <= d['date'] <= end_date
        ]

        total_excess_fuel = 0
        total_co2_emissions = 0
        total_productivity_loss = 0

        for entry in filtered_data:
            # Find vehicle type details
            vehicle = next((v for v in VEHICLE_TYPES if v['id'] == entry['vehicle_type']), None)
            if not vehicle:
                continue

            # Calculate delay time in hours
            delay_time_minutes = entry['actual_travel_time'] - entry['free_flow_travel_time']
            delay_time_hours = delay_time_minutes / 60

            # Calculate metrics
            excess_fuel = calculate_excess_fuel(vehicle, entry['distance'], delay_time_hours) * entry['volume']
            excess_co2 = calculate_excess_co2(excess_fuel, vehicle)
            productivity_loss = calculate_productivity_loss(
                delay_time_hours, entry['volume'], vehicle, value_of_time
            )

            total_excess_fuel += excess_fuel
            total_co2_emissions += excess_co2
            total_productivity_loss += productivity_loss

        # Calculate costs (assuming fuel cost is 150 Naira per liter)
        fuel_cost_per_liter = 150
        total_excess_fuel_cost = total_excess_fuel * fuel_cost_per_liter
        total_economic_cost = total_excess_fuel_cost + total_productivity_loss

        # Generate charts
        cost_labels = ['Fuel Cost', 'Productivity Loss']
        cost_sizes = [total_excess_fuel_cost, total_productivity_loss]
        cost_chart = generate_chart(cost_labels, cost_sizes, 'Economic Cost Components')

        emission_labels = ['CO2 Emissions']
        emission_sizes = [total_co2_emissions]
        emission_chart = generate_chart(emission_labels, emission_sizes, 'CO2 Emissions')

        # Save results
        result_id = datetime.now().strftime("%Y%m%d%H%M%S")
        # In your analyze function, after generating charts:
        result = {
            "id": result_id,
            "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "location": location,
            "date_range_start": start_date,
            "date_range_end": end_date,
            "total_excess_fuel": total_excess_fuel,
            "total_excess_fuel_cost": total_excess_fuel_cost,
            "total_co2_emissions": total_co2_emissions,
            "total_productivity_loss": total_productivity_loss,
            "total_economic_cost": total_economic_cost,
            "value_of_time": value_of_time,
            "fuel_cost_per_liter": fuel_cost_per_liter,
            "cost_chart": cost_chart,  # Store the chart data
            "emission_chart": emission_chart  # Store the chart data
        }

        data['results'].append(result)
        save_data(data)

        return render_template('results.html',
                               result=result,
                               cost_chart=cost_chart,
                               emission_chart=emission_chart,
                               value_of_time=value_of_time,
                               fuel_cost_per_liter=fuel_cost_per_liter)

    # Get unique locations for the dropdown
    data = load_data()
    locations = list(set(entry['location'] for entry in data['traffic_data']))

    return render_template('analyze.html', locations=locations)


@app.route('/download-pdf/<result_id>')
def download_pdf(result_id):
    data = load_data()
    result = next((r for r in data['results'] if r['id'] == result_id), None)

    if result:
        # Use the rich PDF generator with stored charts
        pdf_buffer = generate_rich_pdf_report(
            result,
            result.get('cost_chart', ''),
            result.get('emission_chart', '')
        )

        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f"traffic_report_{result_id}.pdf",
            mimetype='application/pdf'
        )

    return "Report not found", 404


    # Print startup message with credits
    print("=" * 60)
    print("Traffic Management Portal")
    print("Powered by Oladotun Ajakaiye, Opygoal Technology Ltd")
    print("© 2025 - All rights reserved")
    print("=" * 60)

    # Get port from environment variable or default to 5000 for local development
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)


if __name__ == '__main__':
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')

    # Get port from environment variable (for Render) or default to 5000
    port = int(os.environ.get('PORT', 5000))

    # Run the app
    app.run(host='0.0.0.0', port=port)
