import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import json
from utils.database import add_record, get_records, update_record


def show():
    st.title("🎁 Rewards & Fines Management")

    tab1, tab2, tab3, tab4 = st.tabs(["Rewards Dashboard", "Issue Fines", "Transaction History", "Analytics"])

    with tab1:
        rewards_dashboard()

    with tab2:
        issue_fines()

    with tab3:
        transaction_history()

    with tab4:
        analytics()


def rewards_dashboard():
    st.subheader("🎁 Rewards & Recognition System")

    st.info(
        "🏆 **Reward System**: Citizens and workers earn points for proper waste segregation, community reporting, and quality service delivery.")

    # Get rewards data
    rewards = get_records('rewards_fines', {})

    # Summary cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_rewards = len(
            [r for r in rewards if r.get('type') in ['reward', 'incentive', 'community_reward', 'ai_bonus']])
        st.metric("Total Rewards Issued", total_rewards)

    with col2:
        total_points = sum([r.get('amount', 0) for r in rewards if
                            r.get('type') in ['reward', 'incentive', 'community_reward', 'ai_bonus']])
        st.metric("Total Points Awarded", total_points)

    with col3:
        active_participants = len(set([r.get('family_id') for r in rewards if r.get('family_id')] +
                                      [r.get('worker_name') for r in rewards if r.get('worker_name')] +
                                      [r.get('reporter_name') for r in rewards if r.get('reporter_name')]))
        st.metric("Active Participants", active_participants)

    with col4:
        recent_rewards = len([r for r in rewards if r.get('created_at', '')[:10] == str(date.today())])
        st.metric("Today's Rewards", recent_rewards)

    # Leaderboards
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏆 Top Families (This Month)")

        # Calculate family points
        family_points = {}
        families = get_records('families', {})
        family_lookup = {f['id']: f['family_name'] for f in families}

        current_month = datetime.now().strftime('%Y-%m')
        for reward in rewards:
            if (reward.get('family_id') and
                    reward.get('created_at', '').startswith(current_month) and
                    reward.get('type') in ['reward', 'incentive']):

                family_id = reward.get('family_id')
                family_name = family_lookup.get(family_id, f'Family {family_id}')

                if family_name not in family_points:
                    family_points[family_name] = {'points': 0, 'rewards': 0}

                family_points[family_name]['points'] += reward.get('amount', 0)
                family_points[family_name]['rewards'] += 1

        # Sort by points
        top_families = sorted(family_points.items(), key=lambda x: x[1]['points'], reverse=True)[:10]

        if top_families:
            for i, (family, data) in enumerate(top_families, 1):
                rank_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                st.write(f"{rank_emoji} **{family}** - {data['points']} points ({data['rewards']} rewards)")
        else:
            st.info("No family rewards recorded this month")

    with col2:
        st.subheader("🚛 Top Workers (This Month)")

        # Calculate worker points
        worker_points = {}
        current_month = datetime.now().strftime('%Y-%m')

        for reward in rewards:
            if (reward.get('worker_name') and
                    reward.get('created_at', '').startswith(current_month) and
                    reward.get('type') in ['incentive', 'ai_bonus']):

                worker_name = reward.get('worker_name')

                if worker_name not in worker_points:
                    worker_points[worker_name] = {'points': 0, 'rewards': 0}

                worker_points[worker_name]['points'] += reward.get('amount', 0)
                worker_points[worker_name]['rewards'] += 1

        # Sort by points
        top_workers = sorted(worker_points.items(), key=lambda x: x[1]['points'], reverse=True)[:10]

        if top_workers:
            for i, (worker, data) in enumerate(top_workers, 1):
                rank_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                st.write(f"{rank_emoji} **{worker}** - {data['points']} points ({data['rewards']} rewards)")
        else:
            st.info("No worker incentives recorded this month")

    # Recent rewards
    st.subheader("📋 Recent Rewards & Incentives")

    recent_rewards = [r for r in rewards if r.get('type') in ['reward', 'incentive', 'community_reward', 'ai_bonus']]
    recent_rewards.sort(key=lambda x: x.get('created_at', ''), reverse=True)

    for reward in recent_rewards[:10]:
        reward_icons = {
            'reward': '🎁',
            'incentive': '💰',
            'community_reward': '👥',
            'ai_bonus': '🤖'
        }

        icon = reward_icons.get(reward.get('type'), '🏆')

        # Determine recipient
        recipient = (reward.get('family_name') or
                     reward.get('worker_name') or
                     reward.get('reporter_name') or
                     'Unknown')

        st.write(
            f"{icon} **{recipient}** earned **{reward.get('amount', 0)} points** - {reward.get('reason', 'No reason specified')} ({reward.get('created_at', 'N/A')[:10]})")

    # Reward categories
    st.subheader("🎯 Reward Categories & Points")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 🏠 Household Rewards
        - **Excellent Segregation**: 10 points
        - **Good Segregation**: 5 points
        - **Consistent Quality**: 15 points bonus (monthly)
        - **Zero Violations**: 20 points bonus (monthly)

        ### 👥 Community Rewards
        - **Valid Report (Low Severity)**: 5 points
        - **Valid Report (Medium Severity)**: 10 points
        - **Valid Report (High Severity)**: 15 points
        - **High AI Confidence Bonus**: +5 points
        - **Community Confirmations**: +2 points each
        """)

    with col2:
        st.markdown("""
        ### 🚛 Worker Incentives
        - **Quality Delivery (Good)**: 25 points
        - **Quality Delivery (Excellent)**: 50 points
        - **AI Verification Bonus**: 15 points
        - **Safety Compliance**: 10 points
        - **Route Efficiency**: 20 points

        ### 🎁 Reward Redemption
        - **50 points**: Discount coupon (₹100)
        - **100 points**: Cash reward (₹200)
        - **200 points**: Utility bill discount (₹500)
        - **500 points**: Special recognition certificate
        """)

    # Manual reward issuance
    st.subheader("➕ Issue Manual Reward")

    with st.form("manual_reward"):
        col1, col2 = st.columns(2)

        with col1:
            recipient_type = st.selectbox("Recipient Type", ["Family", "Worker", "Community Member"])

            if recipient_type == "Family":
                families = get_records('families', {})
                family_options = [f"{f['family_name']} (ID: {f['id']})" for f in families]
                family_options.insert(0, "Select family")
                selected_recipient = st.selectbox("Select Family", family_options)

            elif recipient_type == "Worker":
                workers = get_records('workers', {})
                worker_options = [f"{w['worker_name']} - {w['job_type']}" for w in workers]
                worker_options.insert(0, "Select worker")
                selected_recipient = st.selectbox("Select Worker", worker_options)

            else:  # Community Member
                selected_recipient = st.text_input("Community Member Name", placeholder="Enter name")

            reward_reason = st.text_input("Reward Reason*", placeholder="Reason for reward")

        with col2:
            reward_points = st.number_input("Points to Award*", min_value=1, max_value=100, value=10)
            reward_category = st.selectbox("Category", [
                "Manual Award",
                "Special Recognition",
                "Bonus Performance",
                "Community Service",
                "Environmental Excellence"
            ])

            notes = st.text_area("Additional Notes", placeholder="Optional notes about this reward")

        submitted = st.form_submit_button("🎁 Issue Reward")

        if submitted:
            if selected_recipient and reward_reason and recipient_type:
                if ((recipient_type == "Family" and selected_recipient != "Select family") or
                        (recipient_type == "Worker" and selected_recipient != "Select worker") or
                        (recipient_type == "Community Member" and selected_recipient)):

                    # Create manual reward record
                    reward_record = {
                        'type': 'manual_reward',
                        'reason': reward_reason,
                        'amount': reward_points,
                        'category': reward_category,
                        'notes': notes,
                        'issued_by': 'Admin',  # In real app, would use current user
                        'created_at': datetime.now().isoformat()
                    }

                    # Add recipient-specific fields
                    if recipient_type == "Family":
                        family_id = selected_recipient.split("ID: ")[1].split(")")[0]
                        family_name = selected_recipient.split(" (ID:")[0]
                        reward_record.update({
                            'family_id': int(family_id),
                            'family_name': family_name
                        })

                    elif recipient_type == "Worker":
                        worker_name = selected_recipient.split(" - ")[0]
                        reward_record['worker_name'] = worker_name

                    else:
                        reward_record['reporter_name'] = selected_recipient

                    record = add_record('rewards_fines', reward_record)

                    st.success(
                        f"✅ Reward issued successfully! {reward_points} points awarded to {selected_recipient.split('(')[0] if '(' in selected_recipient else selected_recipient}")
                    st.rerun()

                else:
                    st.error("❌ Please select a valid recipient")
            else:
                st.error("❌ Please fill in all required fields")


def issue_fines():
    st.subheader("⚠️ Fines & Penalties System")

    st.info(
        "📋 **Penalty System**: Issue fines for repeat violations, poor segregation, and non-compliance with waste management rules.")

    # Get violations data
    fines = get_records('rewards_fines', {})
    violations = [f for f in fines if f.get('type') in ['fine', 'warning', 'penalty']]

    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_fines = len([v for v in violations if v.get('type') == 'fine'])
        st.metric("Total Fines Issued", total_fines)

    with col2:
        total_warnings = len([v for v in violations if v.get('type') == 'warning'])
        st.metric("Warnings Issued", total_warnings)

    with col3:
        total_amount = sum([v.get('amount', 0) for v in violations if v.get('type') == 'fine'])
        st.metric("Total Fine Amount", f"₹{total_amount}")

    with col4:
        recent_violations = len([v for v in violations if v.get('created_at', '')[:10] == str(date.today())])
        st.metric("Today's Violations", recent_violations)

    # Issue new fine/warning
    st.subheader("➕ Issue Fine or Warning")

    with st.form("issue_fine"):
        col1, col2 = st.columns(2)

        with col1:
            violation_type = st.selectbox("Violation Type", ["Warning", "Fine", "Penalty"])

            # Select family
            families = get_records('families', {})
            family_options = [f"{f['family_name']} - {f['address'][:30]}... (ID: {f['id']})" for f in families]
            family_options.insert(0, "Select family")
            selected_family = st.selectbox("Select Family", family_options)

            violation_reason = st.selectbox("Violation Reason", [
                "Poor Waste Segregation",
                "Improper Bin Placement",
                "Mixed Waste Types",
                "Hazardous Waste Mishandling",
                "Non-compliance with Schedule",
                "Littering/Illegal Dumping",
                "Contaminated Recyclables",
                "Overweight Bins",
                "Other"
            ])

            custom_reason = ""
            if violation_reason == "Other":
                custom_reason = st.text_input("Specify Violation*", placeholder="Describe the specific violation")

        with col2:
            if violation_type == "Fine":
                fine_amount = st.number_input("Fine Amount (₹)*", min_value=50, max_value=5000, value=100, step=50)
            else:
                fine_amount = 0

            severity = st.selectbox("Severity", ["Low", "Medium", "High"])

            # Check for repeat violations
            if selected_family and selected_family != "Select family":
                family_id = int(selected_family.split("ID: ")[1].split(")")[0])
                previous_violations = [v for v in violations if v.get('family_id') == family_id]

                st.info(f"**Previous Violations**: {len(previous_violations)}")

                if len(previous_violations) >= 2:
                    st.warning("⚠️ **Repeat Offender**: This family has multiple previous violations")
                    repeat_offender_penalty = st.checkbox("Apply repeat offender penalty (+50%)")
                    if repeat_offender_penalty and violation_type == "Fine":
                        fine_amount = int(fine_amount * 1.5)
                        st.write(f"**Adjusted Fine Amount**: ₹{fine_amount}")

            violation_date = st.date_input("Violation Date", value=date.today())

            # Collection record reference
            collections = get_records('collections', {})
            collection_options = [
                f"Collection {c['id']} - {c.get('family_name', 'Unknown')} ({c.get('collection_date', 'N/A')})"
                for c in collections if c.get('segregation_quality') == 'poor']
            collection_options.insert(0, "No related collection record")

            related_collection = st.selectbox("Related Collection Record", collection_options)

        detailed_description = st.text_area("Detailed Description*",
                                            placeholder="Provide specific details about the violation")

        # Evidence
        st.subheader("📷 Evidence")
        evidence_photo = st.file_uploader("Photo Evidence", type=['png', 'jpg', 'jpeg'])

        # Inspector details
        col1, col2 = st.columns(2)
        with col1:
            inspector_name = st.text_input("Inspector Name*", placeholder="Name of person issuing violation")
        with col2:
            inspector_id = st.text_input("Inspector ID", placeholder="Inspector identification number")

        submitted = st.form_submit_button(f"📋 Issue {violation_type}")

        if submitted:
            if (selected_family and selected_family != "Select family" and
                    violation_reason and detailed_description and inspector_name):

                # Extract family information
                family_id = int(selected_family.split("ID: ")[1].split(")")[0])
                family_name = selected_family.split(" - ")[0]

                # Create violation record
                violation_record = {
                    'type': violation_type.lower(),
                    'family_id': family_id,
                    'family_name': family_name,
                    'reason': custom_reason if violation_reason == "Other" else violation_reason,
                    'amount': fine_amount,
                    'severity': severity.lower(),
                    'violation_date': str(violation_date),
                    'detailed_description': detailed_description,
                    'inspector_name': inspector_name,
                    'inspector_id': inspector_id,
                    'evidence_photo': evidence_photo is not None,
                    'status': 'issued',
                    'payment_status': 'pending' if fine_amount > 0 else 'n/a',
                    'created_at': datetime.now().isoformat()
                }

                # Add collection record reference if selected
                if related_collection and related_collection != "No related collection record":
                    collection_id = related_collection.split("Collection ")[1].split(" -")[0]
                    violation_record['collection_record_id'] = int(collection_id)

                record = add_record('rewards_fines', violation_record)

                st.success(f"✅ {violation_type} issued successfully! Record ID: {record['id']}")

                if fine_amount > 0:
                    st.warning(f"💰 Fine amount: ₹{fine_amount} - Payment pending")

                # Update family's violation count
                families = get_records('families', {'id': family_id})
                if families:
                    family = families[0]
                    violation_count = family.get('violation_count', 0) + 1
                    update_record('families', family_id, {'violation_count': violation_count})

                st.rerun()

            else:
                st.error("❌ Please fill in all required fields")

    # Recent violations
    st.subheader("📋 Recent Violations")

    violations.sort(key=lambda x: x.get('created_at', ''), reverse=True)

    for violation in violations[:10]:
        violation_icons = {
            'warning': '⚠️',
            'fine': '💰',
            'penalty': '🚫'
        }

        icon = violation_icons.get(violation.get('type'), '📋')
        amount_text = f" - ₹{violation.get('amount', 0)}" if violation.get('amount', 0) > 0 else ""

        with st.expander(
                f"{icon} {violation.get('family_name', 'Unknown')} - {violation.get('reason', 'No reason')}{amount_text}"):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Type**: {violation.get('type', 'Unknown').title()}")
                st.write(f"**Family**: {violation.get('family_name', 'Unknown')}")
                st.write(f"**Reason**: {violation.get('reason', 'No reason specified')}")
                st.write(f"**Severity**: {violation.get('severity', 'Unknown').title()}")
                st.write(f"**Date**: {violation.get('violation_date', 'N/A')}")

            with col2:
                st.write(f"**Amount**: ₹{violation.get('amount', 0)}")
                st.write(f"**Status**: {violation.get('status', 'Unknown').title()}")
                st.write(f"**Payment**: {violation.get('payment_status', 'N/A').title()}")
                st.write(f"**Inspector**: {violation.get('inspector_name', 'Unknown')}")
                st.write(f"**Evidence Photo**: {'Yes' if violation.get('evidence_photo') else 'No'}")

            if violation.get('detailed_description'):
                st.write(f"**Description**: {violation.get('detailed_description')}")

            # Update status buttons
            if violation.get('status') == 'issued':
                col1, col2 = st.columns(2)

                with col1:
                    if st.button(f"✅ Mark Resolved", key=f"resolve_{violation.get('id')}"):
                        update_record('rewards_fines', violation.get('id'), {'status': 'resolved'})
                        st.success("Violation marked as resolved")
                        st.rerun()

                with col2:
                    if violation.get('amount', 0) > 0 and violation.get('payment_status') == 'pending':
                        if st.button(f"💰 Mark Paid", key=f"paid_{violation.get('id')}"):
                            update_record('rewards_fines', violation.get('id'), {'payment_status': 'paid'})
                            st.success("Payment recorded")
                            st.rerun()


def transaction_history():
    st.subheader("📊 Transaction History")

    all_transactions = get_records('rewards_fines', {})

    if not all_transactions:
        st.info("📝 No transaction history found.")
        return

    # Filters
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        transaction_type = st.selectbox("Transaction Type",
                                        ["All", "Rewards", "Fines", "Warnings", "Incentives"])

    with col2:
        date_filter = st.date_input("Filter by Date", value=None)

    with col3:
        amount_filter = st.selectbox("Amount Range",
                                     ["All", "0 points/₹", "1-50", "51-100", "100+"])

    with col4:
        status_filter = st.selectbox("Status",
                                     ["All", "issued", "resolved", "pending", "paid"])

    # Apply filters
    filtered_transactions = all_transactions

    # Type filter
    if transaction_type == "Rewards":
        filtered_transactions = [t for t in filtered_transactions
                                 if t.get('type') in ['reward', 'manual_reward', 'community_reward']]
    elif transaction_type == "Fines":
        filtered_transactions = [t for t in filtered_transactions if t.get('type') == 'fine']
    elif transaction_type == "Warnings":
        filtered_transactions = [t for t in filtered_transactions if t.get('type') == 'warning']
    elif transaction_type == "Incentives":
        filtered_transactions = [t for t in filtered_transactions
                                 if t.get('type') in ['incentive', 'ai_bonus']]

    # Date filter
    if date_filter:
        filtered_transactions = [t for t in filtered_transactions
                                 if t.get('created_at', '').startswith(str(date_filter))]

    # Amount filter
    if amount_filter != "All":
        if amount_filter == "0 points/₹":
            filtered_transactions = [t for t in filtered_transactions if t.get('amount', 0) == 0]
        elif amount_filter == "1-50":
            filtered_transactions = [t for t in filtered_transactions
                                     if 1 <= t.get('amount', 0) <= 50]
        elif amount_filter == "51-100":
            filtered_transactions = [t for t in filtered_transactions
                                     if 51 <= t.get('amount', 0) <= 100]
        elif amount_filter == "100+":
            filtered_transactions = [t for t in filtered_transactions if t.get('amount', 0) > 100]

    # Status filter
    if status_filter != "All":
        filtered_transactions = [t for t in filtered_transactions if t.get('status') == status_filter]

    # Sort by date (newest first)
    filtered_transactions.sort(key=lambda x: x.get('created_at', ''), reverse=True)

    # Summary of filtered results
    if filtered_transactions:
        st.subheader("📊 Filtered Results Summary")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Transactions", len(filtered_transactions))

        with col2:
            rewards_count = len([t for t in filtered_transactions
                                 if t.get('type') in ['reward', 'manual_reward', 'community_reward', 'incentive',
                                                      'ai_bonus']])
            st.metric("Rewards/Incentives", rewards_count)

        with col3:
            violations_count = len([t for t in filtered_transactions
                                    if t.get('type') in ['fine', 'warning', 'penalty']])
            st.metric("Violations", violations_count)

        with col4:
            total_amount = sum([t.get('amount', 0) for t in filtered_transactions])
            st.metric("Total Amount", f"{total_amount} pts/₹")

    # Transaction table
    st.subheader("📋 Transaction Details")

    # Convert to DataFrame for better display
    if filtered_transactions:
        transaction_data = []

        for transaction in filtered_transactions:
            # Determine recipient
            recipient = (transaction.get('family_name') or
                         transaction.get('worker_name') or
                         transaction.get('reporter_name') or
                         'Unknown')

            # Determine transaction nature
            if transaction.get('type') in ['reward', 'manual_reward', 'community_reward', 'incentive', 'ai_bonus']:
                nature = "Credit"
                amount_display = f"+{transaction.get('amount', 0)} pts"
            else:
                nature = "Debit"
                amount_display = f"-₹{transaction.get('amount', 0)}" if transaction.get('amount', 0) > 0 else "Warning"

            transaction_data.append({
                'ID': transaction.get('id', 'N/A'),
                'Date': transaction.get('created_at', 'N/A')[:10],
                'Type': transaction.get('type', 'Unknown').title(),
                'Nature': nature,
                'Recipient': recipient,
                'Amount': amount_display,
                'Reason': transaction.get('reason', 'No reason specified'),
                'Status': transaction.get('status', 'N/A').title()
            })

        df_transactions = pd.DataFrame(transaction_data)

        # Display with pagination
        items_per_page = 20
        total_pages = len(df_transactions) // items_per_page + (1 if len(df_transactions) % items_per_page > 0 else 0)

        if total_pages > 1:
            page = st.selectbox("Page", range(1, total_pages + 1))
            start_idx = (page - 1) * items_per_page
            end_idx = start_idx + items_per_page
            df_display = df_transactions.iloc[start_idx:end_idx]
        else:
            df_display = df_transactions

        st.dataframe(df_display, use_container_width=True)

        # Export functionality
        if st.button("📥 Export Transaction History"):
            csv = df_transactions.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"transaction_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

    else:
        st.info("No transactions found matching the selected criteria.")


def analytics():
    st.subheader("📊 Rewards & Fines Analytics")

    transactions = get_records('rewards_fines', {})

    if not transactions:
        st.info("📊 No data available for analytics.")
        return

    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=date.today() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", value=date.today())

    # Filter by date range
    filtered_transactions = []
    for transaction in transactions:
        try:
            transaction_date = datetime.strptime(transaction.get('created_at', '')[:10], '%Y-%m-%d').date()
            if start_date <= transaction_date <= end_date:
                filtered_transactions.append(transaction)
        except:
            continue

    if not filtered_transactions:
        st.warning("No data available for the selected date range.")
        return

    # Key Performance Indicators
    st.subheader("🎯 Key Performance Indicators")

    col1, col2, col3, col4 = st.columns(4)

    # Calculate metrics
    rewards = [t for t in filtered_transactions if
               t.get('type') in ['reward', 'manual_reward', 'community_reward', 'incentive', 'ai_bonus']]
    violations = [t for t in filtered_transactions if t.get('type') in ['fine', 'warning', 'penalty']]

    with col1:
        st.metric("Total Rewards", len(rewards))

    with col2:
        st.metric("Total Violations", len(violations))

    with col3:
        total_points = sum([r.get('amount', 0) for r in rewards])
        st.metric("Points Awarded", total_points)

    with col4:
        total_fines = sum([v.get('amount', 0) for v in violations if v.get('amount', 0) > 0])
        st.metric("Fines Collected", f"₹{total_fines}")

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        # Transaction type distribution
        type_counts = {}
        for transaction in filtered_transactions:
            t_type = transaction.get('type', 'unknown')
            type_counts[t_type] = type_counts.get(t_type, 0) + 1

        if type_counts:
            import plotly.express as px
            fig_types = px.pie(values=list(type_counts.values()),
                               names=list(type_counts.keys()),
                               title='Transaction Type Distribution')
            st.plotly_chart(fig_types, use_container_width=True)

    with col2:
        # Daily trend
        daily_data = {}
        for transaction in filtered_transactions:
            date_key = transaction.get('created_at', '')[:10]
            if date_key not in daily_data:
                daily_data[date_key] = {'rewards': 0, 'violations': 0}

            if transaction.get('type') in ['reward', 'manual_reward', 'community_reward', 'incentive', 'ai_bonus']:
                daily_data[date_key]['rewards'] += 1
            else:
                daily_data[date_key]['violations'] += 1

        if daily_data:
            df_daily = pd.DataFrame.from_dict(daily_data, orient='index').reset_index()
            df_daily.columns = ['Date', 'Rewards', 'Violations']
            df_daily['Date'] = pd.to_datetime(df_daily['Date'])

            fig_daily = px.line(df_daily, x='Date', y=['Rewards', 'Violations'],
                                title='Daily Rewards vs Violations')
            st.plotly_chart(fig_daily, use_container_width=True)

    # Performance metrics by category
    st.subheader("📈 Performance Metrics")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏆 Top Performing Categories")

        # Reward categories
        reward_categories = {}
        for reward in rewards:
            category = reward.get('type', 'unknown')
            if category not in reward_categories:
                reward_categories[category] = {'count': 0, 'points': 0}

            reward_categories[category]['count'] += 1
            reward_categories[category]['points'] += reward.get('amount', 0)

        for category, data in sorted(reward_categories.items(), key=lambda x: x[1]['points'], reverse=True):
            st.write(f"**{category.title()}**: {data['count']} rewards, {data['points']} points")

    with col2:
        st.subheader("⚠️ Violation Analysis")

        # Violation severity
        violation_severity = {'high': 0, 'medium': 0, 'low': 0}
        for violation in violations:
            severity = violation.get('severity', 'low')
            violation_severity[severity] += 1

        for severity, count in violation_severity.items():
            st.write(f"**{severity.title()} Severity**: {count} violations")

        # Payment status for fines
        fines = [v for v in violations if v.get('type') == 'fine']
        if fines:
            paid_fines = len([f for f in fines if f.get('payment_status') == 'paid'])
            pending_fines = len([f for f in fines if f.get('payment_status') == 'pending'])

            st.write(f"**Paid Fines**: {paid_fines}")
            st.write(f"**Pending Fines**: {pending_fines}")

            if len(fines) > 0:
                collection_rate = (paid_fines / len(fines)) * 100
                st.metric("Collection Rate", f"{collection_rate:.1f}%")

    # Trends and insights
    st.subheader("📊 Trends & Insights")

    # Monthly comparison
    current_month = datetime.now().strftime('%Y-%m')
    previous_month = (datetime.now() - timedelta(days=30)).strftime('%Y-%m')

    current_rewards = len([r for r in rewards if r.get('created_at', '').startswith(current_month)])
    previous_rewards = len([r for r in transactions if r.get('created_at', '').startswith(previous_month)
                            and r.get('type') in ['reward', 'manual_reward', 'community_reward', 'incentive',
                                                  'ai_bonus']])

    current_violations = len([v for v in violations if v.get('created_at', '').startswith(current_month)])
    previous_violations = len([v for v in transactions if v.get('created_at', '').startswith(previous_month)
                               and v.get('type') in ['fine', 'warning', 'penalty']])

    col1, col2 = st.columns(2)

    with col1:
        reward_change = current_rewards - previous_rewards
        st.metric("Monthly Rewards", current_rewards, delta=reward_change)

    with col2:
        violation_change = current_violations - previous_violations
        st.metric("Monthly Violations", current_violations, delta=violation_change)

    # Insights
    st.subheader("💡 Key Insights")

    insights = []

    # Reward vs violation ratio
    if len(violations) > 0:
        reward_ratio = len(rewards) / len(violations)
        if reward_ratio > 2:
            insights.append("🟢 Excellent compliance: Rewards significantly outnumber violations")
        elif reward_ratio > 1:
            insights.append("🟡 Good compliance: More rewards than violations")
        else:
            insights.append("🔴 Poor compliance: Violations exceed rewards")

    # Fine collection efficiency
    fines = [v for v in violations if v.get('type') == 'fine' and v.get('amount', 0) > 0]
    if fines:
        paid_fines = [f for f in fines if f.get('payment_status') == 'paid']
        collection_rate = len(paid_fines) / len(fines) * 100

        if collection_rate > 80:
            insights.append("🟢 High fine collection rate - Good enforcement")
        elif collection_rate > 60:
            insights.append("🟡 Moderate fine collection rate - Room for improvement")
        else:
            insights.append("🔴 Low fine collection rate - Enhanced follow-up needed")

    # Community engagement
    community_rewards = [r for r in rewards if r.get('type') == 'community_reward']
    if len(community_rewards) > len(rewards) * 0.3:
        insights.append("🟢 High community engagement in waste reporting")
    elif len(community_rewards) > 0:
        insights.append("🟡 Moderate community participation - Encourage more reporting")
    else:
        insights.append("🔴 Low community engagement - Need awareness campaigns")

    for insight in insights:
        st.info(insight)

    # Export analytics
    if st.button("📥 Export Analytics Report"):
        analytics_data = {
            'summary': {
                'date_range': f"{start_date} to {end_date}",
                'total_transactions': len(filtered_transactions),
                'total_rewards': len(rewards),
                'total_violations': len(violations),
                'points_awarded': sum([r.get('amount', 0) for r in rewards]),
                'fines_collected': sum([v.get('amount', 0) for v in violations if v.get('amount', 0) > 0])
            },
            'type_distribution': type_counts,
            'daily_trends': daily_data,
            'reward_categories': reward_categories,
            'violation_severity': violation_severity,
            'insights': insights
        }

        analytics_json = json.dumps(analytics_data, indent=2, default=str)

        st.download_button(
            label="Download Analytics Report (JSON)",
            data=analytics_json,
            file_name=f"rewards_fines_analytics_{start_date}_{end_date}.json",
            mime="application/json"
        )
