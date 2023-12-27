import requests
from rich.console import Console
from rich.table import Table
import argparse

# Command line arguments
parser = argparse.ArgumentParser(description='Display Span Status')
parser.add_argument('--ip', help='SPAN ip address')
parser.add_argument('--token', help='bearer token')
parser.add_argument('-z', '--include-zeroes', action='store_false', default=True,
                    help='Include circuits with zero power')
args = parser.parse_args()
include_zeroes = args.include_zeroes
ip = args.ip
bearer_token = args.token

# Send a GET request to the endpoint
circuits_endpoint = f"http://{ip}/api/v1/circuits"
headers = {"Authorization": f"Bearer {bearer_token}"}
response = requests.get(circuits_endpoint, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()

    # Process the JSON data
    circuits = []
    total_power = 0
    for key, value in data['circuits'].items():
        power_watts = abs(value['instantPowerW'])
        display_power = f"{power_watts / 1000:.1f} kW" if power_watts >= 1000 else f"{power_watts:.1f} W"
        if power_watts <= 0 and include_zeroes:
            continue
        total_power += power_watts
        circuits.append({
            "Slots": str(value['tabs']),
            "Name": value['name'],
            "Power": display_power,
            "SortKey": power_watts
        })

    circuits = sorted(circuits, key=lambda x: x['SortKey'], reverse=True)

    # Create a console object
    console = Console()

    # Create a table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Slots", style="dim")
    table.add_column("Name")
    table.add_column("Power", justify="right", style="orange1")

    # Unpack all but the last circuit, and then the last circuit separately
    *other_circuits, last_circuit = circuits

    # Add all but the last circuit normally
    for circuit in other_circuits:
        table.add_row(circuit["Slots"], circuit["Name"], circuit["Power"])

    # Add the last circuit with end_section=True
    table.add_row(last_circuit["Slots"], last_circuit["Name"], last_circuit["Power"], end_section=True)

    # Add total power to the list
    total_row = {
        "Slots": "Total",
        "Name": "",
        "Power": f"{total_power:.1f} W" if total_power < 1000 else f"{total_power / 1000:.1f} kW"
    }
    table.add_row(total_row["Slots"], total_row["Name"], total_row["Power"], end_section=True)

    # Print the table to the console
    console.print(table)
else:
    print(f"Failed to get data: {response.status_code}")
