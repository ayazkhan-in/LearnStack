import streamlit as st
import google.generativeai as genai
import json
import re

# --- CONFIG ---
genai.configure(api_key="AIzaSyBfr-e5TXq4QeE5xZ2U3bRqdzYPZRxxD5s")
model = genai.GenerativeModel("gemini-2.0-flash")

# Show tip only if not dismissed before
if "sidebar_tip_shown" not in st.session_state:
    st.session_state.sidebar_tip_shown = True

if st.session_state.sidebar_tip_shown:
    with st.sidebar.expander("ℹ️ Tip", expanded=True):
        st.markdown("👉 On mobile, click **`<<`** at the top to open the sidebar.")
        if st.button("Got it!", key="dismiss_tip"):
            st.session_state.sidebar_tip_shown = False

st.set_page_config(page_title="LearnStack", page_icon="📌", layout="wide")
st.title("📌 LearnStack")
st.subheader("AI-powered structured learning plans")

# --- SIDEBAR INPUT & EXPORT ---
with st.sidebar:
    topic = st.text_input("Topic", "Python")
    total_time = st.text_input("Total time (e.g. '10 hrs', '3 weeks')", "10 hrs")
    depth = st.slider("Depth (1=basic, 5=expert)", 1, 5, 3)

    if st.button("Generate Plan"):
        prompt = (
            f"Create a structured learning plan for {topic}.\n"
            f"Total time: {total_time}.\n"
            f"Depth: {depth} (1=basic, 5=expert).\n"
            "Each task should include: title, description, and estimated time (use the same format as total time).\n"
            "Format output strictly as JSON list only, with no text before or after:\n"
            '[{"title": "...", "description": "...", "time": "..."}, ...]'
        )
        response = model.generate_content(prompt)
        match = re.search(r"\[.*\]", response.text.strip(), re.S)
        if match:
            try:
                st.session_state.tasks = json.loads(match.group())
                st.session_state.completed = [False] * len(st.session_state.tasks)
            except Exception as e:
                st.error(f"Failed to parse Gemini JSON: {e}")
        else:
            st.error("No valid JSON found in Gemini response.")

    if st.button("Export to Notion") and "tasks" in st.session_state:
        md = f"# 📚 Learning Plan for: {topic}\n\n"
        for i, task in enumerate(st.session_state.tasks):
            box = "[x]" if st.session_state.completed[i] else "[ ]"
            md += f"- {box} **{task['title']}** ({task['time']})\n    {task['description']}\n\n"
        st.markdown("### Copy the Markdown below and paste into Notion:")
        st.code(md, language="markdown")

# --- MAIN: SHOW TASKS & PROGRESS ---
if "tasks" in st.session_state:
    st.subheader(f"📚 Learning Plan for: {topic}")
    tasks = st.session_state.tasks
    completed = st.session_state.completed

    for i, task in enumerate(tasks):
        col1, col2 = st.columns([0.08, 0.92])
        with col1:
            checked = st.checkbox("", value=completed[i], key=f"cb{i}", label_visibility="hidden")
            completed[i] = checked
        with col2:
            card_bg = "#2e7d32" if checked else "#232323"
            text_color = "#fff" if checked else "#ddd"
            st.markdown(
                f"""
                <div style="
                    background-color:{card_bg};
                    padding:18px 24px 18px 18px;
                    margin-bottom:18px;
                    border-radius:18px;
                    box-shadow:0 3px 8px rgba(0,0,0,0.18);
                ">
                    <h4 style="margin:0; color:{text_color}; font-size:1.6rem;">
                        {'✅' if checked else '⏳'} {task['title']} — <span style="font-size:1.1rem;">⏱ {task['time']}</span>
                    </h4>
                    <p style="margin:10px 0 0; color:{text_color}; font-size:1.08rem;">
                        {task['description']}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.session_state.completed = completed
    st.progress(sum(completed) / len(tasks))
    st.write(f"**Progress:** {sum(completed)}/{len(tasks)} tasks completed ✅")

