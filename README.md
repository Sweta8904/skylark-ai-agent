# 🚁 Skylark Drone Operations – AI Coordinator Agent

## 📌 Overview

This project is an AI-powered Drone Operations Coordinator that automates:

- Pilot roster management
- Mission assignment
- Drone allocation
- Conflict detection
- Urgent mission reassignment

It replaces manual coordination across spreadsheets and messaging tools with a single intelligent interface.

The agent reads live data from Google Sheets, makes decisions based on operational constraints, and writes updates back to the sheet.

---

## ⚙️ Tech Stack

- Python
- Pandas
- Streamlit (Conversational UI)
- Google Sheets API (gspread)
- OAuth2 Service Account

---

## 🧠 Core Features

### 👨‍✈️ Pilot Management
- Query available pilots by skill
- Cost calculation based on mission duration
- Budget validation
- Live status update (2-way sync with Google Sheets)

### 📦 Assignment Tracking
- Intelligent pilot-to-mission matching
- Location-aware selection
- Reassignment handling

### 🚁 Drone Allocation
- Capability matching
- Weather compatibility check
- Maintenance conflict detection
- Location-based prioritization

### ⚠️ Conflict Detection
- Budget overrun warnings
- Skill mismatch detection
- Weather risk alerts
- Maintenance conflicts
- Availability validation

### 🚨 Urgent Reassignment Engine
When no pilot is available for an urgent mission:
- System evaluates pilots assigned to lower-priority missions
- Finds a valid reassignment candidate
- Displays operational impact

---

## 💬 Conversational Interface

Users can interact with the system using natural queries such as:

- “Find best pilot for PRJ001”
- “Assign drone for PRJ002”
- “Show available Mapping pilots”
- “Handle urgent mission”

---

## 🔄 Google Sheets Integration

### Read:
- Pilot roster
- Drone fleet
- Missions

### Write:
- Pilot status updates (live sync)

---

## 🏗️ Architecture

Streamlit UI  
↓  
Decision Engine (agent_logic.py)  
↓  
Google Sheets (Live Data Source)

---

## ▶️ How to Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
