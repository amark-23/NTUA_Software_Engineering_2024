#!/usr/bin/env python3

import requests
import argparse
import json
import os

API_BASE_URL = "http://localhost:9115/api"

def get_token():
    """Retrieve the saved JWT token"""
    try:
        with open("token.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("Error: No token found. Please login first.")
        exit(1)

def login(username, password):
    """Login and get a JWT token"""
    url = f"{API_BASE_URL}/login"
    data = {"username": username, "password": password}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(url, data=data, headers=headers)

    if response.status_code == 200:
        with open("token.txt", "w") as f:
            f.write(response.json()["token"])
        print("Login successful!")
    else:
        print("Login failed:", response.json())

def logout():
    """Logout the current user"""
    url = f"{API_BASE_URL}/logout"
    headers = {"X-OBSERVATORY-AUTH": f"Bearer {get_token()}"}
    
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        os.remove("token.txt")
        print("Logout successful.")
    else:
        print("Logout failed:", response.text)

def get_toll_station_passes(station, from_date, to_date, format_type="json"):
    """Fetch toll station passes"""
    if format_type is None: format_type = "csv" 
    url = f"{API_BASE_URL}/tollStationPasses/{station}/{from_date}/{to_date}?format={format_type}"
    headers = {"X-OBSERVATORY-AUTH": f"Bearer {get_token()}"}
    
    response = requests.get(url, headers=headers)
    handle_response(response, format_type)

def get_pass_analysis(station_op, tag_op, from_date, to_date, output_format="csv"):
    """Fetch pass analysis"""
    if output_format is None: output_format = "csv" 
    url = f"{API_BASE_URL}/passAnalysis/{station_op}/{tag_op}/{from_date}/{to_date}?format={output_format}"
    headers = {"X-OBSERVATORY-AUTH": f"Bearer {get_token()}"}
    
    response = requests.get(url, headers=headers)
    handle_response(response, output_format)

def get_passes_cost(station_op, tag_op, from_date, to_date, output_format="csv"):
    """Fetch passes cost"""
    if output_format is None: output_format = "csv" 
    url = f"{API_BASE_URL}/passesCost/{station_op}/{tag_op}/{from_date}/{to_date}?format={output_format}"
    headers = {"X-OBSERVATORY-AUTH": f"Bearer {get_token()}"}
    
    response = requests.get(url, headers=headers)
    handle_response(response, output_format)

def get_charges_by(opid, from_date, to_date, output_format="csv"):
    """Fetch charges by operator"""
    if output_format is None: output_format = "csv" 
    url = f"{API_BASE_URL}/chargesBy/{opid}/{from_date}/{to_date}?format={output_format}"
    headers = {"X-OBSERVATORY-AUTH": f"Bearer {get_token()}"}
    
    response = requests.get(url, headers=headers)
    handle_response(response, output_format)

def handle_response(response, format_type):
    """Handle API responses consistently"""
    if response.status_code == 200:
        if format_type == "json":
            try:
                print(json.dumps(response.json(), indent=2))
            except json.JSONDecodeError:
                print("Invalid JSON response:", response.text)
        else:
            print(response.text)
    else:
        print(f"Request failed ({response.status_code}): {response.text}")

# ===================== ADMIN FUNCTIONS =====================
def reset_stations():
    """Reset toll stations"""
    url = f"{API_BASE_URL}/admin/resetstations"
    headers = {"X-OBSERVATORY-AUTH": f"Bearer {get_token()}"}
    
    response = requests.post(url, headers=headers)
    
    # Handle the response
    if response.status_code == 200:
        print("Reset stations:", response.json())
    else:
        print(f"Request failed ({response.status_code}): {response.text}")
def reset_passes():
    """Reset all passes"""
    url = f"{API_BASE_URL}/admin/resetpasses"
    headers = {"X-OBSERVATORY-AUTH": f"Bearer {get_token()}"}
    
    response = requests.post(url, headers=headers)
    print("Reset passes:", response.json())

def healthcheck():
    """Check system health"""
    url = f"{API_BASE_URL}/admin/healthcheck"
    headers = {"X-OBSERVATORY-AUTH": f"Bearer {get_token()}"}
    
    response = requests.get(url, headers=headers)
    handle_response(response, "json")

def add_passes(file_path):
    """Upload passes CSV"""
    url = f"{API_BASE_URL}/admin/addpasses"
    headers = {"X-OBSERVATORY-AUTH": f"Bearer {get_token()}"}
    
    try:
        with open(file_path, "rb") as f:
            response = requests.post(url, headers=headers, files={"file": f})
            print("Add passes:", response.json())
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")

def admin_usermod(username, password, operator=None):
    """Create/modify user"""
    url = f"{API_BASE_URL}/admin/usermod"
    headers = {
        "X-OBSERVATORY-AUTH": f"Bearer {get_token()}",
        "Content-Type": "application/json"
    }
    data = {"username": username, "password": password}
    if operator:
        data["operator"] = operator

    response = requests.post(url, headers=headers, json=data)
    print("User modification:", response.json())

def get_users():
    """List all users"""
    url = f"{API_BASE_URL}/admin/users?format={args.format}"
    headers = {"X-OBSERVATORY-AUTH": f"Bearer {get_token()}"}
    
    response = requests.get(url, headers=headers)
    handle_response(response, args.format)

# ===================== CLI SETUP =====================
parser = argparse.ArgumentParser(description="Toll System CLI")
subparsers = parser.add_subparsers(dest="command")

# Authentication commands
login_parser = subparsers.add_parser("login")
login_parser.add_argument("--username", required=True)
login_parser.add_argument("--password", required=True, dest="password")

subparsers.add_parser("logout")

# Data retrieval commands
tollpass_parser = subparsers.add_parser("tollstationpasses")
tollpass_parser.add_argument("--station", required=True)
tollpass_parser.add_argument("--from", dest="from_date", required=True)
tollpass_parser.add_argument("--to", dest="to_date", required=True)
tollpass_parser.add_argument("--format", choices=["json", "csv"], default="csv")

analysis_parser = subparsers.add_parser("passanalysis")
analysis_parser.add_argument("--stationop", required=True)
analysis_parser.add_argument("--tagop", required=True)
analysis_parser.add_argument("--from", dest="from_date", required=True)
analysis_parser.add_argument("--to", dest="to_date", required=True)
analysis_parser.add_argument("--format", choices=["json", "csv"], default="csv")

cost_parser = subparsers.add_parser("passescost")
cost_parser.add_argument("--stationop", required=True)
cost_parser.add_argument("--tagop", required=True)
cost_parser.add_argument("--from", dest="from_date", required=True)
cost_parser.add_argument("--to", dest="to_date", required=True)
cost_parser.add_argument("--format", choices=["json", "csv"], default="csv")

charges_parser = subparsers.add_parser("chargesby")
charges_parser.add_argument("--opid", required=True)
charges_parser.add_argument("--from", dest="from_date", required=True)
charges_parser.add_argument("--to", dest="to_date", required=True)
charges_parser.add_argument("--format", choices=["json", "csv"], default="csv")

# Admin commands
admin_parser = subparsers.add_parser("admin")
admin_parser.add_argument("--usermod", action="store_true")
admin_parser.add_argument("--users", action="store_true")
admin_parser.add_argument("--addpasses", action="store_true")
admin_parser.add_argument("--username")
admin_parser.add_argument("--password", "--passw", dest="password", help="User's password")
admin_parser.add_argument("--operator")
admin_parser.add_argument("--source")
admin_parser.add_argument("--format", choices=["json", "csv"], default="csv")

# New top-level admin commands
subparsers.add_parser("healthcheck")
subparsers.add_parser("resetpasses")
subparsers.add_parser("resetstations")

# ===================== COMMAND ROUTING =====================
args = parser.parse_args()

if args.command == "login":
    login(args.username, args.password)
elif args.command == "logout":
    logout()
elif args.command == "tollstationpasses":
    get_toll_station_passes(args.station, args.from_date, args.to_date, args.format)
elif args.command == "passanalysis":
    get_pass_analysis(args.stationop, args.tagop, args.from_date, args.to_date, args.format)
elif args.command == "passescost":
    get_passes_cost(args.stationop, args.tagop, args.from_date, args.to_date, args.format)
elif args.command == "chargesby":
    get_charges_by(args.opid, args.from_date, args.to_date, args.format)
elif args.command == "admin":
    if args.usermod:
        if not args.username or not args.password:
            print("Error: --username and --password required for usermod")
            exit(1)
        admin_usermod(args.username, args.password, args.operator)
    elif args.users:
        get_users()
    elif args.addpasses:
        if not args.source:
            print("Error: --source required for addpasses")
            exit(1)
        add_passes(args.source)
elif args.command == "healthcheck":
    healthcheck()
elif args.command == "resetpasses":
    reset_passes()
elif args.command == "resetstations":
    reset_stations()