import streamlit as st
from agent_logic import (
    find_best_pilot,
    find_best_drone,
    urgent_reassignment,
    update_pilot_status,
    get_available_pilots
)

st.set_page_config(page_title="Skylark Drone AI Coordinator", layout="wide")

st.title("🚁 Skylark Drone Operations AI Agent")
st.markdown("Ask anything about pilots, drones, and missions.")

# ==============================
# USER INPUT
# ==============================

user_query = st.text_input("💬 Enter your request")

# ==============================
# QUICK ACTION BUTTONS
# ==============================

st.subheader("⚡ Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Best Pilot → PRJ001"):
        result = find_best_pilot("PRJ001")
        st.success(result)

with col2:
    if st.button("Best Drone → PRJ001"):
        result = find_best_drone("PRJ001")
        st.success(result)

with col3:
    if st.button("Urgent Reassignment → PRJ002"):
        result = urgent_reassignment("PRJ002")
        st.success(result)

# ==============================
# PILOT STATUS UPDATE
# ==============================

st.subheader("🧑‍✈ Update Pilot Status")

pilot_id = st.text_input("Pilot ID")
new_status = st.selectbox("New Status", ["Available", "On Leave", "Assigned"])

if st.button("Update Status"):
    msg = update_pilot_status(pilot_id, new_status)
    st.success(msg)

# ==============================
# AVAILABLE PILOTS BY SKILL
# ==============================

st.subheader("🔍 Find Available Pilots by Skill")

skill = st.text_input("Enter Skill")

if st.button("Search Pilots"):
    result = get_available_pilots(skill)
    st.dataframe(result)

# ==============================
# SIMPLE CHAT INTERFACE
# ==============================

if user_query:

    query = user_query.lower()

    # Extract project id dynamically
    words = query.upper().split()
    project_ids = [word for word in words if word.startswith("PRJ")]

    project_id = project_ids[0] if project_ids else None

    if "pilot" in query and project_id:
        result = find_best_pilot(project_id)
        st.success(result)

    elif "drone" in query and project_id:
        result = find_best_drone(project_id)
        st.success(result)

    elif "urgent" in query and project_id:
        result = urgent_reassignment(project_id)
        st.success(result)

    else:
        st.warning("🤖 I didn’t understand. Try: best pilot for PRJ001")
