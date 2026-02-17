import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ==============================
# LOAD LOCAL CSV (for testing)
# ==============================

pilots = pd.read_csv("pilot_roster.csv")
drones = pd.read_csv("drone_fleet.csv")
missions = pd.read_csv("missions.csv")

# Convert dates
pilots["available_from"] = pd.to_datetime(pilots["available_from"])
missions["start_date"] = pd.to_datetime(missions["start_date"])
missions["end_date"] = pd.to_datetime(missions["end_date"])

print("✅ Local CSV Data Loaded\n")

# ==============================
# GOOGLE SHEETS CONNECTION
# ==============================

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)

pilot_sheet = client.open("pilot_roster").sheet1
drone_sheet = client.open("drone_fleet").sheet1

pilot_data = pilot_sheet.get_all_records()
drone_data = drone_sheet.get_all_records()

pilots_df = pd.DataFrame(pilot_data)
drones_df = pd.DataFrame(drone_data)

# Convert dates for sheet data
pilots_df["available_from"] = pd.to_datetime(pilots_df["available_from"])

print("✅ Data from Google Sheets\n")

# ==============================
# EXISTING FUNCTIONS
# ==============================

def calculate_cost(rate_per_day, start_date, end_date):

    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)

    days = (end - start).days + 1

    if days <= 0:
        return 0

    return days * rate_per_day


def update_pilot_status(pilot_id, new_status):

    try:
        cell = pilot_sheet.find(pilot_id)

        headers = pilot_sheet.row_values(1)

        status_column = None
        for i, col_name in enumerate(headers):
            if col_name.lower() == "status":
                status_column = i + 1
                break

        pilot_sheet.update_cell(cell.row, status_column, new_status)

        print(f"✅ Status of {pilot_id} updated to {new_status}")

    except:
        print("❌ Pilot ID not found")


# ==============================
# CORE LOGIC FUNCTIONS
# ==============================

def has_required_skill(pilot, mission):
    return mission["required_skills"].lower() in pilot["skills"].lower()


def is_available_for_dates(pilot, mission):
    return pilot["available_from"] <= mission["start_date"]


def location_match(pilot, mission):
    return pilot["location"] == mission["location"]


def within_budget(cost, mission):
    return cost <= mission["mission_budget_inr"]


# ==============================
# ⭐ BEST PILOT SELECTION ENGINE
# ==============================

def find_best_pilot(mission_id):

    mission = missions[missions["project_id"] == mission_id].iloc[0]

    print(f"\n🚀 Finding best pilot for mission: {mission_id}")

    available_pilots = pilots_df[pilots_df["status"].str.lower() == "available"]

    if available_pilots.empty:
        print("❌ No available pilots")
        return

    best_pilots = []

    for _, pilot in available_pilots.iterrows():

        # Skill check
        if not has_required_skill(pilot, mission):
            continue

        # Date availability
        if not is_available_for_dates(pilot, mission):
            continue

        # Cost calculation
        cost = calculate_cost(
            pilot["daily_rate_inr"],
            mission["start_date"],
            mission["end_date"]
        )

        # Budget check
        if not within_budget(cost, mission):
            print(f"⚠ {pilot['name']} exceeds budget")
            continue

        score = 0

        if location_match(pilot, mission):
            score += 1

        best_pilots.append({
            "name": pilot["name"],
            "cost": cost,
            "location_match": score
        })

    if not best_pilots:
        print("❌ No suitable pilot found")
        return

    best_pilots = sorted(
        best_pilots,
        key=lambda x: (x["location_match"], -x["cost"]),
        reverse=True
    )

    print("\n✅ BEST PILOT FOUND:")
    print(best_pilots[0])

def urgent_reassignment(mission_id):

    mission = missions[missions["project_id"] == mission_id].iloc[0]

    print(f"\n🚨 URGENT REASSIGNMENT CHECK FOR: {mission_id}")

    if mission["priority"] != "Urgent":
        print("⚠ Mission is not urgent")
        return

    busy_pilots = pilots_df[pilots_df["status"].str.lower() == "assigned"]

    if busy_pilots.empty:
        print("❌ No pilots available for reassignment")
        return

    for _, pilot in busy_pilots.iterrows():

        # Skill check
        if mission["required_skills"].lower() not in pilot["skills"].lower():
            continue

        cost = calculate_cost(
            pilot["daily_rate_inr"],
            mission["start_date"],
            mission["end_date"]
        )

        if cost > mission["mission_budget_inr"]:
            continue

        current_project = pilot["current_assignment"]

        # Get current mission priority
        current_mission = missions[missions["project_id"] == current_project]

        if current_mission.empty:
            continue

        current_priority = current_mission.iloc[0]["priority"]

        if priority_rank[current_priority] < priority_rank[mission["priority"]]:

            print("\n✅ REASSIGNMENT POSSIBLE")
            print(f"👨‍✈ Pilot: {pilot['name']}")
            print(f"🔁 Move from: {current_project} → {mission_id}")
            print(f"📉 Impact: {current_project} will be delayed")

            return

    print("❌ No suitable pilot found for reassignment")

# ==============================
# TEST
# ==============================
urgent_reassignment("PRJ002")

find_best_pilot("PRJ001")
find_best_pilot("PRJ002")
find_best_pilot("PRJ003")
