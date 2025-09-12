import streamlit as st
import pandas as pd
from datetime import datetime, date
import json
from utils.database import add_record, get_records, update_record


def show():
    st.title("🗑️ Waste Collection Management")

    tab1, tab2, tab3 = st.tabs(["QR Scanning & Collection", "Collection Records", "Route Management"])

    with tab1:
        qr_scanning_collection()

    with tab2:
        collection_records()

    with tab3:
        route_management()


def qr_scanning_collection():
    st.subheader("📱 QR Code Scanning & Collection Update")

    # Simulate QR code scanning
    st.info("📱 **QR Scanner Simulation**: In a real deployment, this would use camera-based QR scanning.")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📱 Scan QR Code")

        # QR Code input simulation
        qr_input_method = st.radio("QR Input Method", ["Scan Simulation", "Manual Entry"])

        if qr_input_method == "Scan Simulation":
            # Simulate scanning by selecting from registered families
            families = get_records('families', {'status': 'active'})
            if families:
                family_options = [f"Family: {f['family_name']} (ID: {f['id']})" for f in families]
                family_options.insert(0, "Select family to simulate scan")

                selected_family = st.selectbox("🏠 Simulate QR Scan", family_options)

                if selected_family and selected_family != "Select family to simulate scan":
                    family_id = selected_family.split("ID: ")[1].split(")")[0]
                    st.session_state['scanned_family_id'] = family_id
                    st.success(f"✅ QR Code Scanned! Family ID: {family_id}")
            else:
                st.warning("⚠️ No active families found for scanning simulation")

        else:  # Manual Entry
            manual_family_id = st.text_input("Enter Family ID", placeholder="Enter family ID from QR code")
            if manual_family_id and st.button("🔍 Verify Family ID"):
                st.session_state['scanned_family_id'] = manual_family_id
                st.success(f"✅ Family ID Verified: {manual_family_id}")

    with col2:
        st.subheader("📝 Collection Update Form")

        if 'scanned_family_id' in st.session_state:
            family_id = st.session_state['scanned_family_id']

            # Get family details
            families = get_records('families', {'id': int(family_id)})
            if families:
                family = families[0]

                st.info(f"📍 **Collection Location**: {family.get('family_name')} - {family.get('address')}")

                with st.form("collection_update"):
                    col1, col2 = st.columns(2)

                    with col1:
                        collection_date = st.date_input("Collection Date", value=date.today())
                        collection_time = st.time_input("Collection Time", value=datetime.now().time())
                        collector_name = st.text_input("Collector Name*", placeholder="Name of waste collector")
                        vehicle_number = st.text_input("Vehicle Number", placeholder="Waste collection vehicle number")

                    with col2:
                        waste_types_collected = st.multiselect(
                            "Waste Types Collected*",
                            ["Organic Waste", "Recyclable Waste", "Hazardous Waste", "General Waste"],
                            default=["Organic Waste", "Recyclable Waste"]
                        )

                        segregation_quality = st.selectbox(
                            "Segregation Quality*",
                            ["Good - Properly segregated",
                             "Average - Minor issues",
                             "Poor - Improperly segregated"]
                        )

                        quantity_estimate = st.selectbox(
                            "Quantity Estimate",
                            ["Small (< 5kg)", "Medium (5-15kg)", "Large (> 15kg)"]
                        )

                    # Additional details
                    st.subheader("📋 Additional Information")

                    col1, col2 = st.columns(2)

                    with col1:
                        bins_present = st.checkbox("All bins were present", value=True)
                        household_cooperative = st.checkbox("Household was cooperative", value=True)
                        contamination_issues = st.checkbox("Contamination issues found")

                    with col2:
                        special_items = st.checkbox("Special items collected (electronics, furniture)")
                        missed_collection = st.checkbox("Previously missed collection")
                        payment_required = st.checkbox("Payment/fine collected")

                    collection_notes = st.text_area("Collection Notes",
                                                    placeholder="Any additional observations or issues")

                    # Photo upload simulation
                    st.subheader("📷 Collection Evidence")
                    uploaded_files = st.file_uploader("Upload Photos (Optional)",
                                                      accept_multiple_files=True,
                                                      type=['png', 'jpg', 'jpeg'])

                    submitted = st.form_submit_button("✅ Submit Collection Update")

                    if submitted:
                        if collector_name and waste_types_collected and segregation_quality:
                            # Process segregation quality
                            quality_map = {
                                "Good - Properly segregated": "good",
                                "Average - Minor issues": "average",
                                "Poor - Improperly segregated": "poor"
                            }

                            # Create collection record
                            collection_record = {
                                'family_id': int(family_id),
                                'family_name': family.get('family_name'),
                                'address': family.get('address'),
                                'collection_date': str(collection_date),
                                'collection_time': str(collection_time),
                                'collector_name': collector_name,
                                'vehicle_number': vehicle_number,
                                'waste_types_collected': waste_types_collected,
                                'segregation_quality': quality_map[segregation_quality],
                                'quantity_estimate': quantity_estimate,
                                'bins_present': bins_present,
                                'household_cooperative': household_cooperative,
                                'contamination_issues': contamination_issues,
                                'special_items': special_items,
                                'missed_collection': missed_collection,
                                'payment_required': payment_required,
                                'collection_notes': collection_notes,
                                'photos_uploaded': len(uploaded_files) if uploaded_files else 0,
                                'created_at': datetime.now().isoformat()
                            }

                            record = add_record('collections', collection_record)

                            st.success(f"✅ Collection updated successfully! Record ID: {record['id']}")

                            # Clear the scanned family for next collection
                            del st.session_state['scanned_family_id']

                            # Show rewards/penalties based on segregation quality
                            if collection_record['segregation_quality'] == 'good':
                                st.success("🎁 Family eligible for reward points!")
                                # Add reward
                                add_record('rewards_fines', {
                                    'family_id': int(family_id),
                                    'type': 'reward',
                                    'reason': 'Proper waste segregation',
                                    'amount': 10,  # reward points
                                    'collection_record_id': record['id'],
                                    'created_at': datetime.now().isoformat()
                                })

                            elif collection_record['segregation_quality'] == 'poor':
                                st.warning("⚠️ Poor segregation - Warning issued")
                                # Add warning/fine
                                add_record('rewards_fines', {
                                    'family_id': int(family_id),
                                    'type': 'warning',
                                    'reason': 'Poor waste segregation',
                                    'amount': 0,
                                    'collection_record_id': record['id'],
                                    'created_at': datetime.now().isoformat()
                                })

                            st.rerun()

                        else:
                            st.error("❌ Please fill in all required fields")

            else:
                st.error("❌ Family not found with this ID")

        else:
            st.info("📱 Please scan a QR code or enter Family ID to start collection update")


def collection_records():
    st.subheader("📋 Collection Records")

    records = get_records('collections')

    if not records:
        st.info("📝 No collection records found. Start collecting waste to see records here.")
        return

    # Filters
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        date_filter = st.date_input("Filter by Date", value=date.today())

    with col2:
        collector_filter = st.selectbox("Filter by Collector",
                                        ["All"] + list(set([r.get('collector_name', 'Unknown') for r in records])))

    with col3:
        quality_filter = st.selectbox("Filter by Quality",
                                      ["All", "good", "average", "poor"])

    with col4:
        family_filter = st.text_input("Search Family", placeholder="Family name or ID")

    # Apply filters
    filtered_records = records

    if date_filter:
        filtered_records = [r for r in filtered_records
                            if r.get('collection_date') == str(date_filter)]

    if collector_filter != "All":
        filtered_records = [r for r in filtered_records
                            if r.get('collector_name') == collector_filter]

    if quality_filter != "All":
        filtered_records = [r for r in filtered_records
                            if r.get('segregation_quality') == quality_filter]

    if family_filter:
        filtered_records = [r for r in filtered_records
                            if family_filter.lower() in r.get('family_name', '').lower()
                            or family_filter in str(r.get('family_id', ''))]

    # Statistics
    if filtered_records:
        st.subheader("📊 Collection Statistics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Collections", len(filtered_records))

        with col2:
            good_quality = len([r for r in filtered_records if r.get('segregation_quality') == 'good'])
            st.metric("Good Segregation", good_quality)

        with col3:
            poor_quality = len([r for r in filtered_records if r.get('segregation_quality') == 'poor'])
            st.metric("Poor Segregation", poor_quality)

        with col4:
            avg_quality = len([r for r in filtered_records if r.get('segregation_quality') == 'average'])
            st.metric("Average Segregation", avg_quality)

    # Display records
    for record in filtered_records:
        quality_color = {
            'good': '🟢',
            'average': '🟡',
            'poor': '🔴'
        }.get(record.get('segregation_quality'), '⚪')

        with st.expander(
                f"{quality_color} {record.get('family_name', 'Unknown')} - {record.get('collection_date', 'N/A')} (ID: {record.get('id', 'N/A')})"):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Family ID**: {record.get('family_id', 'N/A')}")
                st.write(f"**Address**: {record.get('address', 'N/A')}")
                st.write(f"**Collection Time**: {record.get('collection_time', 'N/A')}")
                st.write(f"**Collector**: {record.get('collector_name', 'N/A')}")
                st.write(f"**Vehicle**: {record.get('vehicle_number', 'Not specified')}")

            with col2:
                st.write(f"**Waste Types**: {', '.join(record.get('waste_types_collected', []))}")
                st.write(f"**Quality**: {record.get('segregation_quality', 'N/A').title()}")
                st.write(f"**Quantity**: {record.get('quantity_estimate', 'N/A')}")
                st.write(f"**Photos**: {record.get('photos_uploaded', 0)} uploaded")

            # Additional flags
            flags = []
            if record.get('contamination_issues'): flags.append("🚫 Contamination Issues")
            if record.get('special_items'): flags.append("📦 Special Items")
            if record.get('missed_collection'): flags.append("⏰ Previously Missed")
            if record.get('payment_required'): flags.append("💰 Payment Collected")

            if flags:
                st.write("**Flags**: " + " | ".join(flags))

            if record.get('collection_notes'):
                st.write(f"**Notes**: {record.get('collection_notes')}")


def route_management():
    st.subheader("🗺️ Collection Route Management")

    st.info("📍 Route optimization helps waste collectors plan efficient collection paths.")

    # Route planning
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📋 Create Collection Route")

        route_name = st.text_input("Route Name", placeholder="e.g., Sector 1 Morning Route")
        collector_assigned = st.text_input("Assigned Collector", placeholder="Collector name")
        vehicle_assigned = st.text_input("Assigned Vehicle", placeholder="Vehicle number")

        # Get families for route selection
        families = get_records('families', {'status': 'active'})

        if families:
            family_options = [f"{f['family_name']} - {f['address'][:50]}... (ID: {f['id']})"
                              for f in families]

            selected_families = st.multiselect("Select Families for Route", family_options)

            estimated_time = st.number_input("Estimated Collection Time (hours)",
                                             min_value=1.0, max_value=12.0, value=4.0, step=0.5)

            route_notes = st.text_area("Route Notes", placeholder="Special instructions, traffic considerations, etc.")

            if st.button("📍 Create Route"):
                if route_name and collector_assigned and selected_families:
                    # Extract family IDs
                    family_ids = [f.split("ID: ")[1].split(")")[0] for f in selected_families]

                    route_record = {
                        'route_name': route_name,
                        'collector_assigned': collector_assigned,
                        'vehicle_assigned': vehicle_assigned,
                        'family_ids': family_ids,
                        'estimated_time': estimated_time,
                        'route_notes': route_notes,
                        'status': 'planned',
                        'families_count': len(family_ids),
                        'created_at': datetime.now().isoformat()
                    }

                    record = add_record('collection_routes', route_record)
                    st.success(f"✅ Route created successfully! Route ID: {record['id']}")
                else:
                    st.error("❌ Please fill in all required fields")
        else:
            st.warning("⚠️ No active families found for route planning")

    with col2:
        st.subheader("📊 Route Statistics")

        routes = get_records('collection_routes', {})

        if routes:
            st.metric("Total Routes", len(routes))

            planned_routes = len([r for r in routes if r.get('status') == 'planned'])
            st.metric("Planned Routes", planned_routes)

            total_families = sum([r.get('families_count', 0) for r in routes])
            st.metric("Total Families in Routes", total_families)

            # Recent routes
            st.subheader("📋 Recent Routes")
            for route in routes[-5:]:  # Show last 5 routes
                status_icon = "📍" if route.get('status') == 'planned' else "✅"
                st.write(f"{status_icon} **{route.get('route_name')}** - {route.get('families_count', 0)} families")
        else:
            st.info("No routes created yet.")

    # Existing routes management
    st.subheader("🗂️ Manage Existing Routes")

    routes = get_records('collection_routes', {})

    if routes:
        for route in routes:
            with st.expander(
                    f"📍 {route.get('route_name', 'Unnamed Route')} - {route.get('families_count', 0)} families"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Collector**: {route.get('collector_assigned', 'N/A')}")
                    st.write(f"**Vehicle**: {route.get('vehicle_assigned', 'N/A')}")
                    st.write(f"**Families Count**: {route.get('families_count', 0)}")
                    st.write(f"**Estimated Time**: {route.get('estimated_time', 'N/A')} hours")

                with col2:
                    st.write(f"**Status**: {route.get('status', 'Unknown').title()}")
                    st.write(f"**Created**: {route.get('created_at', 'N/A')[:10]}")

                if route.get('route_notes'):
                    st.write(f"**Notes**: {route.get('route_notes')}")

                # Update route status
                new_status = st.selectbox(
                    "Update Status",
                    ["planned", "in_progress", "completed", "cancelled"],
                    key=f"route_status_{route.get('id')}",
                    index=["planned", "in_progress", "completed", "cancelled"].index(route.get('status', 'planned'))
                )

                if st.button(f"Update Route Status", key=f"update_route_{route.get('id')}"):
                    update_record('collection_routes', route.get('id'), {'status': new_status})
                    st.success(f"Route status updated to {new_status}")
                    st.rerun()
    else:
        st.info("📍 No collection routes found. Create routes to manage waste collection efficiently.")
