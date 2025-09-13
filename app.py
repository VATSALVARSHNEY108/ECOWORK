import streamlit as st
import pandas as pd
from datetime import datetime
import os


from pages import training, household_management, waste_collection
from pages import worker_management, vehicle_tracking, treatment_plant
from pages import community_reporting, rewards_fines
from utils.database import init_database


def main():
    st.header("हाँ इस वत्सल वार्ष्णेय ने इसे बनाया है")

    st.set_page_config(
        page_title="Waste Management System",
        page_icon="♻️",
        layout="wide",
        initial_sidebar_state="expanded"
    )


    init_database()

    st.sidebar.title("♻️ Waste Management System")

    pages = {
        "🏠 Dashboard": "dashboard",
        "📚 Training Management": "training",
        "🏡 Household Management": "household",
        "🗑️ Waste Collection": "collection",
        "👷 Worker Management": "worker",
        "🚛 Vehicle Tracking": "vehicle",
        "🏭 Treatment Plant": "treatment",
        "📢 Community Reporting": "community",
        "🎁 Rewards & Fines": "rewards"
    }

    selected_page = st.sidebar.radio("Navigate to:", list(pages.keys()))
    page_key = pages[selected_page]

  
    if page_key == "dashboard":
        show_dashboard()
    elif page_key == "training":
        training.show()
    elif page_key == "household":
        household_management.show()
    elif page_key == "collection":
        waste_collection.show()
    elif page_key == "worker":
        worker_management.show()
    elif page_key == "vehicle":
        vehicle_tracking.show()
    elif page_key == "treatment":
        treatment_plant.show()
    elif page_key == "community":
        community_reporting.show()
    elif page_key == "rewards":
        rewards_fines.show()


def show_dashboard():
    st.title("🏠 Waste Management Dashboard")

    from utils.database import get_dashboard_stats
    stats = get_dashboard_stats()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Registered Families", stats.get('families', 0))

    with col2:
        st.metric("Active Workers", stats.get('workers', 0))

    with col3:
        st.metric("Collections Today", stats.get('collections_today', 0))

    with col4:
        st.metric("Community Reports", stats.get('community_reports', 0))

    # Recent activities
    st.subheader("📊 System Overview")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎯 Training Completion Rate")
        training_data = stats.get('training_completion', {'completed': 0, 'pending': 0})
        if training_data['completed'] + training_data['pending'] > 0:
            completion_rate = training_data['completed'] / (training_data['completed'] + training_data['pending']) * 100
            st.progress(completion_rate / 100)
            st.write(f"{completion_rate:.1f}% completion rate")
        else:
            st.info("No training data available")

    with col2:
        st.subheader("♻️ Segregation Quality")
        segregation_data = stats.get('segregation_quality', {'good': 0, 'poor': 0})
        if segregation_data['good'] + segregation_data['poor'] > 0:
            quality_rate = segregation_data['good'] / (segregation_data['good'] + segregation_data['poor']) * 100
            st.progress(quality_rate / 100)
            st.write(f"{quality_rate:.1f}% proper segregation")
        else:
            st.info("No segregation data available")

    st.subheader("🚨 Recent Alerts")
    alerts = stats.get('recent_alerts', [])
    if alerts:
        for alert in alerts[:5]:
            st.warning(f"**{alert.get('type', 'Alert')}**: {alert.get('message', 'No details available')}")
    else:
        st.info("No recent alerts")

    st.subheader("⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📚 Register New Family Training"):
            st.session_state.redirect_to = "training"
            st.rerun()

    with col2:
        if st.button("👷 Add New Worker"):
            st.session_state.redirect_to = "worker"
            st.rerun()

    with col3:
        if st.button("📢 View Community Reports"):
            st.session_state.redirect_to = "community"
            st.rerun()


if __name__ == "__main__":
    main()



