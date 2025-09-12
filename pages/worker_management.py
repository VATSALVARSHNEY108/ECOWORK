import streamlit as st
import pandas as pd
from datetime import datetime, date
import base64
from utils.database import add_record, get_records, update_record
from utils.ai_verification import verify_safety_kit_photo
from utils.qr_generator import create_worker_qr, display_qr_code


def show():
    st.title("👷 Worker Management System")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Worker Registration", "Safety Kit Distribution", "Worker Records", "Training & Verification"])

    with tab1:
        worker_registration()

    with tab2:
        safety_kit_distribution()

    with tab3:
        worker_records()

    with tab4:
        training_verification()


def worker_registration():
    st.subheader("👷 Register New Worker")

    st.info(
        "💡 **Note**: All workers must complete mandatory training before starting their job and receive safety kits.")

    with st.form("worker_registration"):
        col1, col2 = st.columns(2)

        with col1:
            worker_name = st.text_input("Worker Name*", placeholder="Full name")
            worker_id_number = st.text_input("ID Number*", placeholder="Government ID number")
            contact_number = st.text_input("Contact Number*", placeholder="10-digit mobile number")
            email = st.text_input("Email Address", placeholder="Optional email")
            date_of_birth = st.date_input("Date of Birth*", max_value=date.today())

        with col2:
            address = st.text_area("Address*", placeholder="Complete residential address")
            job_type = st.selectbox("Job Type*",
                                    ["Waste Collector", "Vehicle Driver", "Sorting Facility Worker",
                                     "Supervisor", "Safety Inspector"])
            employment_type = st.selectbox("Employment Type",
                                           ["Full-time", "Part-time", "Contract", "Temporary"])
            supervisor_name = st.text_input("Supervisor Name", placeholder="Direct supervisor")
            vehicle_assigned = st.text_input("Vehicle Assigned", placeholder="Vehicle number if applicable")

        # Emergency contact
        st.subheader("🆘 Emergency Contact")
        col1, col2 = st.columns(2)
        with col1:
            emergency_contact_name = st.text_input("Emergency Contact Name*")
            emergency_relationship = st.text_input("Relationship*", placeholder="e.g., Spouse, Father, etc.")
        with col2:
            emergency_contact_number = st.text_input("Emergency Contact Number*")
            emergency_address = st.text_input("Emergency Contact Address")

        # Medical information
        st.subheader("🏥 Medical Information")
        medical_conditions = st.text_area("Medical Conditions",
                                          placeholder="Any known medical conditions or allergies")
        medications = st.text_area("Current Medications",
                                   placeholder="List of current medications")

        # Work preferences
        shift_preference = st.selectbox("Shift Preference",
                                        ["Morning (6 AM - 2 PM)", "Afternoon (2 PM - 10 PM)",
                                         "Night (10 PM - 6 AM)", "Flexible"])

        # Document uploads (simulated)
        st.subheader("📄 Document Upload")
        id_proof = st.file_uploader("ID Proof*", type=['png', 'jpg', 'jpeg', 'pdf'])
        address_proof = st.file_uploader("Address Proof", type=['png', 'jpg', 'jpeg', 'pdf'])
        medical_certificate = st.file_uploader("Medical Fitness Certificate*", type=['png', 'jpg', 'jpeg', 'pdf'])

        submitted = st.form_submit_button("👷 Register Worker")

        if submitted:
            if (worker_name and worker_id_number and contact_number and date_of_birth and
                    address and job_type and emergency_contact_name and emergency_relationship and
                    emergency_contact_number and id_proof and medical_certificate):

                worker_record = {
                    'worker_name': worker_name,
                    'worker_id_number': worker_id_number,
                    'contact_number': contact_number,
                    'email': email,
                    'date_of_birth': str(date_of_birth),
                    'address': address,
                    'job_type': job_type,
                    'employment_type': employment_type,
                    'supervisor_name': supervisor_name,
                    'vehicle_assigned': vehicle_assigned,
                    'emergency_contact_name': emergency_contact_name,
                    'emergency_relationship': emergency_relationship,
                    'emergency_contact_number': emergency_contact_number,
                    'emergency_address': emergency_address,
                    'medical_conditions': medical_conditions,
                    'medications': medications,
                    'shift_preference': shift_preference,
                    'status': 'registered',
                    'training_completed': False,
                    'safety_kit_received': False,
                    'qr_generated': False,
                    'documents_uploaded': True,
                    'registration_date': datetime.now().isoformat()
                }

                record = add_record('workers', worker_record)

                # Generate worker QR code
                qr_img = create_worker_qr(record['id'], worker_name)
                if qr_img:
                    update_record('workers', record['id'], {'qr_generated': True})

                st.success(f"✅ Worker registered successfully! Worker ID: {record['id']}")

                if qr_img:
                    st.subheader("📱 Worker QR Code")
                    display_qr_code(qr_img, f"Worker QR - {worker_name}")

                st.info("""
                📋 **Next Steps**:
                1. Worker must complete mandatory training
                2. Safety kit distribution with photo verification
                3. Final verification before job assignment
                """)
            else:
                st.error("❌ Please fill in all required fields and upload necessary documents")


def safety_kit_distribution():
    st.subheader("🦺 Safety Kit Distribution & Verification")

    # Get workers who need safety kits
    workers = get_records('workers', {'safety_kit_received': False, 'status': 'registered'})

    if not workers:
        st.info("👷 No workers pending safety kit distribution.")
        return

    # Select worker
    worker_options = [f"{w['worker_name']} - {w['job_type']} (ID: {w['id']})" for w in workers]
    worker_options.insert(0, "Select worker for safety kit distribution")

    selected_worker = st.selectbox("👷 Select Worker", worker_options)

    if selected_worker and selected_worker != "Select worker for safety kit distribution":
        worker_id = selected_worker.split("ID: ")[1].split(")")[0]
        worker = next((w for w in workers if w['id'] == int(worker_id)), None)

        if worker:
            st.info(f"📋 **Worker**: {worker['worker_name']} - {worker['job_type']}")

            with st.form("safety_kit_distribution"):
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("🦺 Safety Kit Items")

                    # Standard safety items
                    safety_items = {
                        'safety_gloves': st.checkbox("Safety Gloves", value=True),
                        'face_masks': st.checkbox("Face Masks/Respirators", value=True),
                        'safety_goggles': st.checkbox("Safety Goggles", value=True),
                        'protective_clothing': st.checkbox("Protective Clothing/Overalls", value=True),
                        'safety_boots': st.checkbox("Safety Boots", value=True),
                        'hard_hat': st.checkbox("Hard Hat/Helmet", value=True),
                        'high_vis_vest': st.checkbox("High Visibility Vest", value=True),
                        'first_aid_kit': st.checkbox("Personal First Aid Kit"),
                        'sanitizer': st.checkbox("Hand Sanitizer", value=True),
                        'safety_manual': st.checkbox("Safety Manual/Guidelines", value=True)
                    }

                    # Additional items based on job type
                    if worker.get('job_type') == 'Vehicle Driver':
                        safety_items['vehicle_safety_kit'] = st.checkbox("Vehicle Safety Kit")

                    kit_condition = st.selectbox("Kit Condition",
                                                 ["New", "Good", "Refurbished"])

                with col2:
                    st.subheader("📷 Photo Verification")

                    st.info(
                        "📸 **AI Verification**: Upload 1-2 photos showing the worker receiving the safety kit for fraud prevention.")

                    # Photo uploads
                    photo1 = st.file_uploader("Photo 1: Worker with Safety Kit*",
                                              type=['png', 'jpg', 'jpeg'], key="safety_photo1")
                    photo2 = st.file_uploader("Photo 2: Close-up of Safety Items",
                                              type=['png', 'jpg', 'jpeg'], key="safety_photo2")

                    distribution_date = st.date_input("Distribution Date", value=date.today())
                    distributor_name = st.text_input("Distributed By*", placeholder="Name of person distributing kit")

                    verification_notes = st.text_area("Verification Notes",
                                                      placeholder="Any observations or special notes")

                submitted = st.form_submit_button("🦺 Distribute Safety Kit")

                if submitted:
                    if photo1 and distributor_name and any(safety_items.values()):
                        # Convert photos to base64 for AI verification
                        try:
                            photo1_b64 = base64.b64encode(photo1.read()).decode()

                            # AI verification
                            st.info("🤖 Verifying photos with AI...")
                            verification_result = verify_safety_kit_photo(photo1_b64)

                            # Create safety kit record
                            kit_record = {
                                'worker_id': int(worker_id),
                                'worker_name': worker['worker_name'],
                                'safety_items': {k: v for k, v in safety_items.items() if v},
                                'kit_condition': kit_condition,
                                'distribution_date': str(distribution_date),
                                'distributor_name': distributor_name,
                                'verification_notes': verification_notes,
                                'photos_uploaded': 2 if photo2 else 1,
                                'ai_verification': verification_result,
                                'verification_status': 'verified' if verification_result.get(
                                    'verified') else 'needs_review',
                                'created_at': datetime.now().isoformat()
                            }

                            record = add_record('safety_kits', kit_record)

                            # Update worker record
                            update_record('workers', int(worker_id), {
                                'safety_kit_received': True,
                                'safety_kit_id': record['id'],
                                'status': 'kit_distributed'
                            })

                            st.success(f"✅ Safety kit distributed successfully! Record ID: {record['id']}")

                            # Show AI verification results
                            col1, col2 = st.columns(2)

                            with col1:
                                if verification_result.get('verified'):
                                    st.success("🤖 AI Verification: ✅ Photos verified successfully")
                                else:
                                    st.warning("🤖 AI Verification: ⚠️ Photos need manual review")

                            with col2:
                                confidence = verification_result.get('confidence', 0)
                                st.metric("AI Confidence", f"{confidence:.1%}")

                            # Show detected items
                            if verification_result.get('items_detected'):
                                st.write("🔍 **AI Detected Items**:",
                                         ', '.join(verification_result['items_detected']))

                            if verification_result.get('concerns'):
                                st.warning("⚠️ **AI Concerns**: " +
                                           ', '.join(verification_result['concerns']))

                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ Error processing photos: {str(e)}")

                    else:
                        st.error("❌ Please upload at least one photo, enter distributor name, and select safety items")


def worker_records():
    st.subheader("📋 Worker Records")

    workers = get_records('workers')

    if not workers:
        st.info("👷 No worker records found.")
        return

    # Filters
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        status_filter = st.selectbox("Filter by Status",
                                     ["All", "registered", "kit_distributed", "training_completed", "active",
                                      "inactive"])

    with col2:
        job_filter = st.selectbox("Filter by Job Type",
                                  ["All", "Waste Collector", "Vehicle Driver", "Sorting Facility Worker",
                                   "Supervisor", "Safety Inspector"])

    with col3:
        search_term = st.text_input("Search Worker", placeholder="Name or ID")

    with col4:
        safety_kit_filter = st.selectbox("Safety Kit Status", ["All", "Received", "Pending"])

    # Apply filters
    filtered_workers = workers

    if status_filter != "All":
        filtered_workers = [w for w in filtered_workers if w.get('status') == status_filter]

    if job_filter != "All":
        filtered_workers = [w for w in filtered_workers if w.get('job_type') == job_filter]

    if search_term:
        filtered_workers = [w for w in filtered_workers
                            if search_term.lower() in w.get('worker_name', '').lower()
                            or search_term in str(w.get('id', ''))]

    if safety_kit_filter == "Received":
        filtered_workers = [w for w in filtered_workers if w.get('safety_kit_received')]
    elif safety_kit_filter == "Pending":
        filtered_workers = [w for w in filtered_workers if not w.get('safety_kit_received')]

    # Statistics
    if filtered_workers:
        st.subheader("📊 Worker Statistics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Workers", len(filtered_workers))

        with col2:
            active_workers = len([w for w in filtered_workers if w.get('status') == 'active'])
            st.metric("Active Workers", active_workers)

        with col3:
            kit_received = len([w for w in filtered_workers if w.get('safety_kit_received')])
            st.metric("Safety Kits Distributed", kit_received)

        with col4:
            training_completed = len([w for w in filtered_workers if w.get('training_completed')])
            st.metric("Training Completed", training_completed)

    # Display worker records
    for worker in filtered_workers:
        status_icons = {
            'registered': '📝',
            'kit_distributed': '🦺',
            'training_completed': '🎓',
            'active': '✅',
            'inactive': '❌'
        }

        status_icon = status_icons.get(worker.get('status'), '❓')

        with st.expander(
                f"{status_icon} {worker.get('worker_name', 'Unknown')} - {worker.get('job_type', 'N/A')} (ID: {worker.get('id', 'N/A')})"):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**ID Number**: {worker.get('worker_id_number', 'N/A')}")
                st.write(f"**Contact**: {worker.get('contact_number', 'N/A')}")
                st.write(f"**Job Type**: {worker.get('job_type', 'N/A')}")
                st.write(f"**Employment Type**: {worker.get('employment_type', 'N/A')}")
                st.write(f"**Status**: {worker.get('status', 'Unknown').title()}")
                st.write(f"**Registration Date**: {worker.get('registration_date', 'N/A')[:10]}")

            with col2:
                st.write(f"**Supervisor**: {worker.get('supervisor_name', 'Not assigned')}")
                st.write(f"**Vehicle**: {worker.get('vehicle_assigned', 'Not assigned')}")
                st.write(f"**Shift**: {worker.get('shift_preference', 'N/A')}")
                st.write(f"**Training Completed**: {'✅ Yes' if worker.get('training_completed') else '❌ No'}")
                st.write(f"**Safety Kit**: {'✅ Received' if worker.get('safety_kit_received') else '❌ Pending'}")
                st.write(f"**QR Generated**: {'✅ Yes' if worker.get('qr_generated') else '❌ No'}")

            # Emergency contact
            if worker.get('emergency_contact_name'):
                st.write(
                    f"**Emergency Contact**: {worker.get('emergency_contact_name')} ({worker.get('emergency_relationship')}) - {worker.get('emergency_contact_number')}")

            # Update worker status
            new_status = st.selectbox(
                "Update Status",
                ["registered", "kit_distributed", "training_completed", "active", "inactive"],
                key=f"worker_status_{worker.get('id')}",
                index=["registered", "kit_distributed", "training_completed", "active", "inactive"].index(
                    worker.get('status', 'registered'))
            )

            if st.button(f"Update Status", key=f"update_worker_{worker.get('id')}"):
                update_record('workers', worker.get('id'), {'status': new_status})
                st.success(f"Worker status updated to {new_status}")
                st.rerun()


def training_verification():
    st.subheader("🎓 Worker Training & Verification")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📚 Training Modules for Workers")

        st.markdown("""
        ### 🎯 Mandatory Training Curriculum

        #### Module 1: Safety Protocols
        - Personal protective equipment (PPE) usage
        - Hazardous waste handling procedures
        - Emergency response protocols
        - First aid basics

        #### Module 2: Waste Classification
        - Identifying different waste types
        - Proper segregation techniques
        - Contamination prevention
        - Special waste handling

        #### Module 3: Collection Procedures
        - QR code scanning and data entry
        - Route optimization
        - Customer interaction protocols
        - Quality assessment techniques

        #### Module 4: Vehicle & Equipment Safety
        - Vehicle inspection procedures
        - Equipment maintenance
        - Load securing techniques
        - Traffic safety rules

        #### Module 5: Documentation & Reporting
        - Digital form completion
        - Photo documentation
        - Incident reporting
        - Performance metrics
        """)

    with col2:
        st.subheader("✅ Training Completion")

        # Get workers who need training
        workers = get_records('workers', {'training_completed': False})

        if workers:
            worker_options = [f"{w['worker_name']} - {w['job_type']} (ID: {w['id']})" for w in workers]
            worker_options.insert(0, "Select worker for training completion")

            selected_worker = st.selectbox("👷 Mark Training Complete", worker_options)

            if selected_worker and selected_worker != "Select worker for training completion":
                worker_id = selected_worker.split("ID: ")[1].split(")")[0]

                with st.form("training_completion"):
                    training_date = st.date_input("Training Completion Date", value=date.today())
                    trainer_name = st.text_input("Trainer Name*", placeholder="Name of trainer")
                    training_duration = st.number_input("Training Duration (hours)",
                                                        min_value=1.0, max_value=40.0, value=8.0, step=0.5)

                    # Training modules completed
                    st.subheader("📋 Modules Completed")
                    modules = {
                        'safety_protocols': st.checkbox("Safety Protocols", value=True),
                        'waste_classification': st.checkbox("Waste Classification", value=True),
                        'collection_procedures': st.checkbox("Collection Procedures", value=True),
                        'vehicle_safety': st.checkbox("Vehicle & Equipment Safety", value=True),
                        'documentation': st.checkbox("Documentation & Reporting", value=True)
                    }

                    assessment_score = st.slider("Assessment Score (%)", 0, 100, 85)
                    training_notes = st.text_area("Training Notes",
                                                  placeholder="Training observations and additional notes")

                    submitted = st.form_submit_button("🎓 Mark Training Complete")

                    if submitted:
                        if trainer_name and assessment_score >= 70:  # Minimum passing score
                            # Create training record
                            training_record = {
                                'worker_id': int(worker_id),
                                'worker_name': next(w['worker_name'] for w in workers if w['id'] == int(worker_id)),
                                'training_date': str(training_date),
                                'trainer_name': trainer_name,
                                'training_duration': training_duration,
                                'modules_completed': {k: v for k, v in modules.items() if v},
                                'assessment_score': assessment_score,
                                'training_notes': training_notes,
                                'completion_status': 'passed',
                                'created_at': datetime.now().isoformat()
                            }

                            record = add_record('worker_training', training_record)

                            # Update worker record
                            update_record('workers', int(worker_id), {
                                'training_completed': True,
                                'training_record_id': record['id'],
                                'status': 'training_completed'
                            })

                            st.success(f"✅ Training completion recorded! Record ID: {record['id']}")
                            st.info("📋 Worker can now be marked as active and assigned to collection routes.")
                            st.rerun()

                        else:
                            if assessment_score < 70:
                                st.error("❌ Assessment score must be at least 70% to pass")
                            else:
                                st.error("❌ Please enter trainer name")
        else:
            st.info("🎓 All registered workers have completed their training.")

    # Training records
    st.subheader("📋 Training Records")

    training_records = get_records('worker_training', {})

    if training_records:
        for record in training_records[-10:]:  # Show last 10 records
            with st.expander(f"🎓 {record.get('worker_name', 'Unknown')} - Score: {record.get('assessment_score', 0)}%"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Training Date**: {record.get('training_date', 'N/A')}")
                    st.write(f"**Trainer**: {record.get('trainer_name', 'N/A')}")
                    st.write(f"**Duration**: {record.get('training_duration', 0)} hours")
                    st.write(f"**Assessment Score**: {record.get('assessment_score', 0)}%")

                with col2:
                    modules_completed = record.get('modules_completed', {})
                    st.write("**Modules Completed**:")
                    for module, completed in modules_completed.items():
                        if completed:
                            st.write(f"  ✅ {module.replace('_', ' ').title()}")

                if record.get('training_notes'):
                    st.write(f"**Notes**: {record.get('training_notes')}")
    else:
        st.info("📝 No training records found.")
