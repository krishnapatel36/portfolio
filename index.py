import streamlit as st
import json
import os
from datetime import date

TASKS_FILE = "tasks.json"

if os.path.exists(TASKS_FILE):
    with open(TASKS_FILE, "r") as f:
        tasks = json.load(f)
else:
    tasks = []

if "tasks" not in st.session_state:
    st.session_state.tasks = tasks

today = str(date.today())
if "current_day" not in st.session_state:
    st.session_state.current_day = today
elif st.session_state.current_day != today:
    for task in st.session_state.tasks:
        task["done"] = False
    st.session_state.current_day = today

def save_tasks():
    with open(TASKS_FILE, "w") as f:
        json.dump(st.session_state.tasks, f)

st.sidebar.title("👋 Hello Krishna")
st.sidebar.markdown("---")

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
                "department": department
            })
            save_tasks()
            st.success(f"Task added to {department}!")

st.sidebar.markdown("---")

st.sidebar.subheader("📌 Filter Tasks")
department_filter = st.sidebar.selectbox(
    "Select Department",
    ["All", "Odoo", "Home"],
    key="filter_department"
)

st.title("📋 My Task Manager")
st.markdown("---")

st.subheader("📝 Task Dashboard")

cols = st.columns([0.05, 0.5, 0.25, 0.15])
cols[0].markdown("✅")
cols[1].markdown("Task")
cols[2].markdown("Department")
cols[3].markdown("Delete")
st.markdown("---")

filtered_tasks = st.session_state.tasks if department_filter == "All" else [
    t for t in st.session_state.tasks if t["department"] == department_filter
]

for task in filtered_tasks:
    cols = st.columns([0.05, 0.5, 0.25, 0.15])

    checked = cols[0].checkbox("", value=task["done"], key=f"done_{task['id']}")
    task["done"] = checked

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

    cols[2].markdown(task["department"])

    if cols[3].button("❌", key=f"del_{task['id']}"):
        st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != task["id"]]
        save_tasks()

save_tasks()
