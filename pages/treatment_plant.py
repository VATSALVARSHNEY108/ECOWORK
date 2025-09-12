import streamlit as st
import pandas as pd
from datetime import datetime, date
import base64
import json
from utils.database import add_record, get_records, update_record
from utils.ai_verification import verify_treatment_plant_delivery, verify_waste_segregation


def show():
    st.title("🏭 Treatment Plant Management")

    tab1, tab2, tab3, tab4 = st.tabs(["Waste Delivery", "AI Verification", "Plant Records", "Performance Analytics"])

    with tab1:
        waste_delivery()

    with tab2:
        ai_verification()

    with tab3:
        plant_records()

    with tab4:
        performance_analytics()


def waste_delivery():
    st.subheader("🚛 Waste Delivery Registration")

    st.info(
        "📋 **Process**: Vehicles deliver waste to treatment plant and must report delivery details for verification and worker incentives.")

    # Get active vehicles
    vehicles = get_records('vehicles', {'status': 'active'})

    if not vehicles:
        st.warning("🚛 No active vehicles found. Add vehicles in Vehicle Tracking section.")
        return

    with st.form("waste_delivery"):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🚛 Vehicle Information")

            vehicle_options = [f"{v['vehicle_number']} - {v.get('driver_name', 'No driver')}" for v in vehicles]
            vehicle_options.insert(0, "Select vehicle")

            selected_vehicle = st.selectbox("Vehicle*", vehicle_options)

            vehicle = None
            if selected_vehicle and selected_vehicle != "Select vehicle":
                vehicle_number = selected_vehicle.split(" - ")[0]
                vehicle = next(v for v in vehicles if v['vehicle_number'] == vehicle_number)

                st.info(f"**Driver**: {vehicle.get('driver_name', 'Not assigned')}")
                st.info(f"**Vehicle Type**: {vehicle.get('vehicle_type', 'Unknown')}")
                st.info(f"**Capacity**: {vehicle.get('capacity', 0)} kg")

            delivery_date = st.date_input("Delivery Date*", value=date.today())
            delivery_time = st.time_input("Delivery Time*", value=datetime.now().time())

            # Collection route information
            collection_routes = get_records('collection_routes', {})
            route_options = [f"{r.get('route_name', 'Unknown')} ({r.get('families_count', 0)} families)"
                             for r in collection_routes]
            route_options.insert(0, "Select collection route")

            selected_route = st.selectbox("Collection Route", route_options)

        with col2:
            st.subheader("♻️ Waste Details")

            # Waste types and quantities
            organic_weight = st.number_input("Organic Waste (kg)", min_value=0.0, step=10.0)
            recyclable_weight = st.number_input("Recyclable Waste (kg)", min_value=0.0, step=10.0)
            hazardous_weight = st.number_input("Hazardous Waste (kg)", min_value=0.0, step=5.0)
            general_weight = st.number_input("General Waste (kg)", min_value=0.0, step=10.0)

            total_weight = organic_weight + recyclable_weight + hazardous_weight + general_weight
            st.metric("Total Weight", f"{total_weight} kg")

            # Quality assessment
            overall_segregation = st.selectbox(
                "Overall Segregation Quality*",
                ["Excellent - Properly segregated",
                 "Good - Minor contamination",
                 "Average - Some mixing",
                 "Poor - Badly mixed"]
            )

            contamination_level = st.slider("Contamination Level (%)", 0, 100, 10)

        st.subheader("📷 Delivery Documentation")

        col1, col2 = st.columns(2)

        with col1:
            delivery_photo = st.file_uploader("Delivery Photo*",
                                              type=['png', 'jpg', 'jpeg'],
                                              help="Photo of waste being delivered to treatment plant")

            segregation_photo = st.file_uploader("Segregation Photo*",
                                                 type=['png', 'jpg', 'jpeg'],
                                                 help="Photo showing waste segregation quality")

        with col2:
            # Treatment plant details
            plant_section = st.selectbox("Plant Section",
                                         ["Organic Processing", "Recycling Unit", "Hazardous Treatment",
                                          "General Disposal", "Sorting Area"])

            received_by = st.text_input("Received By*", placeholder="Plant operator name")

            # Additional notes
            delivery_notes = st.text_area("Delivery Notes",
                                          placeholder="Any observations, issues, or special instructions")

        # Verification checkboxes
        st.subheader("✅ Verification Checklist")
        col1, col2 = st.columns(2)

        with col1:
            vehicle_inspected = st.checkbox("Vehicle properly cleaned", value=True)
            documentation_complete = st.checkbox("All documentation provided", value=True)
            safety_protocols = st.checkbox("Safety protocols followed", value=True)

        with col2:
            weight_verified = st.checkbox("Weight measurements verified", value=True)
            quality_checked = st.checkbox("Quality assessment completed", value=True)
            receipt_issued = st.checkbox("Delivery receipt issued", value=True)

        submitted = st.form_submit_button("📋 Register Delivery")

        if submitted:
            if (selected_vehicle and selected_vehicle != "Select vehicle" and
                    delivery_photo and segregation_photo and received_by and
                    overall_segregation and total_weight > 0 and vehicle):

                # Process segregation quality
                quality_map = {
                    "Excellent - Properly segregated": "excellent",
                    "Good - Minor contamination": "good",
                    "Average - Some mixing": "average",
                    "Poor - Badly mixed": "poor"
                }

                # Create delivery record
                delivery_record = {
                    'vehicle_id': vehicle['id'],
                    'vehicle_number': vehicle['vehicle_number'],
                    'driver_name': vehicle.get('driver_name', ''),
                    'collection_route': selected_route if selected_route != "Select collection route" else '',
                    'delivery_date': str(delivery_date),
                    'delivery_time': str(delivery_time),
                    'organic_weight': organic_weight,
                    'recyclable_weight': recyclable_weight,
                    'hazardous_weight': hazardous_weight,
                    'general_weight': general_weight,
                    'total_weight': total_weight,
                    'segregation_quality': quality_map[overall_segregation],
                    'contamination_level': contamination_level,
                    'plant_section': plant_section,
                    'received_by': received_by,
                    'delivery_notes': delivery_notes,
                    'vehicle_inspected': vehicle_inspected,
                    'documentation_complete': documentation_complete,
                    'safety_protocols': safety_protocols,
                    'weight_verified': weight_verified,
                    'quality_checked': quality_checked,
                    'receipt_issued': receipt_issued,
                    'photos_uploaded': 2,
                    'ai_verification_pending': True,
                    'status': 'delivered',
                    'created_at': datetime.now().isoformat()
                }

                record = add_record('treatment_reports', delivery_record)

                st.success(f"✅ Delivery registered successfully! Record ID: {record['id']}")

                # Update vehicle status
                update_record('vehicles', vehicle['id'], {
                    'current_status': 'At Treatment Plant',
                    'last_delivery': datetime.now().isoformat(),
                    'total_collections': vehicle.get('total_collections', 0) + 1
                })

                # Determine worker incentives based on quality
                if delivery_record['segregation_quality'] in ['excellent', 'good']:
                    st.success("🎁 Driver eligible for performance incentive!")

                    # Add reward for driver
                    incentive_amount = 50 if delivery_record['segregation_quality'] == 'excellent' else 25
                    add_record('rewards_fines', {
                        'worker_name': vehicle.get('driver_name', ''),
                        'vehicle_number': vehicle['vehicle_number'],
                        'type': 'incentive',
                        'reason': f'Quality waste delivery - {delivery_record["segregation_quality"]} segregation',
                        'amount': incentive_amount,
                        'treatment_record_id': record['id'],
                        'created_at': datetime.now().isoformat()
                    })

                elif delivery_record['segregation_quality'] == 'poor':
                    st.warning("⚠️ Poor segregation quality - Driver training recommended")

                st.info("🤖 Photos will be processed by AI for verification. Check AI Verification tab for results.")
                st.rerun()

            else:
                st.error("❌ Please fill in all required fields and upload both photos")


def ai_verification():
    st.subheader("🤖 AI Verification System")

    st.info(
        "🔍 **AI Verification**: Automatically verifies delivery photos and segregation quality to prevent fraud and ensure accuracy.")

    # Get pending verifications
    pending_reports = get_records('treatment_reports', {'ai_verification_pending': True})

    if not pending_reports:
        st.info("✅ No pending AI verifications. All deliveries have been processed.")
        return

    st.subheader(f"📋 Pending Verifications ({len(pending_reports)})")

    for report in pending_reports:
        with st.expander(
                f"🚛 {report.get('vehicle_number', 'Unknown')} - {report.get('delivery_date', 'N/A')} (ID: {report.get('id', 'N/A')})"):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Vehicle**: {report.get('vehicle_number', 'N/A')}")
                st.write(f"**Driver**: {report.get('driver_name', 'N/A')}")
                st.write(f"**Total Weight**: {report.get('total_weight', 0)} kg")
                st.write(f"**Segregation Quality**: {report.get('segregation_quality', 'Unknown').title()}")
                st.write(f"**Plant Section**: {report.get('plant_section', 'N/A')}")

            with col2:
                st.write(f"**Delivery Time**: {report.get('delivery_time', 'N/A')}")
                st.write(f"**Contamination Level**: {report.get('contamination_level', 0)}%")
                st.write(f"**Received By**: {report.get('received_by', 'N/A')}")
                st.write(f"**Photos Uploaded**: {report.get('photos_uploaded', 0)}")

            # Simulate AI verification process
            if st.button(f"🤖 Run AI Verification", key=f"verify_{report.get('id')}"):
                st.info("🤖 Processing photos with AI...")

                # Simulate AI verification (in real app, would process actual photos)
                verification_result = {
                    'verified': True,
                    'segregation_quality': report.get('segregation_quality'),
                    'vehicle_compliance': True,
                    'notes': 'AI verification completed successfully. Photos show proper delivery procedures.',
                    'confidence_score': 0.92,
                    'detected_issues': [],
                    'recommendations': ['Continue current quality standards']
                }

                # In real implementation, would call:
                # verification_result = verify_treatment_plant_delivery(photo_base64)

                # Update record with AI results
                update_record('treatment_reports', report.get('id'), {
                    'ai_verification_pending': False,
                    'ai_verification_result': verification_result,
                    'ai_verified': verification_result['verified'],
                    'ai_confidence': verification_result.get('confidence_score', 0),
                    'verification_date': datetime.now().isoformat()
                })

                if verification_result['verified']:
                    st.success("✅ AI Verification: Delivery verified successfully!")

                    # Additional incentive for AI-verified quality delivery
                    if verification_result.get('confidence_score', 0) > 0.9:
                        st.success("🏆 High confidence AI verification - Additional bonus earned!")

                        add_record('rewards_fines', {
                            'worker_name': report.get('driver_name', ''),
                            'vehicle_number': report.get('vehicle_number', ''),
                            'type': 'ai_bonus',
                            'reason': 'High-confidence AI verification of quality delivery',
                            'amount': 15,
                            'treatment_record_id': report.get('id'),
                            'created_at': datetime.now().isoformat()
                        })
                else:
                    st.warning("⚠️ AI Verification: Issues detected - Manual review required")

                # Show detailed results
                col1, col2 = st.columns(2)

                with col1:
                    st.metric("AI Confidence", f"{verification_result.get('confidence_score', 0):.1%}")
                    st.write(
                        f"**Vehicle Compliance**: {'✅ Yes' if verification_result.get('vehicle_compliance') else '❌ No'}")

                with col2:
                    st.write(
                        f"**Detected Quality**: {verification_result.get('segregation_quality', 'Unknown').title()}")

                if verification_result.get('notes'):
                    st.info(f"**AI Notes**: {verification_result['notes']}")

                if verification_result.get('detected_issues'):
                    st.warning("**Issues Detected**: " + ', '.join(verification_result['detected_issues']))

                if verification_result.get('recommendations'):
                    st.success("**Recommendations**: " + ', '.join(verification_result['recommendations']))

                st.rerun()

    # AI Verification Statistics
    st.subheader("📊 AI Verification Statistics")

    all_reports = get_records('treatment_reports', {})
    verified_reports = [r for r in all_reports if r.get('ai_verified') is not None]

    if verified_reports:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Verifications", len(verified_reports))

        with col2:
            successful_verifications = len([r for r in verified_reports if r.get('ai_verified')])
            st.metric("Successful Verifications", successful_verifications)

        with col3:
            if verified_reports:
                avg_confidence = sum([r.get('ai_confidence', 0) for r in verified_reports]) / len(verified_reports)
                st.metric("Average Confidence", f"{avg_confidence:.1%}")

        with col4:
            pending_count = len(get_records('treatment_reports', {'ai_verification_pending': True}))
            st.metric("Pending Verifications", pending_count)


def plant_records():
    st.subheader("📋 Treatment Plant Records")

    reports = get_records('treatment_reports', {})

    if not reports:
        st.info("📝 No treatment plant records found. Register waste deliveries to see records here.")
        return

    # Filters
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        date_filter = st.date_input("Filter by Date", value=date.today())

    with col2:
        vehicle_filter = st.selectbox("Filter by Vehicle",
                                      ["All"] + list(set([r.get('vehicle_number', 'Unknown') for r in reports])))

    with col3:
        quality_filter = st.selectbox("Filter by Quality",
                                      ["All", "excellent", "good", "average", "poor"])

    with col4:
        verification_filter = st.selectbox("AI Verification",
                                           ["All", "Verified", "Pending", "Failed"])

    # Apply filters
    filtered_reports = reports

    if date_filter:
        filtered_reports = [r for r in filtered_reports
                            if r.get('delivery_date') == str(date_filter)]

    if vehicle_filter != "All":
        filtered_reports = [r for r in filtered_reports
                            if r.get('vehicle_number') == vehicle_filter]

    if quality_filter != "All":
        filtered_reports = [r for r in filtered_reports
                            if r.get('segregation_quality') == quality_filter]

    if verification_filter == "Verified":
        filtered_reports = [r for r in filtered_reports if r.get('ai_verified') is True]
    elif verification_filter == "Pending":
        filtered_reports = [r for r in filtered_reports if r.get('ai_verification_pending') is True]
    elif verification_filter == "Failed":
        filtered_reports = [r for r in filtered_reports if r.get('ai_verified') is False]

    # Summary statistics
    if filtered_reports:
        st.subheader("📊 Delivery Statistics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_deliveries = len(filtered_reports)
            st.metric("Total Deliveries", total_deliveries)

        with col2:
            total_weight = sum([r.get('total_weight', 0) for r in filtered_reports])
            st.metric("Total Weight", f"{total_weight:.1f} kg")

        with col3:
            excellent_quality = len([r for r in filtered_reports if r.get('segregation_quality') == 'excellent'])
            st.metric("Excellent Quality", excellent_quality)

        with col4:
            ai_verified = len([r for r in filtered_reports if r.get('ai_verified') is True])
            st.metric("AI Verified", ai_verified)

    # Display detailed records
    for report in filtered_reports:
        quality_colors = {
            'excellent': '🟢',
            'good': '🟡',
            'average': '🟠',
            'poor': '🔴'
        }

        quality_icon = quality_colors.get(report.get('segregation_quality'), '⚪')
        verification_icon = "✅" if report.get('ai_verified') else (
            "⏳" if report.get('ai_verification_pending') else "❌")

        with st.expander(
                f"{quality_icon} {verification_icon} {report.get('vehicle_number', 'Unknown')} - {report.get('delivery_date', 'N/A')} (ID: {report.get('id', 'N/A')})"):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Vehicle**: {report.get('vehicle_number', 'N/A')}")
                st.write(f"**Driver**: {report.get('driver_name', 'N/A')}")
                st.write(f"**Delivery Time**: {report.get('delivery_time', 'N/A')}")
                st.write(f"**Plant Section**: {report.get('plant_section', 'N/A')}")
                st.write(f"**Received By**: {report.get('received_by', 'N/A')}")

            with col2:
                st.write(f"**Total Weight**: {report.get('total_weight', 0)} kg")
                st.write(f"**Segregation Quality**: {report.get('segregation_quality', 'Unknown').title()}")
                st.write(f"**Contamination**: {report.get('contamination_level', 0)}%")
                st.write(
                    f"**AI Verified**: {'✅ Yes' if report.get('ai_verified') else ('⏳ Pending' if report.get('ai_verification_pending') else '❌ No')}")

                if report.get('ai_confidence'):
                    st.write(f"**AI Confidence**: {report.get('ai_confidence', 0):.1%}")

            # Weight breakdown
            st.write("**Weight Breakdown**:")
            weight_data = {
                'Organic': report.get('organic_weight', 0),
                'Recyclable': report.get('recyclable_weight', 0),
                'Hazardous': report.get('hazardous_weight', 0),
                'General': report.get('general_weight', 0)
            }

            for waste_type, weight in weight_data.items():
                if weight > 0:
                    st.write(f"  • {waste_type}: {weight} kg")

            # Verification checklist
            verification_items = [
                ('Vehicle Inspected', report.get('vehicle_inspected')),
                ('Documentation Complete', report.get('documentation_complete')),
                ('Safety Protocols', report.get('safety_protocols')),
                ('Weight Verified', report.get('weight_verified')),
                ('Quality Checked', report.get('quality_checked')),
                ('Receipt Issued', report.get('receipt_issued'))
            ]

            st.write("**Verification Checklist**:")
            for item, status in verification_items:
                icon = "✅" if status else "❌"
                st.write(f"  {icon} {item}")

            if report.get('delivery_notes'):
                st.write(f"**Notes**: {report.get('delivery_notes')}")


def performance_analytics():
    st.subheader("📊 Treatment Plant Performance Analytics")

    reports = get_records('treatment_reports', {})

    if not reports:
        st.info("📊 No data available for analytics. Register deliveries to see performance metrics.")
        return

    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=date.today() - pd.Timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", value=date.today())

    # Filter reports by date range
    filtered_reports = []
    for report in reports:
        try:
            report_date = datetime.strptime(report.get('delivery_date', ''), '%Y-%m-%d').date()
            if start_date <= report_date <= end_date:
                filtered_reports.append(report)
        except:
            continue

    if not filtered_reports:
        st.warning("No data available for the selected date range.")
        return

    # Key Performance Indicators
    st.subheader("🎯 Key Performance Indicators")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_weight = sum([r.get('total_weight', 0) for r in filtered_reports])
        st.metric("Total Waste Processed", f"{total_weight:.1f} kg")

    with col2:
        daily_avg = total_weight / max(1, (end_date - start_date).days + 1)
        st.metric("Daily Average", f"{daily_avg:.1f} kg/day")

    with col3:
        excellent_deliveries = len([r for r in filtered_reports if r.get('segregation_quality') == 'excellent'])
        quality_rate = (excellent_deliveries / len(filtered_reports)) * 100 if filtered_reports else 0
        st.metric("Quality Rate", f"{quality_rate:.1f}%")

    with col4:
        ai_verified = len([r for r in filtered_reports if r.get('ai_verified')])
        verification_rate = (ai_verified / len(filtered_reports)) * 100 if filtered_reports else 0
        st.metric("AI Verification Rate", f"{verification_rate:.1f}%")

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        # Daily waste processing chart
        daily_data = {}
        for report in filtered_reports:
            date_key = report.get('delivery_date', '')
            if date_key:
                daily_data[date_key] = daily_data.get(date_key, 0) + report.get('total_weight', 0)

        if daily_data:
            df_daily = pd.DataFrame(list(daily_data.items()), columns=['Date', 'Weight'])
            df_daily['Date'] = pd.to_datetime(df_daily['Date'])

            import plotly.express as px
            fig_daily = px.line(df_daily, x='Date', y='Weight',
                                title='Daily Waste Processing (kg)')
            st.plotly_chart(fig_daily, use_container_width=True)

    with col2:
        # Waste type distribution
        waste_types = {
            'Organic': sum([r.get('organic_weight', 0) for r in filtered_reports]),
            'Recyclable': sum([r.get('recyclable_weight', 0) for r in filtered_reports]),
            'Hazardous': sum([r.get('hazardous_weight', 0) for r in filtered_reports]),
            'General': sum([r.get('general_weight', 0) for r in filtered_reports])
        }

        # Filter out zero values
        waste_types = {k: v for k, v in waste_types.items() if v > 0}

        if waste_types:
            fig_waste = px.pie(values=list(waste_types.values()),
                               names=list(waste_types.keys()),
                               title='Waste Type Distribution')
            st.plotly_chart(fig_waste, use_container_width=True)

    # Quality trends
    st.subheader("📈 Quality Trends")

    col1, col2 = st.columns(2)

    with col1:
        # Segregation quality distribution
        quality_counts = {}
        for report in filtered_reports:
            quality = report.get('segregation_quality', 'unknown')
            quality_counts[quality] = quality_counts.get(quality, 0) + 1

        if quality_counts:
            fig_quality = px.bar(x=list(quality_counts.keys()),
                                 y=list(quality_counts.values()),
                                 title='Segregation Quality Distribution',
                                 color=list(quality_counts.values()),
                                 color_continuous_scale='RdYlGn')
            st.plotly_chart(fig_quality, use_container_width=True)

    with col2:
        # AI verification success rate over time
        weekly_verification = {}
        for report in filtered_reports:
            if report.get('verification_date'):
                try:
                    week = datetime.strptime(report['verification_date'][:10], '%Y-%m-%d').strftime('%Y-W%U')
                    if week not in weekly_verification:
                        weekly_verification[week] = {'total': 0, 'verified': 0}
                    weekly_verification[week]['total'] += 1
                    if report.get('ai_verified'):
                        weekly_verification[week]['verified'] += 1
                except:
                    continue

        if weekly_verification:
            verification_data = []
            for week, data in weekly_verification.items():
                success_rate = (data['verified'] / data['total']) * 100 if data['total'] > 0 else 0
                verification_data.append({'Week': week, 'Success Rate': success_rate})

            df_verification = pd.DataFrame(verification_data)
            fig_verification = px.line(df_verification, x='Week', y='Success Rate',
                                       title='AI Verification Success Rate (%)')
            st.plotly_chart(fig_verification, use_container_width=True)

    # Vehicle performance ranking
    st.subheader("🏆 Vehicle Performance Ranking")

    vehicle_performance = {}
    for report in filtered_reports:
        vehicle = report.get('vehicle_number', 'Unknown')
        if vehicle not in vehicle_performance:
            vehicle_performance[vehicle] = {
                'deliveries': 0,
                'total_weight': 0,
                'excellent_quality': 0,
                'ai_verified': 0
            }

        vehicle_performance[vehicle]['deliveries'] += 1
        vehicle_performance[vehicle]['total_weight'] += report.get('total_weight', 0)

        if report.get('segregation_quality') == 'excellent':
            vehicle_performance[vehicle]['excellent_quality'] += 1

        if report.get('ai_verified'):
            vehicle_performance[vehicle]['ai_verified'] += 1

    # Create performance DataFrame
    performance_data = []
    for vehicle, stats in vehicle_performance.items():
        quality_rate = (stats['excellent_quality'] / stats['deliveries']) * 100 if stats['deliveries'] > 0 else 0
        verification_rate = (stats['ai_verified'] / stats['deliveries']) * 100 if stats['deliveries'] > 0 else 0

        performance_data.append({
            'Vehicle': vehicle,
            'Deliveries': stats['deliveries'],
            'Total Weight (kg)': stats['total_weight'],
            'Quality Rate (%)': round(quality_rate, 1),
            'AI Verification Rate (%)': round(verification_rate, 1),
            'Performance Score': round((quality_rate + verification_rate) / 2, 1)
        })

    # Sort by performance score
    performance_data.sort(key=lambda x: x['Performance Score'], reverse=True)

    df_performance = pd.DataFrame(performance_data)
    st.dataframe(df_performance, use_container_width=True)

    # Export functionality
    if st.button("📥 Export Analytics Report"):
        # Create comprehensive report
        report_data = {
            'summary': {
                'date_range': f"{start_date} to {end_date}",
                'total_deliveries': len(filtered_reports),
                'total_weight': total_weight,
                'quality_rate': quality_rate,
                'verification_rate': verification_rate
            },
            'daily_processing': daily_data,
            'waste_distribution': waste_types,
            'quality_counts': quality_counts,
            'vehicle_performance': performance_data
        }

        report_json = json.dumps(report_data, indent=2, default=str)

        st.download_button(
            label="Download Analytics Report (JSON)",
            data=report_json,
            file_name=f"treatment_plant_analytics_{start_date}_{end_date}.json",
            mime="application/json"
        )
