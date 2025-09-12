import streamlit as st
import pandas as pd
from datetime import datetime
import json
from utils.database import add_record, get_records, update_record
from utils.qr_generator import create_household_qr, display_qr_code


def show():
    st.title("🏡 Household Management System")

    tab1, tab2, tab3 = st.tabs(
        ["Register Household", "Manage QR Codes", "Household Directory"])

    with tab1:
        register_household()

    with tab2:
        manage_qr_codes()

    with tab3:
        household_directory()


def register_household():
    st.subheader("🏠 Register New Household")

    st.info(
        "💡 **Note**: Household registration requires completed mandatory training. QR codes will be generated after successful registration."
    )

    with st.form("household_registration"):
        col1, col2 = st.columns(2)

        with col1:
            family_name = st.text_input("Family Name*",
                                        placeholder="Enter family surname")
            head_of_family = st.text_input("Head of Family*",
                                           placeholder="Full name")
            contact_number = st.text_input(
                "Contact Number*", placeholder="10-digit mobile number")
            email = st.text_input("Email Address",
                                  placeholder="Optional email")

        with col2:
            address = st.text_area(
                "Complete Address*",
                placeholder="House number, street, area, city, pincode")
            family_size = st.number_input("Family Size",
                                          min_value=1,
                                          max_value=20,
                                          value=4)
            house_type = st.selectbox(
                "House Type",
                ["Apartment", "Independent House", "Villa", "Other"])
            collection_preference = st.selectbox(
                "Collection Time Preference", [
                    "Morning (6-9 AM)", "Afternoon (12-3 PM)",
                    "Evening (6-8 PM)"
                ])

        # Training verification
        st.subheader("🎓 Training Verification")
        training_records = get_records('training_records.json',
                                       {'status': 'completed'})

        if training_records:
            training_options = [
                f"{r['family_name']} - {r['head_of_family']} (ID: {r['id']})"
                for r in training_records
            ]
            training_options.insert(0, "Select completed training record")

            selected_training = st.selectbox("Select Training Record*",
                                             training_options)
        else:
            st.warning(
                "⚠️ No completed training records found. Families must complete training before registration."
            )
            selected_training = None

        bin_types = st.multiselect(
            "Bin Types Required*", [
                "Organic Waste", "Recyclable Waste", "Hazardous Waste",
                "General Waste"
            ],
            default=["Organic Waste", "Recyclable Waste", "General Waste"])

        special_requirements = st.text_area(
            "Special Requirements",
            placeholder="Medical waste, large items, etc.")

        submitted = st.form_submit_button("🏠 Register Household")

        if submitted:
            if (family_name and head_of_family and contact_number and address
                    and selected_training
                    and selected_training != "Select completed training record"
                    and bin_types):

                # Extract training ID
                training_id = selected_training.split("ID: ")[1].split(")")[0]

                # Register household
                household_record = {
                    'family_name': family_name,
                    'head_of_family': head_of_family,
                    'contact_number': contact_number,
                    'email': email,
                    'address': address,
                    'family_size': family_size,
                    'house_type': house_type,
                    'collection_preference': collection_preference,
                    'training_id': training_id,
                    'bin_types': bin_types,
                    'special_requirements': special_requirements,
                    'status': 'active',
                    'registration_date': datetime.now().isoformat(),
                    'qr_generated': False
                }

                record = add_record('families', household_record)

                # Generate QR code
                qr_img = create_household_qr(record['id'], family_name,
                                             address)

                if qr_img:
                    # Update record with QR generated flag
                    update_record('families', record['id'],
                                  {'qr_generated': True})

                    st.success(
                        f"✅ Household registered successfully! Family ID: {record['id']}"
                    )
                    st.subheader("📱 Your QR Code")
                    display_qr_code(qr_img, f"Family QR - {family_name}")

                    st.info("""
                    📋 **Next Steps**:
                    1. Print and stick this QR code on your waste bins or house wall
                    2. QR code can be re-downloaded anytime from the 'Manage QR Codes' tab
                    3. Waste collectors will scan this code during collection
                    """)
                else:
                    st.error(
                        "❌ Household registered but QR code generation failed")
            else:
                st.error(
                    "❌ Please fill in all required fields and select a completed training record"
                )


def manage_qr_codes():
    st.subheader("📱 QR Code Management")

    families = get_records('families')

    if not families:
        st.info("🏠 No registered households found. Register families first.")
        return

    # Search and filter
    col1, col2 = st.columns(2)
    with col1:
        search_term = st.text_input("🔍 Search Family",
                                    placeholder="Enter family name or ID")
    with col2:
        status_filter = st.selectbox(
            "Filter by Status", ["All", "Active", "Inactive", "Suspended"])

    # Filter families
    filtered_families = families
    if search_term:
        filtered_families = [
            f for f in filtered_families
            if search_term.lower() in f.get('family_name', '').lower()
            or search_term in str(f.get('id', ''))
        ]

    if status_filter != "All":
        filtered_families = [
            f for f in filtered_families
            if f.get('status', '').lower() == status_filter.lower()
        ]

    # Display families with QR management
    for family in filtered_families:
        with st.expander(
                f"🏠 {family.get('family_name', 'Unknown')} - ID: {family.get('id', 'N/A')}"
        ):
            col1, col2 = st.columns(2)

            with col1:
                st.write(
                    f"**Head of Family**: {family.get('head_of_family', 'N/A')}"
                )
                st.write(f"**Contact**: {family.get('contact_number', 'N/A')}")
                st.write(f"**Address**: {family.get('address', 'N/A')}")
                st.write(f"**Status**: {family.get('status', 'Unknown')}")

            with col2:
                st.write(
                    f"**Family Size**: {family.get('family_size', 'N/A')}")
                st.write(f"**House Type**: {family.get('house_type', 'N/A')}")
                st.write(
                    f"**Collection Preference**: {family.get('collection_preference', 'N/A')}"
                )
                st.write(
                    f"**QR Generated**: {'✅ Yes' if family.get('qr_generated') else '❌ No'}"
                )

            # QR Code Actions
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button(f"📱 Generate/Regenerate QR",
                             key=f"gen_qr_{family.get('id')}"):
                    qr_img = create_household_qr(family.get('id'),
                                                 family.get('family_name'),
                                                 family.get('address'))

                    if qr_img:
                        update_record('families', family.get('id'),
                                      {'qr_generated': True})
                        st.success("QR Code regenerated!")
                        display_qr_code(
                            qr_img, f"Family QR - {family.get('family_name')}")

            with col2:
                if family.get('qr_generated'):
                    if st.button(f"📥 Download QR",
                                 key=f"dl_qr_{family.get('id')}"):
                        qr_img = create_household_qr(family.get('id'),
                                                     family.get('family_name'),
                                                     family.get('address'))
                        if qr_img:
                            display_qr_code(
                                qr_img,
                                f"Family QR - {family.get('family_name')}")

            with col3:
                new_status = st.selectbox(
                    "Update Status", ["active", "inactive", "suspended"],
                    key=f"status_{family.get('id')}",
                    index=["active", "inactive",
                           "suspended"].index(family.get('status', 'active')))

                if st.button(f"Update", key=f"update_{family.get('id')}"):
                    update_record('families', family.get('id'),
                                  {'status': new_status})
                    st.success(f"Status updated to {new_status}")
                    st.rerun()


def household_directory():
    st.subheader("📖 Household Directory")

    families = get_records('families')

    if not families:
        st.info("🏠 No registered households found.")
        return

    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Families", len(families))

    with col2:
        active_families = len(
            [f for f in families if f.get('status') == 'active'])
        st.metric("Active Families", active_families)

    with col3:
        qr_generated = len([f for f in families if f.get('qr_generated')])
        st.metric("QR Codes Generated", qr_generated)

    with col4:
        total_people = sum([f.get('family_size', 0) for f in families])
        st.metric("Total People", total_people)

    # Detailed table
    st.subheader("📊 Family Details")

    # Convert to DataFrame for better display
    df_data = []
    for family in families:
        df_data.append({
            'ID':
            family.get('id', 'N/A'),
            'Family Name':
            family.get('family_name', 'N/A'),
            'Head of Family':
            family.get('head_of_family', 'N/A'),
            'Contact':
            family.get('contact_number', 'N/A'),
            'Family Size':
            family.get('family_size', 0),
            'House Type':
            family.get('house_type', 'N/A'),
            'Status':
            family.get('status', 'Unknown'),
            'QR Generated':
            '✅' if family.get('qr_generated') else '❌',
            'Registration Date':
            family.get('registration_date', 'N/A')[:10]
            if family.get('registration_date') else 'N/A'
        })

    if df_data:
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)

    # Export option
    if st.button("📥 Export Directory"):
        if df_data:
            csv = pd.DataFrame(df_data).to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=
                f"household_directory_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv")
