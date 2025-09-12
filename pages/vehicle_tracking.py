import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import random
import plotly.express as px
import plotly.graph_objects as go
from utils.database import add_record, get_records, update_record


def show():
    st.title("🚛 Vehicle Tracking System")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Real-time Tracking", "Vehicle Management", "Route History", "Performance Analytics"])

    with tab1:
        realtime_tracking()

    with tab2:
        vehicle_management()

    with tab3:
        route_history()

    with tab4:
        performance_analytics()


def realtime_tracking():
    st.subheader("📍 Real-time Vehicle Tracking")

    # Get active vehicles
    vehicles = get_records('vehicles', {'status': 'active'})

    if not vehicles:
        st.warning("🚛 No active vehicles found. Add vehicles in the Vehicle Management tab.")
        return

    # Vehicle selection for tracking
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("🚛 Select Vehicle")

        vehicle_options = [f"{v['vehicle_number']} - {v['vehicle_type']}" for v in vehicles]
        selected_vehicle = st.selectbox("Choose Vehicle", vehicle_options)

        if selected_vehicle:
            vehicle_number = selected_vehicle.split(" - ")[0]
            vehicle = next(v for v in vehicles if v['vehicle_number'] == vehicle_number)

            # Vehicle status display
            st.info(f"**Vehicle**: {vehicle['vehicle_number']}")
            st.info(f"**Driver**: {vehicle.get('driver_name', 'Not assigned')}")
            st.info(f"**Route**: {vehicle.get('current_route', 'Not assigned')}")

            # Current status
            status_options = ["On Route", "At Collection Point", "Heading to Treatment Plant",
                              "At Treatment Plant", "Returning to Base", "Break", "Maintenance"]

            current_status = st.selectbox("Update Status",
                                          status_options,
                                          index=status_options.index(vehicle.get('current_status', 'On Route')))

            if st.button("📍 Update Vehicle Status"):
                update_record('vehicles', vehicle['id'], {
                    'current_status': current_status,
                    'last_update': datetime.now().isoformat()
                })
                st.success("Status updated!")
                st.rerun()

            # GPS coordinates simulation
            st.subheader("🗺️ GPS Location")

            # Simulate GPS coordinates (in real app, these would come from GPS tracker)
            base_lat = 12.9716  # Bangalore coordinates
            base_lng = 77.5946

            # Add some random variation for simulation
            current_lat = base_lat + random.uniform(-0.1, 0.1)
            current_lng = base_lng + random.uniform(-0.1, 0.1)

            st.write(f"**Latitude**: {current_lat:.6f}")
            st.write(f"**Longitude**: {current_lng:.6f}")
            st.write(f"**Last Update**: {datetime.now().strftime('%H:%M:%S')}")

            # Speed and other metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Speed", f"{random.randint(15, 45)} km/h")
            with col2:
                st.metric("Fuel Level", f"{random.randint(20, 80)}%")
            with col3:
                st.metric("Collections Today", f"{random.randint(15, 50)}")

    with col2:
        st.subheader("🗺️ Live Map")

        # In a real application, this would show an actual map with vehicle locations
        # For now, we'll simulate with location data

        try:
            import streamlit_folium as st_folium
            import folium

            # Create a map centered on the city
            m = folium.Map(location=[12.9716, 77.5946], zoom_start=12)

            # Add markers for each active vehicle
            colors = ['red', 'blue', 'green', 'purple', 'orange']
            for i, vehicle in enumerate(vehicles[:5]):  # Show up to 5 vehicles
                # Simulate different locations for each vehicle
                lat = 12.9716 + random.uniform(-0.05, 0.05)
                lng = 77.5946 + random.uniform(-0.05, 0.05)

                folium.Marker(
                    location=[lat, lng],
                    popup=f"{vehicle['vehicle_number']}\n{vehicle.get('current_status', 'On Route')}",
                    tooltip=vehicle['vehicle_number'],
                    icon=folium.Icon(color=colors[i % len(colors)], icon='truck', prefix='fa')
                ).add_to(m)

            # Display the map
            st_folium.st_folium(m, width=700, height=500)

        except ImportError:
            # Fallback if folium is not available
            st.info("🗺️ Map visualization requires streamlit-folium package. Showing coordinates instead.")

            # Show vehicle locations in a table
            location_data = []
            for vehicle in vehicles:
                lat = 12.9716 + random.uniform(-0.05, 0.05)
                lng = 77.5946 + random.uniform(-0.05, 0.05)

                location_data.append({
                    'Vehicle': vehicle['vehicle_number'],
                    'Status': vehicle.get('current_status', 'On Route'),
                    'Latitude': f"{lat:.6f}",
                    'Longitude': f"{lng:.6f}",
                    'Driver': vehicle.get('driver_name', 'Not assigned')
                })

            if location_data:
                df = pd.DataFrame(location_data)
                st.dataframe(df, use_container_width=True)

    # Alert system
    st.subheader("🚨 Vehicle Alerts")

    alerts = [
        {"vehicle": "WM-001", "type": "Maintenance Due", "priority": "Medium", "time": "2 hours ago"},
        {"vehicle": "WM-003", "type": "Route Delay", "priority": "High", "time": "15 minutes ago"},
        {"vehicle": "WM-002", "type": "Low Fuel", "priority": "Medium", "time": "1 hour ago"},
    ]

    for alert in alerts:
        priority_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
        st.warning(f"{priority_color[alert['priority']]} **{alert['vehicle']}** - {alert['type']} ({alert['time']})")


def vehicle_management():
    st.subheader("🚛 Vehicle Fleet Management")

    tab1, tab2 = st.tabs(["Add Vehicle", "Manage Fleet"])

    with tab1:
        st.subheader("➕ Add New Vehicle")

        with st.form("add_vehicle"):
            col1, col2 = st.columns(2)

            with col1:
                vehicle_number = st.text_input("Vehicle Number*", placeholder="e.g., WM-001")
                vehicle_type = st.selectbox("Vehicle Type*",
                                            ["Small Truck", "Medium Truck", "Large Truck",
                                             "Compactor", "Tipper", "Mini Van"])
                capacity = st.number_input("Capacity (kg)", min_value=100, max_value=10000, value=1000)
                fuel_type = st.selectbox("Fuel Type", ["Diesel", "Petrol", "CNG", "Electric"])

            with col2:
                driver_name = st.text_input("Assigned Driver", placeholder="Driver name")
                driver_contact = st.text_input("Driver Contact", placeholder="Driver mobile number")
                registration_number = st.text_input("Registration Number*", placeholder="Vehicle registration")
                insurance_expiry = st.date_input("Insurance Expiry Date",
                                                 value=date.today() + timedelta(days=365))

            # Vehicle specifications
            col1, col2 = st.columns(2)
            with col1:
                manufacture_year = st.number_input("Manufacture Year",
                                                   min_value=2000, max_value=datetime.now().year, value=2020)
                last_service_date = st.date_input("Last Service Date", value=date.today() - timedelta(days=30))

            with col2:
                next_service_date = st.date_input("Next Service Due",
                                                  value=date.today() + timedelta(days=90))
                gps_device_id = st.text_input("GPS Device ID", placeholder="GPS tracker device ID")

            # Operational details
            operating_hours = st.selectbox("Operating Hours",
                                           ["6 AM - 2 PM", "2 PM - 10 PM", "6 AM - 6 PM", "24 Hours"])
            base_location = st.text_input("Base Location", placeholder="Vehicle parking/base location")

            notes = st.text_area("Additional Notes", placeholder="Any special notes about the vehicle")

            submitted = st.form_submit_button("🚛 Add Vehicle")

            if submitted:
                if vehicle_number and vehicle_type and registration_number:
                    vehicle_record = {
                        'vehicle_number': vehicle_number,
                        'vehicle_type': vehicle_type,
                        'capacity': capacity,
                        'fuel_type': fuel_type,
                        'driver_name': driver_name,
                        'driver_contact': driver_contact,
                        'registration_number': registration_number,
                        'insurance_expiry': str(insurance_expiry),
                        'manufacture_year': manufacture_year,
                        'last_service_date': str(last_service_date),
                        'next_service_date': str(next_service_date),
                        'gps_device_id': gps_device_id,
                        'operating_hours': operating_hours,
                        'base_location': base_location,
                        'notes': notes,
                        'status': 'active',
                        'current_status': 'At Base',
                        'total_collections': 0,
                        'total_distance': 0.0,
                        'created_at': datetime.now().isoformat()
                    }

                    record = add_record('vehicles', vehicle_record)
                    st.success(f"✅ Vehicle added successfully! Vehicle ID: {record['id']}")
                    st.rerun()

                else:
                    st.error("❌ Please fill in all required fields")

    with tab2:
        st.subheader("🚛 Fleet Management")

        vehicles = get_records('vehicles')

        if not vehicles:
            st.info("🚛 No vehicles registered. Add vehicles using the form above.")
            return

        # Fleet statistics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Vehicles", len(vehicles))

        with col2:
            active_vehicles = len([v for v in vehicles if v.get('status') == 'active'])
            st.metric("Active Vehicles", active_vehicles)

        with col3:
            total_capacity = sum([v.get('capacity', 0) for v in vehicles])
            st.metric("Total Capacity", f"{total_capacity} kg")

        with col4:
            maintenance_due = len([v for v in vehicles
                                   if datetime.strptime(v.get('next_service_date', '2099-12-31'),
                                                        '%Y-%m-%d').date() <= date.today() + timedelta(days=30)])
            st.metric("Maintenance Due", maintenance_due)

        # Vehicle list
        for vehicle in vehicles:
            status_icon = "✅" if vehicle.get('status') == 'active' else "❌"

            with st.expander(
                    f"{status_icon} {vehicle.get('vehicle_number', 'Unknown')} - {vehicle.get('vehicle_type', 'N/A')}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Registration**: {vehicle.get('registration_number', 'N/A')}")
                    st.write(f"**Capacity**: {vehicle.get('capacity', 0)} kg")
                    st.write(f"**Fuel Type**: {vehicle.get('fuel_type', 'N/A')}")
                    st.write(f"**Driver**: {vehicle.get('driver_name', 'Not assigned')}")
                    st.write(f"**Driver Contact**: {vehicle.get('driver_contact', 'N/A')}")

                with col2:
                    st.write(f"**Current Status**: {vehicle.get('current_status', 'Unknown')}")
                    st.write(f"**Operating Hours**: {vehicle.get('operating_hours', 'N/A')}")
                    st.write(f"**Next Service**: {vehicle.get('next_service_date', 'N/A')}")
                    st.write(f"**Total Collections**: {vehicle.get('total_collections', 0)}")
                    st.write(f"**GPS Device**: {vehicle.get('gps_device_id', 'Not installed')}")

                if vehicle.get('notes'):
                    st.write(f"**Notes**: {vehicle.get('notes')}")

                # Update vehicle status
                col1, col2 = st.columns(2)

                with col1:
                    new_status = st.selectbox(
                        "Update Status",
                        ["active", "inactive", "maintenance", "repair"],
                        key=f"vehicle_status_{vehicle.get('id')}",
                        index=["active", "inactive", "maintenance", "repair"].index(vehicle.get('status', 'active'))
                    )

                with col2:
                    if st.button(f"Update Status", key=f"update_vehicle_{vehicle.get('id')}"):
                        update_record('vehicles', vehicle.get('id'), {'status': new_status})
                        st.success(f"Vehicle status updated to {new_status}")
                        st.rerun()


def route_history():
    st.subheader("📊 Route History & Analytics")

    # Generate sample route history
    vehicles = get_records('vehicles')

    if not vehicles:
        st.info("🚛 No vehicles found. Add vehicles first.")
        return

    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=date.today() - timedelta(days=7))
    with col2:
        end_date = st.date_input("End Date", value=date.today())

    # Vehicle selector
    vehicle_options = [f"{v['vehicle_number']}" for v in vehicles]
    vehicle_options.insert(0, "All Vehicles")
    selected_vehicle = st.selectbox("Select Vehicle", vehicle_options)

    # Generate sample route data
    route_data = []
    for i in range((end_date - start_date).days + 1):
        current_date = start_date + timedelta(days=i)

        for vehicle in vehicles:
            if selected_vehicle == "All Vehicles" or selected_vehicle == vehicle['vehicle_number']:
                # Simulate daily route data
                collections = random.randint(10, 50)
                distance = random.uniform(50, 150)
                fuel_used = random.uniform(10, 30)

                route_data.append({
                    'Date': current_date,
                    'Vehicle': vehicle['vehicle_number'],
                    'Collections': collections,
                    'Distance (km)': round(distance, 2),
                    'Fuel Used (L)': round(fuel_used, 2),
                    'Efficiency': round(collections / fuel_used, 2)
                })

    if route_data:
        df = pd.DataFrame(route_data)

        # Summary statistics
        st.subheader("📊 Summary Statistics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Collections", df['Collections'].sum())

        with col2:
            st.metric("Total Distance", f"{df['Distance (km)'].sum():.2f} km")

        with col3:
            st.metric("Total Fuel Used", f"{df['Fuel Used (L)'].sum():.2f} L")

        with col4:
            st.metric("Avg Efficiency", f"{df['Efficiency'].mean():.2f} collections/L")

        # Charts
        st.subheader("📈 Performance Charts")

        col1, col2 = st.columns(2)

        with col1:
            # Daily collections chart
            fig_collections = px.line(df, x='Date', y='Collections',
                                      color='Vehicle' if selected_vehicle == "All Vehicles" else None,
                                      title='Daily Collections')
            st.plotly_chart(fig_collections, use_container_width=True)

        with col2:
            # Fuel efficiency chart
            fig_efficiency = px.line(df, x='Date', y='Efficiency',
                                     color='Vehicle' if selected_vehicle == "All Vehicles" else None,
                                     title='Fuel Efficiency (Collections per Liter)')
            st.plotly_chart(fig_efficiency, use_container_width=True)

        # Detailed data table
        st.subheader("📋 Detailed Route Data")
        st.dataframe(df.sort_values('Date', ascending=False), use_container_width=True)

        # Export option
        if st.button("📥 Export Route Data"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"route_history_{start_date}_to_{end_date}.csv",
                mime="text/csv"
            )

    else:
        st.info("No route data available for the selected criteria.")


def performance_analytics():
    st.subheader("📊 Vehicle Performance Analytics")

    vehicles = get_records('vehicles')

    if not vehicles:
        st.info("🚛 No vehicles found for analytics.")
        return

    # Performance metrics
    st.subheader("🎯 Key Performance Indicators")

    col1, col2 = st.columns(2)

    with col1:
        # Vehicle utilization chart
        utilization_data = []
        for vehicle in vehicles:
            # Simulate utilization data
            utilization = random.uniform(0.6, 0.95)
            utilization_data.append({
                'Vehicle': vehicle['vehicle_number'],
                'Utilization': utilization * 100
            })

        df_util = pd.DataFrame(utilization_data)
        fig_util = px.bar(df_util, x='Vehicle', y='Utilization',
                          title='Vehicle Utilization (%)',
                          color='Utilization',
                          color_continuous_scale='RdYlGn')
        st.plotly_chart(fig_util, use_container_width=True)

    with col2:
        # Maintenance cost chart
        maintenance_data = []
        for vehicle in vehicles:
            # Simulate maintenance costs
            cost = random.uniform(5000, 25000)
            maintenance_data.append({
                'Vehicle': vehicle['vehicle_number'],
                'Maintenance Cost': cost
            })

        df_maint = pd.DataFrame(maintenance_data)
        fig_maint = px.bar(df_maint, x='Vehicle', y='Maintenance Cost',
                           title='Monthly Maintenance Cost (₹)',
                           color='Maintenance Cost',
                           color_continuous_scale='Reds')
        st.plotly_chart(fig_maint, use_container_width=True)

    # Performance comparison table
    st.subheader("📊 Vehicle Performance Comparison")

    performance_data = []
    for vehicle in vehicles:
        # Simulate performance metrics
        performance_data.append({
            'Vehicle': vehicle['vehicle_number'],
            'Type': vehicle.get('vehicle_type', 'N/A'),
            'Capacity (kg)': vehicle.get('capacity', 0),
            'Daily Collections': random.randint(20, 60),
            'Fuel Efficiency (km/L)': round(random.uniform(6, 15), 2),
            'Uptime (%)': round(random.uniform(85, 98), 1),
            'Maintenance Score': random.randint(7, 10),
            'Driver Rating': round(random.uniform(4.0, 5.0), 1)
        })

    df_performance = pd.DataFrame(performance_data)

    # Color-code the performance table
    def highlight_performance(val):
        if isinstance(val, (int, float)):
            if val >= 90:  # High performance
                return 'background-color: lightgreen'
            elif val >= 70:  # Medium performance
                return 'background-color: lightyellow'
            else:  # Low performance
                return 'background-color: lightcoral'
        return ''

    styled_df = df_performance.style.applymap(highlight_performance, subset=['Uptime (%)', 'Maintenance Score'])
    st.dataframe(styled_df, use_container_width=True)

    # Fleet health overview
    st.subheader("🏥 Fleet Health Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Vehicles by status
        status_counts = {}
        for vehicle in vehicles:
            status = vehicle.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1

        fig_status = px.pie(values=list(status_counts.values()),
                            names=list(status_counts.keys()),
                            title='Fleet Status Distribution')
        st.plotly_chart(fig_status, use_container_width=True)

    with col2:
        # Maintenance schedule
        maintenance_due = []
        for vehicle in vehicles:
            next_service = datetime.strptime(vehicle.get('next_service_date', '2099-12-31'), '%Y-%m-%d').date()
            days_until = (next_service - date.today()).days

            if days_until <= 30:
                status = "Due Soon"
            elif days_until <= 7:
                status = "Overdue"
            else:
                status = "Scheduled"

            maintenance_due.append({'Status': status})

        df_maint_status = pd.DataFrame(maintenance_due)
        if not df_maint_status.empty:
            maintenance_counts = df_maint_status['Status'].value_counts()
            fig_maint_status = px.pie(values=maintenance_counts.values,
                                      names=maintenance_counts.index,
                                      title='Maintenance Schedule Status')
            st.plotly_chart(fig_maint_status, use_container_width=True)

    with col3:
        # Fuel type distribution
        fuel_counts = {}
        for vehicle in vehicles:
            fuel = vehicle.get('fuel_type', 'Unknown')
            fuel_counts[fuel] = fuel_counts.get(fuel, 0) + 1

        fig_fuel = px.pie(values=list(fuel_counts.values()),
                          names=list(fuel_counts.keys()),
                          title='Fleet Fuel Type Distribution')
        st.plotly_chart(fig_fuel, use_container_width=True)

    # Recommendations
    st.subheader("💡 Fleet Management Recommendations")

    recommendations = [
        "🔧 Schedule maintenance for vehicles with uptime below 90%",
        "⛽ Consider fuel efficiency training for drivers with low km/L ratings",
        "📊 Monitor high-maintenance cost vehicles for potential replacement",
        "🚛 Optimize routes for underutilized vehicles",
        "🔋 Consider electric vehicles for short-distance routes to reduce fuel costs"
    ]

    for rec in recommendations:
        st.info(rec)
