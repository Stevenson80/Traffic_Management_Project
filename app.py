from utils.report_generator import generate_pdf_report, generate_rich_pdf_report
from flask import Flask, render_template, request, jsonify, send_file
import json
import os
import pandas as pd
from datetime import datetime
from utils.calculations import (
    calculate_excess_co2,
    calculate_productivity_loss,
    generate_chart
)
import matplotlib

matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Enhanced vehicle type configuration
VEHICLE_TYPES = {
    'petrol_car': {
        'name': 'Car (Petrol)',
        'fuel_type': 'petrol',
        'base_fc': 8,  # L/100km
        'occupancy': 1.5,
        'co2_factor': 2.31,
        'congestion_multiplier': 1.5  # 50% more fuel in congestion
    },
    'petrol_suv': {
        'name': 'SUV (Petrol)',
        'fuel_type': 'petrol',
        'base_fc': 12,
        'occupancy': 1.8,
        'co2_factor': 2.31,
        'congestion_multiplier': 1.6  # 60% more fuel in congestion
    },
    'diesel_bus': {
        'name': 'Bus (Diesel)',
        'fuel_type': 'diesel',
        'base_fc': 25,
        'occupancy': 25.0,
        'co2_factor': 2.68,
        'congestion_multiplier': 1.4  # 40% more fuel in congestion
    },
    'diesel_truck': {
        'name': 'Truck (Diesel)',
        'fuel_type': 'diesel',
        'base_fc': 35,
        'occupancy': 1.2,
        'co2_factor': 2.68,
        'congestion_multiplier': 1.4  # 40% more fuel in congestion
    },
    'petrol_motorcycle': {
        'name': 'Motorcycle (Petrol)',
        'fuel_type': 'petrol',
        'base_fc': 3,
        'occupancy': 1.2,
        'co2_factor': 2.31,
        'congestion_multiplier': 1.3  # 30% more fuel in congestion
    }
}

# ADD THIS MAPPING - it's essential!
VEHICLE_TYPE_MAPPING = {
    1: 'petrol_car',
    2: 'petrol_suv',
    3: 'diesel_bus',
    4: 'diesel_truck',
    5: 'petrol_motorcycle'
}

# CO2 Emission factors (can be used instead of individual vehicle factors)
CO2_EMISSION_FACTORS = {
    'petrol': 2.31,  # kg CO2 per liter
    'diesel': 2.68  # kg CO2 per liter
}


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
        try:
            traffic_data = {
                "id": datetime.now().strftime("%Y%m%d%H%M%S"),
                "location": request.form.get('location'),
                "date": request.form.get('date'),
                "time": request.form.get('time'),
                "vehicle_type": int(request.form.get('vehicle_type', 0)),
                "volume": int(request.form.get('volume', 0)),
                "actual_travel_time": float(request.form.get('actual_travel_time', 0.1)),
                "free_flow_travel_time": float(request.form.get('free_flow_travel_time', 0.1)),
                "distance": float(request.form.get('distance', 0.1))
            }
            if traffic_data["location"] is None or traffic_data["date"] is None or traffic_data["time"] is None:
                raise ValueError("Missing essential data entry fields.")
        except ValueError as e:
            print(f"Data entry validation error: {e}")
            return render_template('error.html', message=f"Invalid data input: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during data entry: {e}")
            return render_template('error.html', message=f"An unexpected error occurred: {e}")

        # Load existing data, add new entry, and save
        data = load_data()
        data['traffic_data'].append(traffic_data)
        save_data(data)

        return render_template('data_success.html')

    # GET request - format vehicle types for the template
    formatted_vehicles = []
    for i, (key, vehicle) in enumerate(VEHICLE_TYPES.items(), 1):
        formatted_vehicles.append({
            'id': i,
            'name': vehicle['name']
        })
    return render_template('data_entry.html', vehicle_types=formatted_vehicles)


def calculate_excess_fuel_simple(vehicle, delay_time_minutes, distance_km, volume):
    """
    Simple and reliable fuel calculation based on delay time and distance
    """
    # Calculate excess fuel based on delay time and vehicle characteristics
    base_consumption = vehicle.get('base_fc', 8)  # L/100km
    congestion_factor = vehicle.get('congestion_multiplier', 1.5)

    # Free flow consumption
    free_flow_consumption = (base_consumption / 100) * distance_km * volume

    # Congested consumption (increased by congestion factor)
    congested_consumption = free_flow_consumption * congestion_factor

    excess_fuel = max(0, congested_consumption - free_flow_consumption)

    print(f"\n--- Fuel Calculation for {vehicle['name']} ---")
    print(f"  Base FC: {base_consumption} L/100km, Congestion multiplier: {congestion_factor}")
    print(f"  Distance: {distance_km} km, Volume: {volume}")
    print(f"  Free flow consumption: {free_flow_consumption:.2f}L")
    print(f"  Congested consumption: {congested_consumption:.2f}L")
    print(f"  Excess fuel: {excess_fuel:.2f}L")
    print("---------------------------------------------------------")

    return excess_fuel


@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    if request.method == 'POST':
        try:
            # Debug: print all form data
            print("=== FORM DATA ===")
            for key, value in request.form.items():
                print(f"{key}: {value}")

            location = request.form.get('location')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            value_of_time = float(request.form.get('value_of_time', 50.0))
            petrol_price = float(request.form.get('petrol_price', 150.0))
            diesel_price = float(request.form.get('diesel_price', 200.0))
            free_flow_speed = float(request.form.get('free_flow_speed', 80.0))

            print(f"Parsed values - Petrol: {petrol_price}, Diesel: {diesel_price}")

        except ValueError as e:
            print(f"Analyze form input error: {e}")
            return render_template('error.html', message=f"Invalid input for analysis parameters: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during /analyze POST parameter parsing: {e}")
            return render_template('error.html', message=f"An unexpected error occurred: {e}")

        # Load traffic data
        data = load_data()
        traffic_data = data['traffic_data']

        # Filter data by location and date range
        filtered_data = [
            d for d in traffic_data
            if d['location'] == location and start_date <= d['date'] <= end_date
        ]

        if not filtered_data:
            return render_template('results.html',
                                   result={"message": "No data available for the selected location and date range."},
                                   cost_chart=None,
                                   emission_chart=None,
                                   value_of_time=value_of_time,
                                   petrol_price=petrol_price,
                                   diesel_price=diesel_price)

        # Initialize variables
        total_excess_fuel = 0.0
        total_co2_emissions = 0.0
        total_productivity_loss = 0.0
        excess_fuel_petrol = 0.0
        excess_fuel_diesel = 0.0
        total_vehicles = 0

        print("\n=== STARTING ANALYSIS ===")
        print(f"Location: {location}, Date Range: {start_date} to {end_date}")
        print(f"Free flow speed: {free_flow_speed} km/h")
        print(f"Value of time: N{value_of_time}/hour")
        print(f"Petrol price: N{petrol_price}/liter, Diesel price: N{diesel_price}/liter")
        print(f"Number of entries to process: {len(filtered_data)}")

        for entry in filtered_data:
            try:
                print(f"\n--- Processing Entry {entry.get('id', 'N/A')} ---")
                print(f"Vehicle type ID: {entry.get('vehicle_type')}")
                print(f"Volume: {entry.get('volume')} vehicles")
                print(f"Distance: {entry.get('distance')} km")
                print(f"Actual travel time: {entry.get('actual_travel_time')} min")
                print(f"Free flow time: {entry.get('free_flow_travel_time')} min")

                entry_vehicle_type = entry.get('vehicle_type', 0)
                entry_volume = entry.get('volume', 0)
                entry_actual_travel_time = float(entry.get('actual_travel_time', 0.1))
                entry_free_flow_travel_time = float(entry.get('free_flow_travel_time', 0.1))
                entry_distance = float(entry.get('distance', 0.1))

                vehicle_key = VEHICLE_TYPE_MAPPING.get(entry_vehicle_type)
                print(f"Vehicle type mapping: {entry_vehicle_type} -> {vehicle_key}")

                if not vehicle_key or vehicle_key not in VEHICLE_TYPES:
                    print(f"Warning: Unknown vehicle type ID {entry_vehicle_type}. Skipping entry.")
                    continue

                vehicle = VEHICLE_TYPES[vehicle_key]
                print(f"Vehicle details: {vehicle['name']} ({vehicle['fuel_type']})")

                # Calculate delay time
                delay_time_minutes = max(0.0, entry_actual_travel_time - entry_free_flow_travel_time)
                delay_time_hours = delay_time_minutes / 60
                print(f"Delay time: {delay_time_minutes:.1f} minutes ({delay_time_hours:.2f} hours)")

                # Calculate excess fuel using simple reliable method
                excess_fuel = calculate_excess_fuel_simple(
                    vehicle, delay_time_minutes, entry_distance, entry_volume
                )

                if vehicle['fuel_type'] == 'petrol':
                    excess_fuel_petrol += excess_fuel
                elif vehicle['fuel_type'] == 'diesel':
                    excess_fuel_diesel += excess_fuel

                total_excess_fuel += excess_fuel

                # Calculate CO2 emissions
                excess_co2 = excess_fuel * vehicle['co2_factor']
                total_co2_emissions += excess_co2

                # Calculate productivity loss
                productivity_loss = calculate_productivity_loss(
                    delay_time_hours, entry_volume, vehicle, value_of_time
                )
                total_productivity_loss += productivity_loss

                total_vehicles += entry_volume
                print(
                    f"  Entry processed. Excess Fuel: {excess_fuel:.2f}L, Productivity Loss: N{productivity_loss:.2f}")

            except Exception as e:
                print(f"Error processing traffic entry {entry.get('id', 'N/A')}: {e}")
                continue

        # Calculate costs with actual prices
        fuel_cost_petrol = excess_fuel_petrol * petrol_price
        fuel_cost_diesel = excess_fuel_diesel * diesel_price
        total_excess_fuel_cost = fuel_cost_petrol + fuel_cost_diesel
        total_economic_cost = total_excess_fuel_cost + total_productivity_loss

        # Print summary
        print(f"\n=== ANALYSIS SUMMARY ===")
        print(f"Total vehicles: {total_vehicles}")
        print(f"Total excess fuel: {total_excess_fuel:.2f}L")
        print(f"Petrol excess: {excess_fuel_petrol:.2f}L, Diesel excess: {excess_fuel_diesel:.2f}L")
        print(f"Fuel cost: N{total_excess_fuel_cost:.2f}")
        print(f"Productivity loss: N{total_productivity_loss:.2f}")
        print(f"Total economic cost: N{total_economic_cost:.2f}")
        print(f"CO2 emissions: {total_co2_emissions:.2f}kg")

        # Generate charts
        cost_chart = None
        cost_chart_data_url = None
        if total_excess_fuel_cost > 0 or total_productivity_loss > 0:
            cost_labels = ['Fuel Cost', 'Productivity Loss']
            cost_sizes = [total_excess_fuel_cost, total_productivity_loss]
            try:
                chart_result = generate_chart(cost_labels, cost_sizes, 'Economic Cost Distribution')
                if chart_result:
                    cost_chart = chart_result['base64']
                    cost_chart_data_url = chart_result['data_url']
            except Exception as e:
                print(f"Error generating cost chart: {e}")

        emission_chart = None
        emission_chart_data_url = None
        if total_co2_emissions > 0:
            emission_labels = ['CO₂ Emissions from Congestion']
            emission_sizes = [total_co2_emissions]
            try:
                chart_result = generate_chart(emission_labels, emission_sizes, 'CO₂ Emissions Impact')
                if chart_result:
                    emission_chart = chart_result['base64']
                    emission_chart_data_url = chart_result['data_url']
            except Exception as e:
                print(f"Error generating emission chart: {e}")

        # Save results
        result_id = datetime.now().strftime("%Y%m%d%H%M%S")
        result = {
            "id": result_id,
            "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "location": location or "Unknown",
            "date_range_start": start_date or "N/A",
            "date_range_end": end_date or "N/A",
            "total_excess_fuel": total_excess_fuel,
            "excess_fuel_petrol": excess_fuel_petrol,
            "excess_fuel_diesel": excess_fuel_diesel,
            "total_excess_fuel_cost": total_excess_fuel_cost,
            "fuel_cost_petrol": fuel_cost_petrol,
            "fuel_cost_diesel": fuel_cost_diesel,
            "total_co2_emissions": total_co2_emissions,
            "co2_emissions_petrol": excess_fuel_petrol * CO2_EMISSION_FACTORS['petrol'],
            "co2_emissions_diesel": excess_fuel_diesel * CO2_EMISSION_FACTORS['diesel'],
            "total_productivity_loss": total_productivity_loss,
            "total_economic_cost": total_economic_cost,
            "total_vehicles": total_vehicles,
            "value_of_time": value_of_time,
            "petrol_price": petrol_price,
            "diesel_price": diesel_price,
            "free_flow_speed": free_flow_speed,
            "cost_chart": cost_chart or "",
            "emission_chart": emission_chart or ""
        }

        data['results'].append(result)
        save_data(data)

        return render_template('results.html',
                               result=result,
                               cost_chart=cost_chart_data_url,
                               emission_chart=emission_chart_data_url,
                               value_of_time=value_of_time,
                               petrol_price=petrol_price,
                               diesel_price=diesel_price)

    # GET request handling
    data = load_data()
    locations = list(set(entry['location'] for entry in data['traffic_data']))
    return render_template('analyze.html', locations=locations)


@app.route('/download-pdf/<result_id>')
def download_pdf(result_id):
    """Download PDF report for a specific analysis result"""
    try:
        data = load_data()
        result = None
        for res in data['results']:
            if res['id'] == result_id:
                result = res
                break

        if not result:
            return render_template('error.html', message="Result not found")

        pdf_buffer = generate_pdf_report(result)

        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f"traffic_analysis_report_{result_id}.pdf",
            mimetype='application/pdf'
        )

    except Exception as e:
        print(f"Error generating PDF: {e}")
        return render_template('error.html', message=f"Error generating PDF: {e}")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)