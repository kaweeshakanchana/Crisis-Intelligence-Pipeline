import streamlit as st
import re
import pandas as pd
import json
import os
import random
import re
from pydantic import BaseModel, ValidationError
from typing import Literal, Optional

# Set page configuration for a beautiful UI
st.set_page_config(
    page_title="Crisis Intelligence Pipeline",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern look
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #4B5563;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #F3F4F6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F3F4F6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        padding-left: 20px;
        padding-right: 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #DBEAFE !important;
        color: #1E3A8A !important;
        border-bottom: 2px solid #1E3A8A;
    }
</style>
""", unsafe_allow_html=True)

# --- UTILITY FUNCTIONS ---
def count_tokens(text):
    return len(text.split())

def check_budget_and_truncate(text, limit=150):
    tokens = count_tokens(text)
    if tokens > limit:
        return text.split()[:50] + ["...TRUNCATED"], True
    return text, False

def mock_llm_response(prompt, task_type="classification", temperature=0.0):
    if task_type == "classification":
        prompt_lower = prompt.lower()
        
        # Extract District
        districts = ["colombo", "gampaha", "kandy", "kalutara", "galle", "matara", "ja-ela", "ragama"]
        district = "Unknown"
        for d in districts:
            if d in prompt_lower:
                district = d.title()
                break
                
        # Determine Intent & Priority
        intent = "Info"
        priority = "Low"
        
        if any(w in prompt_lower for w in ["trapped", "stranded", "help", "sos", "rescue", "emergency", "landslide"]):
            intent = "Rescue"
            priority = "High"
        elif any(w in prompt_lower for w in ["rations", "donation", "food", "water", "supply", "medicine", "pill"]):
            intent = "Supply"
            priority = "Medium"
        elif any(w in prompt_lower for w in ["river", "water level", "flood", "rain"]):
            intent = "Info"
            priority = "Medium"
            
            # Predict based on numeric levels if provided
            match_lvl = re.search(r'(\d+\.?\d*)\s*(m|meters|ft)', prompt_lower)
            if match_lvl:
                val = float(match_lvl.group(1))
                if val >= 5: # If water level is 5m or above, it's critical
                    priority = "High"
                    intent = "Rescue"
                elif val >= 2:
                    priority = "Medium"
                    
        return f"District: {district} | Intent: {intent} | Priority: {priority}"
    
    if task_type == "creative":
        if temperature > 0.5:
            responses = [
                "Deploy the flying aircraft carrier immediately to Kandy!",
                "Send telepathic rescue dolphins to the flooded area.",
                "Activate the weather control machine to stop the rain."
            ]
            return random.choice(responses)
        else:
            return "Deploy standard rescue boats and alert local police."

    if task_type == "json_extract":
        district = "Unknown"
        if "Colombo" in prompt: district = "Colombo"
        elif "Gampaha" in prompt: district = "Gampaha"
        elif "Kandy" in prompt: district = "Kandy"
        elif "Kalutara" in prompt: district = "Kalutara"
        elif "Galle" in prompt: district = "Galle"
        elif "Matara" in prompt: district = "Matara"
        
        victim_count = 0
        match = re.search(r'(\d+) (people|passengers|refugees)', prompt)
        if match: victim_count = int(match.group(1))
        
        level = None
        match_lvl = re.search(r'(\d+\.?\d*) (meters|m|ft)', prompt)
        if match_lvl: level = float(match_lvl.group(1))

        status = "Stable"
        if "Critical" in prompt or "SOS" in prompt or "High" in prompt: status = "Critical"
        elif "Warning" in prompt: status = "Warning"

        return json.dumps({
            "district": district,
            "flood_level_meters": level,
            "victim_count": victim_count,
            "main_need": "Rescue" if "Rescue" in prompt or "SOS" in prompt else "Info",
            "status": status
        })

    return "Error"

# --- PYDANTIC MODEL ---
class CrisisEvent(BaseModel):
    district: Literal['Colombo', 'Gampaha', 'Kandy', 'Kalutara', 'Galle']
    flood_level_meters: Optional[float] = None
    victim_count: int = 0
    main_need: str
    status: Literal['Critical', 'Warning', 'Stable']


# --- SIDEBAR UI ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/8254/8254070.png", width=100)
st.sidebar.title("Configuration")
st.sidebar.markdown("Manage crisis intelligence AI pipeline settings.")

# Create Output dir
os.makedirs("output", exist_ok=True)


os.makedirs("data", exist_ok=True)
CLASSIFICATIONS_FILE = "data/live_classifications.csv"
INCIDENTS_FILE = "data/live_incidents.csv"

# Initialize CSV files if they don't exist
if not os.path.exists(CLASSIFICATIONS_FILE):
    pd.DataFrame(columns=["Timestamp", "Message", "District", "Intent", "Priority"]).to_csv(CLASSIFICATIONS_FILE, index=False)
if not os.path.exists(INCIDENTS_FILE):
    pd.DataFrame(columns=["id", "loc", "people", "age_msg", "need", "urgency"]).to_csv(INCIDENTS_FILE, index=False)

def save_classification(msg, district, intent, priority):
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_data = pd.DataFrame([[timestamp, msg, district, intent, priority]], columns=["Timestamp", "Message", "District", "Intent", "Priority"])
    new_data.to_csv(CLASSIFICATIONS_FILE, mode='a', header=False, index=False)

def load_incidents():
    df = pd.read_csv(INCIDENTS_FILE)
    if df.empty:
        return []
    return df.to_dict('records')

def save_incident(loc, people, age_msg, need, urgency):
    df = pd.read_csv(INCIDENTS_FILE)
    new_id = int(df['id'].max()) + 1 if not df.empty else 1
    new_data = pd.DataFrame([[new_id, loc, people, age_msg, need, urgency]], columns=["id", "loc", "people", "age_msg", "need", "urgency"])
    new_data.to_csv(INCIDENTS_FILE, mode='a', header=False, index=False)

# --- MAIN UI ---
st.markdown('<div class="main-header">🚨 Crisis Intelligence Pipeline</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-powered analytics for rapid emergency response & logistics commander.</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📂 1. Classification (Few-Shot)", 
    "🧪 2. Stability Experiments", 
    "🗺️ 3. Logistics Commander", 
    "📰 4. News Feed Extraction",
    "📊 5. Live Dashboard"
])

# ----------------- TAB 1: CLASSIFICATION -----------------
with tab1:
    st.header("Classification Pipeline")
    st.markdown("Classifying incoming SOS messages and categorizing them by Intent, District, and Priority.")
    
    col_input, col_output = st.columns([1, 1])
    with col_input:
        st.subheader("Simulate Input")
        msg_input = st.text_area("Enter a crisis message:", "SOS: Trapped in Ja-Ela. Water level 5m.")
        classify_btn = st.button("Classify Message", type="primary")
        
    if classify_btn:
        with col_output:
            st.subheader("AI Analysis Result")
            processed_msg, truncated = check_budget_and_truncate(msg_input)
            if truncated:
                st.warning("⚠️ Message too long. Truncated to fit token budget.")
                msg_input_clean = " ".join(processed_msg)
            else:
                msg_input_clean = processed_msg
                
            response = mock_llm_response(msg_input_clean, task_type="classification")
            try:
                parts = response.split("|")
                d = parts[0].split(":")[1].strip()
                i = parts[1].split(":")[1].strip()
                p = parts[2].split(":")[1].strip()
                
                # Metrics layout
                c1, c2, c3 = st.columns(3)
                c1.metric("District", d)
                c2.metric("Intent", i)
                color = "red" if p == "High" else "orange" if p == "Medium" else "green"
                c3.markdown(f"**Priority:** <span style='color:{color}; font-size:1.5rem; font-weight:bold;'>{p}</span>", unsafe_allow_html=True)
                
                # Save dynamically
                save_classification(msg_input, d, i, p)
                st.success("✅ Analysis saved to dynamic database.")
                
            except:
                st.error("Failed to parse LLM Response.")
                
    st.divider()
    st.subheader("Batch Processing from Data Folder")
    if st.button("Run Batch Process on `Sample Messages.txt`"):
        classified_data = []
        try:
            with open("data/Sample Messages.txt", "r", encoding="utf-8") as f:
                messages = [m.strip() for m in f.read().split('\n') if m.strip()]
        except FileNotFoundError:
            messages = ["SOS: Trapped in Ja-Ela", "Water level 5m"]
            st.warning("File not found, using valid mock data.")
            
        progress_bar = st.progress(0)
        for idx, msg in enumerate(messages):
            processed_msg, _ = check_budget_and_truncate(msg)
            msg_text = " ".join(processed_msg) if isinstance(processed_msg, list) else processed_msg
            response = mock_llm_response(msg_text, task_type="classification")
            try:
                parts = response.split("|")
                classified_data.append({
                    "Message": msg[:50] + "..." if len(msg)>50 else msg, 
                    "District": parts[0].split(":")[1].strip(), 
                    "Intent": parts[1].split(":")[1].strip(), 
                    "Priority": parts[2].split(":")[1].strip()
                })
            except:
                pass
            progress_bar.progress((idx + 1) / len(messages))
            
        if classified_data:
            df_p1 = pd.DataFrame(classified_data)
            df_p1.to_excel("output/classified_messages.xlsx", index=False)
            st.success("✅ Batch Processed. Saved to `output/classified_messages.xlsx`")
            st.dataframe(df_p1, use_container_width=True)
            
            # Simple chart
            st.bar_chart(df_p1['Intent'].value_counts())

# ----------------- TAB 2: STABILITY EXPERIMENT -----------------
with tab2:
    st.header("Stability Experiment (Chaos vs Safe Mode)")
    st.markdown("Testing LLM temperature settings to observe hallucinations vs. safe output.")
    
    scenario_input = st.text_input("Test Scenario:", "THE KANDY LANDSLIDE - Uncle stuck in tree, diabetic patient in factory.")
    
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        st.subheader("Safe Mode (T=0.0)")
        if st.button("Run Safe Mode"):
            res = mock_llm_response(scenario_input, task_type="creative", temperature=0.0)
            st.info(f"**Output:** {res}")
            
    with t_col2:
        st.subheader("Chaos Mode (T=1.0)")
        if st.button("Run Chaos Mode (3 Iterations)"):
            for i in range(3):
                res = mock_llm_response(scenario_input, task_type="creative", temperature=1.0)
                st.warning(f"**Run {i+1}:** {res}")

    st.markdown("> **Comment:** Chaos mode produces unrealistic assets (e.g., aircraft carriers) while Safe mode sticks to standard real-world protocols.")

# ----------------- TAB 3: LOGISTICS COMMANDER -----------------
with tab3:
    st.header("Logistics Commander")
    st.markdown("Routing optimization using Chain-of-Thought (CoT) and Tree-of-Thought (ToT).")
    
    incidents = load_incidents()
    
    col_inc1, col_inc2 = st.columns([1, 2])
    with col_inc1:
        st.subheader("Add Incident")
        with st.form("add_incident_form"):
            loc = st.text_input("Location", "Colombo")
            people = st.number_input("People Affected", min_value=1, value=1)
            age_msg = st.text_input("Age/Demographic details", "20-40")
            need = st.text_input("Primary Need", "Rescue")
            urgency = st.selectbox("Urgency", ["Low", "Medium", "High", "Critical"])
            submit = st.form_submit_button("Add Incident")
            if submit:
                save_incident(loc, people, age_msg, need, urgency)
                st.success(f"Added incident at {loc}")
                st.rerun()

    with col_inc2:
        st.subheader("Current Incidents Database")
        if not incidents:
            st.info("No incidents in database. Please add one.")
        else:
            st.dataframe(pd.DataFrame(incidents), use_container_width=True)
    
        if st.button("Calculate Priority Scores & Optimal Route", type="primary") and incidents:
            st.subheader("Step A: Chain of Thought (CoT) Scoring")
            scored_incidents = []
            for inc in incidents:
                score = 5 # Base
                if "75" in str(inc['age_msg']): score += 2 
                if "Rescue" in str(inc['need']): score += 3
                if "Insulin" in str(inc['need']) or "Water" in str(inc['need']): score += 1
                inc['score'] = score
                scored_incidents.append(inc)
                
            st.dataframe(pd.DataFrame(scored_incidents)[['id', 'loc', 'score']].sort_values(by='score', ascending=False), use_container_width=True)
                
            st.subheader("Step B: Tree of Thought (ToT) Strategy")
            st.markdown("""
            **Starting Point:** Base Hub
            
            Based on dynamic scoring, the algorithm prioritizes the incident with the **highest score** first.
            """)
            
            sorted_inc = sorted(scored_incidents, key=lambda x: x['score'], reverse=True)
            path_str = "Base Hub -> " + " -> ".join([f"{i['loc']} (ID {i['id']})" for i in sorted_inc])
            
            st.markdown(f"🗺️ **Dynamic Path:** `{path_str}`")
            st.success("Optimal Route Selected.")

# ----------------- TAB 4: NEWS FEED EXTRACTION -----------------
with tab4:
    st.header("News Feed Extraction + Pydantic Validation")
    st.markdown("Extracting structured JSON objects from unstructured news data with rigorous schema validation.")
    
    if st.button("Process `News Feed.txt`", type="primary"):
        valid_events = []
        try:
            with open("data/News Feed.txt", "r", encoding="utf-8") as f:
                news_lines = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            st.error("`News Feed.txt` not found. Using defaults.")
            news_lines = ["Massive floods in Colombo, 50 people trapped. Need Rescue immediately.", "Matara underwater."]
            
        st.write(f"Processing {len(news_lines)} news items...")
        
        progress = st.progress(0)
        errors = []
        
        for idx, line in enumerate(news_lines):
            json_str = mock_llm_response(line, task_type="json_extract")
            try:
                data = json.loads(json_str)
                event = CrisisEvent(**data)
                valid_events.append(event.model_dump())
            except ValidationError as e:
                errors.append(f"Validation Error for line '{line[:30]}...': {e.errors()[0]['msg']}")
            except Exception:
                pass
            
            progress.progress((idx + 1) / len(news_lines))
            
        if valid_events:
            df_news = pd.DataFrame(valid_events)
            df_news.to_excel("output/flood_report.xlsx", index=False)
            st.success(f"✅ {len(valid_events)} valid records saved to `output/flood_report.xlsx`")
            st.dataframe(df_news, use_container_width=True)
            
            # Show charts
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.write("**Events by District**")
                st.bar_chart(df_news['district'].value_counts())
            with col_chart2:
                st.write("**Total Victims by Status**")
                status_vics = df_news.groupby('status')['victim_count'].sum().reset_index()
                st.bar_chart(status_vics.set_index('status'))
        else:
            st.warning("⚠️ No valid events found.")
            
        if errors:
            with st.expander("View Validation Errors (Failed Data)"):
                for err in errors:
                    st.write(f"- {err}")

# ----------------- TAB 5: LIVE DASHBOARD -----------------
with tab5:
    st.header("Live Analytics Dashboard")
    st.markdown("Real-time monitoring of dynamically structured crisis data.")
    
    col_dash1, col_dash2 = st.columns(2)
    
    with col_dash1:
        st.subheader("Classification Trends")
        df_class = pd.read_csv(CLASSIFICATIONS_FILE)
        if df_class.empty:
            st.info("No classification data recorded yet.")
        else:
            st.metric("Total Messages Processed", len(df_class))
            st.bar_chart(df_class['Intent'].value_counts())
            with st.expander("View Classification Data"):
                st.dataframe(df_class)

    with col_dash2:
        st.subheader("Logistics & Incidents")
        df_inc = pd.read_csv(INCIDENTS_FILE)
        if df_inc.empty:
            st.info("No incidents recorded yet.")
        else:
            st.metric("Active Incidents", len(df_inc))
            st.bar_chart(df_inc['urgency'].value_counts())
            with st.expander("View Incidents Data"):
                st.dataframe(df_inc)

