import streamlit as st
import json
import os
from datetime import datetime, date
import calendar

TASKS_FILE = "tasks.json"

# --- Load tasks ---
if os.path.exists(TASKS_FILE):
    with open(TASKS_FILE, "r") as f:
        tasks = json.load(f)
else:
    tasks = []

# --- Session state ---
if "tasks" not in st.session_state:
    st.session_state.tasks = tasks
if "selected_date" not in st.session_state:
    st.session_state.selected_date = date.today()

# --- Save function ---
def save_tasks():
    with open(TASKS_FILE, "w") as f:
        json.dump(st.session_state.tasks, f, indent=4)

# --- Sidebar: Month calendar ---
st.sidebar.title("📅 Current Month")
today = date.today()
year = today.year
month = today.month
num_days = calendar.monthrange(year, month)[1]  # correct last day of month
first_weekday = calendar.monthrange(year, month)[0]  # 0=Monday

st.sidebar.markdown("### Select Day")

# Weekday headers
weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
cols = st.sidebar.columns(7)
for i, wd in enumerate(weekdays):
    cols[i].markdown(f"**{wd}**", unsafe_allow_html=True)

# Generate calendar grid
day = 1
while day <= num_days:
    cols = st.sidebar.columns(7)
    for i in range(7):
        if day == 1 and i < first_weekday:
            cols[i].markdown(" ")  # empty cell
            continue
        if day > num_days:
            cols[i].markdown(" ")
            continue

        day_date = date(year, month, day)
        day_str = day_date.strftime("%Y-%m-%d")
        day_tasks = [t for t in st.session_state.tasks if t["date"] == day_str]
        all_done = len(day_tasks) > 0 and all(t["done"] for t in day_tasks)

        # Show tick if all tasks done
        label = f"{day} ✅" if all_done else str(day)

        # Highlight today
        style = "text-align:center; padding:5px; border-radius:5px;"
        style += "background-color:#2196F3; color:white;" if day_date == today else "background-color:#f0f0f0; color:black;"

        # Button with styled label
        if cols[i].button(label, key=f"btn_{day_str}"):
            st.session_state.selected_date = day_date

        day += 1

st.sidebar.markdown("---")

# --- Add new task ---
with st.sidebar.expander("➕ Add New Task"):
    new_task = st.text_input("Task Name", key="sidebar_new_task_input")
    department = st.selectbox("Department", ["Odoo", "Home"], key="sidebar_department")
    if st.button("Add Task", key="sidebar_add_task"):
        if new_task.strip() != "":
            task_id = len(st.session_state.tasks) + 1
            st.session_state.tasks.append({
                "id": task_id,
                "title": new_task,
                "done": False,
                "department": department,
                "date": st.session_state.selected_date.strftime("%Y-%m-%d"),
                "time_done": None
            })
            save_tasks()
            st.success(f"Task added to {department} on {st.session_state.selected_date}!")

st.sidebar.markdown("---")
st.sidebar.subheader("📌 Filter Tasks by Department")
department_filter = st.sidebar.selectbox(
    "Select Department",
    ["All", "Odoo", "Home"],
    key="filter_department"
)

# --- Main App ---
st.title("📋 My Task Manager")
st.markdown(f"### Tasks for {st.session_state.selected_date.strftime('%B %d, %Y')}")
st.markdown("---")

# --- Dashboard headers ---
cols = st.columns([0.05, 0.5, 0.2, 0.2, 0.15])
cols[0].markdown("✅")
cols[1].markdown("Task")
cols[2].markdown("Department")
cols[3].markdown("Done Time")
cols[4].markdown("Delete")
st.markdown("---")

# --- Filter tasks by selected date & department ---
filtered_tasks = [
    t for t in st.session_state.tasks
    if t["date"] == st.session_state.selected_date.strftime("%Y-%m-%d") and
       (department_filter == "All" or t["department"] == department_filter)
]

# --- Display tasks ---
for task in filtered_tasks:
    cols = st.columns([0.05, 0.5, 0.2, 0.2, 0.15])

    # Checkbox
    checked = cols[0].checkbox("", value=task["done"], key=f"done_{task['id']}")
    if checked and not task["done"]:
        task["time_done"] = datetime.now().strftime("%H:%M:%S")
    elif not checked:
        task["time_done"] = None
    task["done"] = checked

    # Task title
    if checked:
        cols[1].markdown(f"~~{task['title']}~~")
    else:
        task_title = cols[1].text_input(
            "Task Title",
            value=task["title"],
            key=f"title_{task['id']}",
            label_visibility="collapsed"
        )
        task["title"] = task_title

    # Department
    cols[2].markdown(task["department"])

    # Time done
    cols[3].markdown(task["time_done"] or "-")

    # Delete
    if cols[4].button("❌", key=f"del_{task['id']}"):
        st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != task["id"]]
        save_tasks()

# --- Save tasks ---
save_tasks()
