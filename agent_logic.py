import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

# ==============================
# GOOGLE SHEETS CONNECTION
# ==============================

@st.cache_resource
def connect_sheets():


    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)

    spreadsheet = client.open_by_url(
        "https://docs.google.com/spreadsheets/d/1d1gvR9GSyTdhWVVx5o2nPVNqbRoQk5toe5S9vJdvFoI"
    )

    pilot_sheet = spreadsheet.worksheet("pilot_roster")
    drone_sheet = spreadsheet.worksheet("drone_fleet")
    mission_sheet = spreadsheet.worksheet("missions")

    return pilot_sheet, drone_sheet, mission_sheet



# ==============================
# LOAD DATA
# ==============================

@st.cache_data(ttl=60)
def load_data():


    pilot_sheet, drone_sheet, mission_sheet = connect_sheets()

    pilots_df = pd.DataFrame(pilot_sheet.get_all_records())
    drones_df = pd.DataFrame(drone_sheet.get_all_records())
    missions_df = pd.DataFrame(mission_sheet.get_all_records())

    pilots_df["available_from"] = pd.to_datetime(pilots_df["available_from"])
    missions_df["start_date"] = pd.to_datetime(missions_df["start_date"])
    missions_df["end_date"] = pd.to_datetime(missions_df["end_date"])

    return pilots_df, drones_df, missions_df, pilot_sheet


# ==============================
# COST FUNCTION
# ==============================

def calculate_cost(rate_per_day, start_date, end_date):

    days = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days + 1
    return max(days, 0) * rate_per_day


# ==============================
# GET AVAILABLE PILOTS BY SKILL
# ==============================

def get_available_pilots(skill):

    pilots_df, _, _, _ = load_data()

    result = pilots_df[
        (pilots_df["status"].str.lower() == "available") &
        (pilots_df["skills"].str.contains(skill, case=False, na=False))
    ]

    return result


# ==============================
# UPDATE PILOT STATUS
# ==============================

def update_pilot_status(pilot_id, new_status):

    _, _, _, pilot_sheet = load_data()

    try:
        cell = pilot_sheet.find(pilot_id)
        headers = pilot_sheet.row_values(1)

        status_column = [i+1 for i, col in enumerate(headers) if col.lower() == "status"][0]

        pilot_sheet.update_cell(cell.row, status_column, new_status)

        return f"✅ Status of {pilot_id} updated to {new_status}"

    except:
        return "❌ Pilot ID not found"


# ==============================
# MATCHING CONDITIONS
# ==============================

def has_required_skill(pilot, mission):
    return mission["required_skills"].lower() in pilot["skills"].lower()

def is_available_for_dates(pilot, mission):
    return pilot["available_from"] <= mission["start_date"]

def location_match(entity, mission):
    return entity["location"] == mission["location"]

def within_budget(cost, mission):
    return cost <= mission["mission_budget_inr"]


# ==============================
# PRIORITY RANK
# ==============================

priority_rank = {
    "Low": 1,
    "Medium": 2,
    "High": 3,
    "Urgent": 4
}


# ==============================
# ⭐ BEST PILOT
# ==============================

def find_best_pilot(mission_id):

    pilots_df, _, missions_df, _ = load_data()

    mission = missions_df[missions_df["project_id"] == mission_id].iloc[0]

    available_pilots = pilots_df[pilots_df["status"].str.lower() == "available"]

    best = []

    for _, pilot in available_pilots.iterrows():

        if not has_required_skill(pilot, mission):
            continue

        if not is_available_for_dates(pilot, mission):
            continue

        cost = calculate_cost(
            pilot["daily_rate_inr"],
            mission["start_date"],
            mission["end_date"]
        )

        if not within_budget(cost, mission):
            continue

        score = 1 if location_match(pilot, mission) else 0

        best.append({
            "pilot": pilot["name"],
            "cost": cost,
            "location_match": score
        })

    if not best:
        return "❌ No suitable pilot found"

    return sorted(best, key=lambda x: (x["location_match"], -x["cost"]), reverse=True)[0]


# ==============================
# 🚨 URGENT REASSIGNMENT
# ==============================

def urgent_reassignment(mission_id):

    pilots_df, _, missions_df, _ = load_data()

    mission = missions_df[missions_df["project_id"] == mission_id].iloc[0]

    if mission["priority"] != "Urgent":
        return "⚠ Mission is not urgent"

    busy_pilots = pilots_df[pilots_df["status"].str.lower() == "assigned"]

    for _, pilot in busy_pilots.iterrows():

        if not has_required_skill(pilot, mission):
            continue

        cost = calculate_cost(
            pilot["daily_rate_inr"],
            mission["start_date"],
            mission["end_date"]
        )

        if cost > mission["mission_budget_inr"]:
            continue

        current_project = pilot["current_assignment"]

        current_mission = missions_df[
            missions_df["project_id"] == current_project
        ]

        if current_mission.empty:
            continue

        current_priority = current_mission.iloc[0]["priority"]

        if priority_rank[current_priority] < priority_rank[mission["priority"]]:

            return {
                "pilot": pilot["name"],
                "reassign_from": current_project,
                "reassign_to": mission_id,
                "impact": f"{current_project} will be delayed"
            }

    return "❌ No suitable pilot found for reassignment"


# ==============================
# 🚁 DRONE MATCHING
# ==============================

def weather_compatible(drone, mission):

    if "rain" in mission["weather_forecast"].lower() and "ip43" not in drone["weather_resistance"].lower():
        return False

    return True


def find_best_drone(mission_id):

    _, drones_df, missions_df, _ = load_data()

    mission = missions_df[missions_df["project_id"] == mission_id].iloc[0]

    available_drones = drones_df[drones_df["status"].str.lower() == "available"]

    best = []

    for _, drone in available_drones.iterrows():

        if drone["status"].lower() == "maintenance":
            continue

        if mission["required_skills"].lower() not in drone["capabilities"].lower():
            continue

        if not weather_compatible(drone, mission):
            continue

        score = 1 if location_match(drone, mission) else 0

        best.append({
            "drone_id": drone["drone_id"],
            "location_match": score
        })

    if not best:
        return "❌ No suitable drone found"

    return sorted(best, key=lambda x: x["location_match"], reverse=True)[0]
