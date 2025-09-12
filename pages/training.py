import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.database import add_record, get_records, update_record


def show():
    st.title("📚 Training Management System")

    tab1, tab2, tab3 = st.tabs(["Register Family Training", "Training Records", "Training Modules"])

    with tab1:
        register_family_training()

    with tab2:
        view_training_records()

    with tab3:
        training_modules()


def register_family_training():
    st.subheader("📝 Register Family for Mandatory Training")

    st.info(
        "💡 **Note**: One family member must undergo training once every 10 years to learn proper waste segregation and rules.")

    with st.form("family_training_registration"):
        col1, col2 = st.columns(2)

        with col1:
            family_name = st.text_input("Family Name*", placeholder="Enter family surname")
            head_of_family = st.text_input("Head of Family*", placeholder="Full name of family head")
            contact_number = st.text_input("Contact Number*", placeholder="10-digit mobile number")
            email = st.text_input("Email Address", placeholder="Optional email for updates")

        with col2:
            address = st.text_area("Complete Address*", placeholder="House number, street, area, city, pincode")
            family_size = st.number_input("Family Size", min_value=1, max_value=20, value=4)
            previous_training = st.selectbox("Previous Training?", ["No", "Yes"])

            if previous_training == "Yes":
                last_training_year = st.number_input("Last Training Year",
                                                     min_value=2000,
                                                     max_value=datetime.now().year,
                                                     value=2020)

        training_preference = st.selectbox(
            "Training Preference*",
            ["Workshop (Community Center)", "Online Training", "Home Visit by Trainer"]
        )

        preferred_date = st.date_input("Preferred Training Date",
                                       min_value=datetime.now().date(),
                                       value=datetime.now().date() + timedelta(days=7))

        notes = st.text_area("Special Requirements", placeholder="Any special needs or requirements")

        submitted = st.form_submit_button("🎯 Register for Training")

        if submitted:
            if family_name and head_of_family and contact_number and address:
                # Check if training is due (10-year rule)
                training_due = True
                if previous_training == "Yes":
                    years_since_training = datetime.now().year - last_training_year
                    if years_since_training < 10:
                        training_due = False
                        st.warning(
                            f"⏳ Training not due yet! Last training was {years_since_training} years ago. Training required every 10 years.")

                if training_due:
                    # Register the family
                    training_record = {
                        'family_name': family_name,
                        'head_of_family': head_of_family,
                        'contact_number': contact_number,
                        'email': email,
                        'address': address,
                        'family_size': family_size,
                        'training_preference': training_preference,
                        'preferred_date': str(preferred_date),
                        'status': 'pending',
                        'notes': notes,
                        'registration_date': datetime.now().isoformat()
                    }

                    record = add_record('training_records.json', training_record)
                    st.success(f"✅ Family registered successfully! Training ID: {record['id']}")
                    st.info("📧 You will receive confirmation details via SMS/Email within 24 hours.")
            else:
                st.error("❌ Please fill in all required fields marked with *")


def view_training_records():
    st.subheader("📋 Training Records")

    records = get_records('training_records.json')

    if not records:
        st.info("📝 No training records found. Register families for training first.")
        return

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Scheduled", "Completed", "Cancelled"])
    with col2:
        training_type_filter = st.selectbox("Filter by Type", ["All", "Workshop (Community Center)", "Online Training",
                                                               "Home Visit by Trainer"])

    # Filter records
    filtered_records = records
    if status_filter != "All":
        filtered_records = [r for r in filtered_records if r.get('status', '').lower() == status_filter.lower()]
    if training_type_filter != "All":
        filtered_records = [r for r in filtered_records if r.get('training_preference', '') == training_type_filter]

    # Display records
    for record in filtered_records:
        with st.expander(
                f"🏠 {record.get('family_name', 'Unknown')} - {record.get('head_of_family', 'N/A')} (ID: {record.get('id', 'N/A')})"):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Status**: {record.get('status', 'Unknown').title()}")
                st.write(f"**Contact**: {record.get('contact_number', 'N/A')}")
                st.write(f"**Email**: {record.get('email', 'Not provided')}")
                st.write(f"**Family Size**: {record.get('family_size', 'N/A')}")

            with col2:
                st.write(f"**Training Type**: {record.get('training_preference', 'N/A')}")
                st.write(f"**Preferred Date**: {record.get('preferred_date', 'N/A')}")
                st.write(f"**Registration Date**: {record.get('registration_date', 'N/A')[:10]}")

            st.write(f"**Address**: {record.get('address', 'N/A')}")

            if record.get('notes'):
                st.write(f"**Notes**: {record.get('notes', '')}")

            # Update status
            new_status = st.selectbox(
                "Update Status",
                ["pending", "scheduled", "completed", "cancelled"],
                key=f"status_{record.get('id')}",
                index=["pending", "scheduled", "completed", "cancelled"].index(record.get('status', 'pending'))
            )

            if st.button(f"Update Status", key=f"update_{record.get('id')}"):
                update_record('training_records.json', record.get('id'), {'status': new_status})
                st.success(f"Status updated to {new_status}")
                st.rerun()


def training_modules():
    st.subheader("🎓 Training Modules")

    st.markdown("""
    ### 📚 Waste Segregation Training Curriculum

    #### Module 1: Understanding Waste Types
    - **Organic Waste**: Food scraps, garden waste, biodegradable materials
    - **Recyclable Waste**: Paper, plastic, glass, metal containers
    - **Hazardous Waste**: Batteries, electronics, chemicals, medical waste
    - **Non-Recyclable Waste**: Mixed materials, contaminated items

    #### Module 2: Proper Segregation Techniques
    - Color-coded bins system
    - Clean and dry recyclables
    - Separate hazardous materials
    - Composting organic waste

    #### Module 3: Collection Schedule and Rules
    - Weekly collection timings
    - Proper bin placement
    - QR code system usage
    - Penalties for improper segregation

    #### Module 4: Community Responsibility
    - Environmental impact awareness
    - Neighborhood cleanliness
    - Reporting violations
    - Reward system participation
    """)

    st.info("💡 Training sessions include practical demonstrations, Q&A sessions, and certification upon completion.")

    # Training statistics
    st.subheader("📊 Training Statistics")

    records = get_records('training_records.json')
    if records:
        status_counts = {}
        for record in records:
            status = record.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Registrations", len(records))
        with col2:
            st.metric("Completed", status_counts.get('completed', 0))
        with col3:
            st.metric("Pending", status_counts.get('pending', 0))
        with col4:
            st.metric("Scheduled", status_counts.get('scheduled', 0))
    else:
        st.info("No training data available yet.")
