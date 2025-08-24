import math


def calculate_fc_barth(speed_kmh):
    """
    Calculates fuel consumption (FC) in L/100km using the Barth & Borinboonsomsin Model (2008).
    FC_Barth = 1.7 + 0.06V + 0.0012V^2 - 0.00001V^3
    Args:
        speed_kmh (float): Vehicle speed in km/h.
    Returns:
        float: Fuel consumption in L/100km.
    """
    V = speed_kmh
    if V < 0:
        V = 0
    fc = 1.7 + 0.06 * V + 0.0012 * (V ** 2) - 0.00001 * (V ** 3)
    return max(0.1, fc)


def calculate_total_fuel_consumption(
        speed_kmh, segment_length_km, total_vehicles, vehicle_mix, vehicle_types_data
):
    """
    Calculates total fuel consumption for a mixed fleet over a given segment length.
    """
    total_fc_liters = 0
    fc_petrol_liters = 0
    fc_diesel_liters = 0

    base_car_fc_per_100km = calculate_fc_barth(speed_kmh)

    for vehicle_type, percentage in vehicle_mix.items():
        fuel_type = vehicle_types_data[vehicle_type]['fuel_type']

        if vehicle_type == 'petrol_car':
            vehicle_fc_per_100km = base_car_fc_per_100km
        elif vehicle_type == 'diesel_minibus':
            vehicle_fc_per_100km = base_car_fc_per_100km * (15 / 8)
        elif vehicle_type == 'diesel_bus_truck':
            vehicle_fc_per_100km = base_car_fc_per_100km * (40 / 8)
        else:
            vehicle_fc_per_100km = base_car_fc_per_100km

        fc_liters_for_type = (vehicle_fc_per_100km / 100) * segment_length_km * total_vehicles * percentage

        total_fc_liters += fc_liters_for_type
        if fuel_type == 'petrol':
            fc_petrol_liters += fc_liters_for_type
        elif fuel_type == 'diesel':
            fc_diesel_liters += fc_liters_for_type

    return total_fc_liters, fc_petrol_liters, fc_diesel_liters