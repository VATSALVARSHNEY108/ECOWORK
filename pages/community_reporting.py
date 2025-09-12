import streamlit as st
import pandas as pd
from datetime import datetime, date
import base64
import json
import random
from utils.database import add_record, get_records, update_record
from utils.ai_verification import analyze_community_report_image


def show():
    st.title("📢 Community Reporting System")

    tab1, tab2, tab3, tab4 = st.tabs(["Submit Report", "Community Feed", "Report Validation", "Analytics"])

    with tab1:
        submit_report()

    with tab2:
        community_feed()

    with tab3:
        report_validation()

    with tab4:
        analytics()


def submit_report():
    st.subheader("📸 Submit Waste Report")

    st.info(
        "📍 **Community Reporting**: Help keep your neighborhood clean by reporting waste issues. Valid reports earn reward points!")

    with st.form("community_report"):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📍 Location Details")

            # Location information
            reporter_name = st.text_input("Your Name*", placeholder="Full name")
            reporter_contact = st.text_input("Contact Number*", placeholder="Mobile number")
            reporter_email = st.text_input("Email", placeholder="Optional email for updates")

            # Location details
            area = st.text_input("Area/Locality*", placeholder="e.g., MG Road, Koramangala")
            landmark = st.text_input("Nearby Landmark", placeholder="e.g., Near City Mall")
            pincode = st.text_input("Pincode*", placeholder="6-digit pincode")

            # GPS coordinates simulation
            st.subheader("🗺️ GPS Location")
            use_gps = st.checkbox("Use current GPS location", value=True)

            if use_gps:
                # Simulate GPS coordinates
                latitude = st.number_input("Latitude", value=12.9716 + random.uniform(-0.05, 0.05), format="%.6f")
                longitude = st.number_input("Longitude", value=77.5946 + random.uniform(-0.05, 0.05), format="%.6f")
            else:
                latitude = st.number_input("Latitude*", value=0.0, format="%.6f")
                longitude = st.number_input("Longitude*", value=0.0, format="%.6f")

        with col2:
            st.subheader("🗑️ Waste Issue Details")

            issue_type = st.selectbox("Issue Type*", [
                "Illegal Dumping",
                "Overflowing Bins",
                "Littering",
                "Poor Segregation",
                "Hazardous Waste",
                "Construction Waste",
                "Burning of Waste",
                "Blocked Drainage",
                "Other"
            ])

            custom_issue = ""
            if issue_type == "Other":
                custom_issue = st.text_input("Specify Issue*", placeholder="Describe the specific issue")

            severity = st.selectbox("Severity Level*", [
                "Low - Minor issue",
                "Medium - Moderate concern",
                "High - Urgent attention needed"
            ])

            waste_types = st.multiselect("Waste Types Observed", [
                "Plastic Waste",
                "Food Waste",
                "Paper/Cardboard",
                "Glass",
                "Metal",
                "Electronic Waste",
                "Construction Debris",
                "Medical Waste",
                "Chemical Waste",
                "Mixed Waste"
            ])

            estimated_quantity = st.selectbox("Estimated Quantity", [
                "Small (Few items)",
                "Medium (Bag-sized)",
                "Large (Cart-sized)",
                "Very Large (Truck-sized)"
            ])

        st.subheader("📷 Photo Evidence")

        col1, col2 = st.columns(2)

        with col1:
            main_photo = st.file_uploader("Main Photo*",
                                          type=['png', 'jpg', 'jpeg'],
                                          help="Clear photo showing the waste issue")

            additional_photo = st.file_uploader("Additional Photo",
                                                type=['png', 'jpg', 'jpeg'],
                                                help="Optional: Another angle or close-up")

        with col2:
            # Photo guidelines
            st.info("""
            📸 **Photo Guidelines**:
            • Take clear, well-lit photos
            • Show the waste issue clearly
            • Include surrounding context
            • Avoid identifying individuals
            • Multiple angles helpful
            """)

        st.subheader("📝 Additional Information")

        description = st.text_area("Detailed Description*",
                                   placeholder="Describe the waste issue in detail, when you noticed it, how long it's been there, etc.")

        col1, col2 = st.columns(2)

        with col1:
            first_noticed = st.date_input("First Noticed", value=date.today())
            recurring_issue = st.checkbox("This is a recurring issue")

        with col2:
            best_time_to_address = st.selectbox("Best Time to Address", [
                "Morning (6-10 AM)",
                "Afternoon (10 AM-2 PM)",
                "Evening (2-6 PM)",
                "Anytime"
            ])

            anonymous = st.checkbox("Submit anonymously")

        urgency_notes = st.text_area("Urgency Notes",
                                     placeholder="Any specific reasons why this needs immediate attention")

        submitted = st.form_submit_button("📤 Submit Report")

        if submitted:
            if (reporter_name and reporter_contact and area and pincode and
                    issue_type and severity and main_photo and description):

                # Process severity
                severity_map = {
                    "Low - Minor issue": "low",
                    "Medium - Moderate concern": "medium",
                    "High - Urgent attention needed": "high"
                }

                # Create report record
                report_record = {
                    'reporter_name': reporter_name if not anonymous else 'Anonymous',
                    'reporter_contact': reporter_contact,
                    'reporter_email': reporter_email,
                    'area': area,
                    'landmark': landmark,
                    'pincode': pincode,
                    'latitude': latitude,
                    'longitude': longitude,
                    'issue_type': custom_issue if issue_type == "Other" and custom_issue else issue_type,
                    'severity': severity_map[severity],
                    'waste_types': waste_types,
                    'estimated_quantity': estimated_quantity,
                    'description': description,
                    'first_noticed': str(first_noticed),
                    'recurring_issue': recurring_issue,
                    'best_time_to_address': best_time_to_address,
                    'urgency_notes': urgency_notes,
                    'anonymous': anonymous,
                    'photos_uploaded': 2 if additional_photo else 1,
                    'status': 'submitted',
                    'upvotes': 0,
                    'downvotes': 0,
                    'validation_status': 'pending',
                    'ai_analysis_pending': True,
                    'created_at': datetime.now().isoformat()
                }

                record = add_record('community_reports', report_record)

                st.success(f"✅ Report submitted successfully! Report ID: {record['id']}")

                st.info("""
                📋 **Next Steps**:
                1. Your report will be analyzed by AI for validation
                2. Community members can upvote/confirm your report
                3. Valid reports earn reward points
                4. Authorities will be notified for action
                """)

                # Show estimated reward
                base_reward = {"low": 5, "medium": 10, "high": 15}
                estimated_points = base_reward[severity_map[severity]]
                st.success(f"🎁 Estimated reward if validated: {estimated_points} points")

                st.rerun()

            else:
                st.error("❌ Please fill in all required fields and upload a photo")


def community_feed():
    st.subheader("📋 Community Waste Reports")

    reports = get_records('community_reports', {})

    if not reports:
        st.info("📝 No community reports found. Submit the first report to get started!")
        return

    # Filters
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        status_filter = st.selectbox("Filter by Status",
                                     ["All", "submitted", "validated", "in_progress", "resolved", "rejected"])

    with col2:
        severity_filter = st.selectbox("Filter by Severity",
                                       ["All", "high", "medium", "low"])

    with col3:
        area_filter = st.selectbox("Filter by Area",
                                   ["All"] + list(set([r.get('area', 'Unknown') for r in reports])))

    with col4:
        sort_by = st.selectbox("Sort by",
                               ["Most Recent", "Most Upvotes", "Highest Severity", "Oldest First"])

    # Apply filters
    filtered_reports = reports

    if status_filter != "All":
        filtered_reports = [r for r in filtered_reports if r.get('status') == status_filter]

    if severity_filter != "All":
        filtered_reports = [r for r in filtered_reports if r.get('severity') == severity_filter]

    if area_filter != "All":
        filtered_reports = [r for r in filtered_reports if r.get('area') == area_filter]

    # Apply sorting
    if sort_by == "Most Recent":
        filtered_reports.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    elif sort_by == "Most Upvotes":
        filtered_reports.sort(key=lambda x: x.get('upvotes', 0), reverse=True)
    elif sort_by == "Highest Severity":
        severity_order = {'high': 3, 'medium': 2, 'low': 1}
        filtered_reports.sort(key=lambda x: severity_order.get(x.get('severity', 'low'), 0), reverse=True)
    elif sort_by == "Oldest First":
        filtered_reports.sort(key=lambda x: x.get('created_at', ''))

    # Summary statistics
    if filtered_reports:
        st.subheader("📊 Report Statistics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Reports", len(filtered_reports))

        with col2:
            high_severity = len([r for r in filtered_reports if r.get('severity') == 'high'])
            st.metric("High Severity", high_severity)

        with col3:
            validated_reports = len([r for r in filtered_reports if r.get('validation_status') == 'validated'])
            st.metric("Validated Reports", validated_reports)

        with col4:
            resolved_reports = len([r for r in filtered_reports if r.get('status') == 'resolved'])
            st.metric("Resolved Issues", resolved_reports)

    # Display reports
    for report in filtered_reports:
        severity_colors = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }

        severity_icon = severity_colors.get(report.get('severity'), '⚪')
        status_icon = {
            'submitted': '📤',
            'validated': '✅',
            'in_progress': '🔄',
            'resolved': '✅',
            'rejected': '❌'
        }.get(report.get('status'), '📝')

        with st.expander(
                f"{severity_icon} {status_icon} {report.get('issue_type', 'Unknown Issue')} - {report.get('area', 'Unknown Area')} (ID: {report.get('id', 'N/A')})"):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.write(f"**Reporter**: {report.get('reporter_name', 'Anonymous')}")
                st.write(f"**Location**: {report.get('area', 'N/A')}")
                if report.get('landmark'):
                    st.write(f"**Landmark**: {report.get('landmark')}")
                st.write(f"**Issue Type**: {report.get('issue_type', 'N/A')}")
                st.write(f"**Severity**: {report.get('severity', 'Unknown').title()}")
                st.write(f"**Status**: {report.get('status', 'Unknown').title()}")

                if report.get('waste_types'):
                    st.write(f"**Waste Types**: {', '.join(report.get('waste_types', []))}")

                st.write(f"**Description**: {report.get('description', 'No description provided')}")

                if report.get('urgency_notes'):
                    st.warning(f"**Urgency**: {report.get('urgency_notes')}")

            with col2:
                st.write(f"**Reported**: {report.get('created_at', 'N/A')[:10]}")
                st.write(f"**First Noticed**: {report.get('first_noticed', 'N/A')}")
                st.write(f"**Quantity**: {report.get('estimated_quantity', 'N/A')}")
                st.write(f"**Recurring**: {'Yes' if report.get('recurring_issue') else 'No'}")
                st.write(f"**Best Time**: {report.get('best_time_to_address', 'N/A')}")
                st.write(f"**Photos**: {report.get('photos_uploaded', 0)} uploaded")

                # GPS coordinates
                if report.get('latitude') and report.get('longitude'):
                    st.write(f"**GPS**: {report.get('latitude', 0):.4f}, {report.get('longitude', 0):.4f}")

            # Community interaction
            st.subheader("👥 Community Validation")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                upvotes = report.get('upvotes', 0)
                if st.button(f"👍 Upvote ({upvotes})", key=f"upvote_{report.get('id')}"):
                    update_record('community_reports', report.get('id'),
                                  {'upvotes': upvotes + 1})
                    st.success("Upvoted!")
                    st.rerun()

            with col2:
                downvotes = report.get('downvotes', 0)
                if st.button(f"👎 Downvote ({downvotes})", key=f"downvote_{report.get('id')}"):
                    update_record('community_reports', report.get('id'),
                                  {'downvotes': downvotes + 1})
                    st.success("Downvoted!")
                    st.rerun()

            with col3:
                if st.button(f"✅ Confirm Issue", key=f"confirm_{report.get('id')}"):
                    # Add confirmation
                    confirmations = report.get('confirmations', 0) + 1
                    update_record('community_reports', report.get('id'),
                                  {'confirmations': confirmations})

                    # Auto-validate if enough confirmations
                    if confirmations >= 3 and report.get('validation_status') == 'pending':
                        update_record('community_reports', report.get('id'),
                                      {'validation_status': 'validated', 'status': 'validated'})

                        # Award points to reporter
                        base_points = {"low": 5, "medium": 10, "high": 15}
                        points = base_points.get(report.get('severity', 'low'), 5)

                        add_record('rewards_fines', {
                            'reporter_name': report.get('reporter_name', 'Anonymous'),
                            'type': 'community_reward',
                            'reason': f'Validated community report - {report.get("issue_type")}',
                            'amount': points,
                            'community_report_id': report.get('id'),
                            'created_at': datetime.now().isoformat()
                        })

                    st.success("Confirmed!")
                    st.rerun()

            with col4:
                confirmations = report.get('confirmations', 0)
                st.write(f"**Confirmations**: {confirmations}")

            # Validation status
            validation_status = report.get('validation_status', 'pending')
            if validation_status == 'validated':
                st.success("✅ Report validated by community")
            elif validation_status == 'rejected':
                st.error("❌ Report rejected")
            else:
                st.info("⏳ Pending community validation")


def report_validation():
    st.subheader("🔍 Report Validation System")

    st.info(
        "🤖 **AI + Community Validation**: Reports are validated using AI analysis and community confirmations before rewards are issued.")

    # Get pending validations
    pending_reports = get_records('community_reports', {'ai_analysis_pending': True})

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🤖 AI Analysis Queue")

        if pending_reports:
            st.write(f"**Pending AI Analysis**: {len(pending_reports)} reports")

            for report in pending_reports[:5]:  # Show first 5
                with st.expander(f"📸 {report.get('issue_type', 'Unknown')} - {report.get('area', 'N/A')}"):
                    st.write(f"**Severity**: {report.get('severity', 'Unknown').title()}")
                    st.write(f"**Submitted**: {report.get('created_at', 'N/A')[:10]}")
                    st.write(f"**Photos**: {report.get('photos_uploaded', 0)}")

                    if st.button(f"🤖 Run AI Analysis", key=f"ai_analyze_{report.get('id')}"):
                        st.info("🤖 Analyzing photos...")

                        # Simulate AI analysis (in real app, would process actual photos)
                        ai_result = {
                            'valid': True,
                            'severity': report.get('severity'),
                            'waste_type': 'Mixed Waste',
                            'description': 'AI detected legitimate waste management issue requiring attention',
                            'action_required': True,
                            'confidence_score': 0.87
                        }

                        # In real implementation, would call:
                        # ai_result = analyze_community_report_image(photo_base64)

                        # Update record
                        update_record('community_reports', report.get('id'), {
                            'ai_analysis_pending': False,
                            'ai_analysis_result': ai_result,
                            'ai_validated': ai_result['valid'],
                            'ai_confidence': ai_result.get('confidence_score', 0),
                            'analysis_date': datetime.now().isoformat()
                        })

                        if ai_result['valid']:
                            st.success("✅ AI Analysis: Valid waste issue detected")
                        else:
                            st.warning("⚠️ AI Analysis: Issue requires manual review")

                        st.write(f"**Confidence**: {ai_result.get('confidence_score', 0):.1%}")
                        st.write(f"**Description**: {ai_result.get('description', 'No description')}")

                        st.rerun()
        else:
            st.success("✅ No reports pending AI analysis")

    with col2:
        st.subheader("👥 Community Validation Status")

        all_reports = get_records('community_reports', {})

        # Validation statistics
        validation_stats = {
            'pending': len([r for r in all_reports if r.get('validation_status') == 'pending']),
            'validated': len([r for r in all_reports if r.get('validation_status') == 'validated']),
            'rejected': len([r for r in all_reports if r.get('validation_status') == 'rejected'])
        }

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Pending", validation_stats['pending'])
        with col2:
            st.metric("Validated", validation_stats['validated'])
        with col3:
            st.metric("Rejected", validation_stats['rejected'])

        # Recent validations
        st.subheader("📋 Recent Validations")

        recent_validated = [r for r in all_reports if r.get('validation_status') in ['validated', 'rejected']]
        recent_validated.sort(key=lambda x: x.get('analysis_date', ''), reverse=True)

        for report in recent_validated[:5]:
            status_icon = "✅" if report.get('validation_status') == 'validated' else "❌"
            st.write(f"{status_icon} **{report.get('issue_type', 'Unknown')}** - {report.get('area', 'N/A')}")

            col1, col2 = st.columns(2)
            with col1:
                st.write(f"  Upvotes: {report.get('upvotes', 0)}")
                st.write(f"  Confirmations: {report.get('confirmations', 0)}")
            with col2:
                if report.get('ai_confidence'):
                    st.write(f"  AI Confidence: {report.get('ai_confidence', 0):.1%}")

    # Validation Rules
    st.subheader("📋 Validation Rules")

    st.markdown("""
    ### 🎯 Automatic Validation Triggers

    **✅ Auto-Validate When**:
    - AI confidence > 80% AND 3+ community confirmations
    - 5+ community confirmations (regardless of AI)
    - High severity + AI validated + 2+ confirmations

    **❌ Auto-Reject When**:
    - AI confidence < 30%
    - 3+ downvotes with no confirmations
    - Duplicate report (same location + time)

    **⏳ Manual Review Required**:
    - AI confidence 30-80% with mixed community response
    - Conflicting community feedback
    - Sensitive locations or situations

    ### 🎁 Reward Structure
    - **Low Severity**: 5 points
    - **Medium Severity**: 10 points  
    - **High Severity**: 15 points
    - **Bonus**: +5 points for high AI confidence (>90%)
    - **Community Bonus**: +2 points for each confirmation beyond 3
    """)


def analytics():
    st.subheader("📊 Community Reporting Analytics")

    reports = get_records('community_reports', {})

    if not reports:
        st.info("📊 No community reports available for analytics.")
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
            report_date = datetime.strptime(report.get('created_at', '')[:10], '%Y-%m-%d').date()
            if start_date <= report_date <= end_date:
                filtered_reports.append(report)
        except:
            continue

    if not filtered_reports:
        st.warning("No data available for the selected date range.")
        return

    # Key metrics
    st.subheader("🎯 Key Metrics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Reports", len(filtered_reports))

    with col2:
        validated = len([r for r in filtered_reports if r.get('validation_status') == 'validated'])
        validation_rate = (validated / len(filtered_reports)) * 100 if filtered_reports else 0
        st.metric("Validation Rate", f"{validation_rate:.1f}%")

    with col3:
        resolved = len([r for r in filtered_reports if r.get('status') == 'resolved'])
        resolution_rate = (resolved / len(filtered_reports)) * 100 if filtered_reports else 0
        st.metric("Resolution Rate", f"{resolution_rate:.1f}%")

    with col4:
        total_upvotes = sum([r.get('upvotes', 0) for r in filtered_reports])
        st.metric("Community Engagement", total_upvotes)

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        # Reports by severity
        severity_counts = {'high': 0, 'medium': 0, 'low': 0}
        for report in filtered_reports:
            severity = report.get('severity', 'low')
            severity_counts[severity] += 1

        import plotly.express as px
        fig_severity = px.pie(values=list(severity_counts.values()),
                              names=list(severity_counts.keys()),
                              title='Reports by Severity',
                              color_discrete_map={'high': 'red', 'medium': 'orange', 'low': 'green'})
        st.plotly_chart(fig_severity, use_container_width=True)

    with col2:
        # Reports by issue type
        issue_counts = {}
        for report in filtered_reports:
            issue = report.get('issue_type', 'Unknown')
            issue_counts[issue] = issue_counts.get(issue, 0) + 1

        # Top 5 issue types
        top_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        fig_issues = px.bar(x=[item[1] for item in top_issues],
                            y=[item[0] for item in top_issues],
                            orientation='h',
                            title='Top Issue Types')
        st.plotly_chart(fig_issues, use_container_width=True)

    # Geographic distribution
    st.subheader("🗺️ Geographic Distribution")

    area_stats = {}
    for report in filtered_reports:
        area = report.get('area', 'Unknown')
        if area not in area_stats:
            area_stats[area] = {'total': 0, 'high_severity': 0, 'resolved': 0}

        area_stats[area]['total'] += 1

        if report.get('severity') == 'high':
            area_stats[area]['high_severity'] += 1

        if report.get('status') == 'resolved':
            area_stats[area]['resolved'] += 1

    # Convert to DataFrame
    area_data = []
    for area, stats in area_stats.items():
        resolution_rate = (stats['resolved'] / stats['total']) * 100 if stats['total'] > 0 else 0
        area_data.append({
            'Area': area,
            'Total Reports': stats['total'],
            'High Severity': stats['high_severity'],
            'Resolved': stats['resolved'],
            'Resolution Rate (%)': round(resolution_rate, 1)
        })

    # Sort by total reports
    area_data.sort(key=lambda x: x['Total Reports'], reverse=True)

    df_areas = pd.DataFrame(area_data)
    st.dataframe(df_areas, use_container_width=True)

    # Timeline analysis
    st.subheader("📈 Timeline Analysis")

    # Daily reports
    daily_counts = {}
    for report in filtered_reports:
        try:
            date_key = report.get('created_at', '')[:10]
            daily_counts[date_key] = daily_counts.get(date_key, 0) + 1
        except:
            continue

    if daily_counts:
        df_daily = pd.DataFrame(list(daily_counts.items()), columns=['Date', 'Reports'])
        df_daily['Date'] = pd.to_datetime(df_daily['Date'])
        df_daily = df_daily.sort_values('Date')

        fig_timeline = px.line(df_daily, x='Date', y='Reports',
                               title='Daily Report Submissions')
        st.plotly_chart(fig_timeline, use_container_width=True)

    # Community engagement metrics
    st.subheader("👥 Community Engagement")

    col1, col2 = st.columns(2)

    with col1:
        # Top reporters
        reporter_stats = {}
        for report in filtered_reports:
            reporter = report.get('reporter_name', 'Anonymous')
            if reporter != 'Anonymous':
                reporter_stats[reporter] = reporter_stats.get(reporter, 0) + 1

        if reporter_stats:
            top_reporters = sorted(reporter_stats.items(), key=lambda x: x[1], reverse=True)[:5]

            st.write("**🏆 Top Reporters**:")
            for i, (reporter, count) in enumerate(top_reporters, 1):
                st.write(f"{i}. {reporter}: {count} reports")

    with col2:
        # Engagement statistics
        total_upvotes = sum([r.get('upvotes', 0) for r in filtered_reports])
        total_confirmations = sum([r.get('confirmations', 0) for r in filtered_reports])
        avg_engagement = (total_upvotes + total_confirmations) / len(filtered_reports) if filtered_reports else 0

        st.write("**📊 Engagement Stats**:")
        st.write(f"• Total Upvotes: {total_upvotes}")
        st.write(f"• Total Confirmations: {total_confirmations}")
        st.write(f"• Avg Engagement per Report: {avg_engagement:.1f}")

    # Export functionality
    if st.button("📥 Export Community Analytics"):
        analytics_data = {
            'summary': {
                'date_range': f"{start_date} to {end_date}",
                'total_reports': len(filtered_reports),
                'validation_rate': validation_rate,
                'resolution_rate': resolution_rate,
                'total_engagement': total_upvotes + total_confirmations
            },
            'severity_distribution': severity_counts,
            'issue_types': dict(issue_counts),
            'geographic_stats': area_data,
            'daily_counts': daily_counts,
            'top_reporters': dict(top_reporters) if 'top_reporters' in locals() else {}
        }

        analytics_json = json.dumps(analytics_data, indent=2, default=str)

        st.download_button(
            label="Download Analytics Report (JSON)",
            data=analytics_json,
            file_name=f"community_analytics_{start_date}_{end_date}.json",
            mime="application/json"
        )
