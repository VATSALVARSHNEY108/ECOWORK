import qrcode
import base64
from io import BytesIO
from PIL import Image
import streamlit as st
import pandas as pd


def generate_qr_code(data, size=10, border=4):
    """Generate QR code for given data"""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        return img
    except Exception as e:
        st.error(f"Error generating QR code: {str(e)}")
        return None


def qr_to_base64(qr_img):
    """Convert QR code image to base64 string"""
    try:
        buffer = BytesIO()
        qr_img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return img_str
    except Exception as e:
        st.error(f"Error converting QR to base64: {str(e)}")
        return None


def create_household_qr(family_id, family_name, address):
    """Create QR code for household with embedded information"""
    qr_data = {
        "type": "household",
        "family_id": family_id,
        "family_name": family_name,
        "address": address,
        "generated_at": str(pd.Timestamp.now())
    }

    # Convert to JSON string for QR code
    import json
    qr_string = json.dumps(qr_data)

    return generate_qr_code(qr_string)


def create_worker_qr(worker_id, worker_name):
    """Create QR code for waste worker"""
    qr_data = {
        "type": "worker",
        "worker_id": worker_id,
        "worker_name": worker_name,
        "generated_at": str(pd.Timestamp.now())
    }

    import json
    qr_string = json.dumps(qr_data)

    return generate_qr_code(qr_string)


def parse_qr_data(qr_string):
    """Parse QR code data back to dictionary"""
    try:
        import json
        return json.loads(qr_string)
    except:
        return {"type": "unknown", "data": qr_string}


def display_qr_code(qr_img, title="QR Code"):
    """Display QR code in Streamlit"""
    if qr_img:
        st.image(qr_img, caption=title, width=300)

        # Convert to downloadable format
        buffer = BytesIO()
        qr_img.save(buffer, format="PNG")

        st.download_button(
            label="📥 Download QR Code",
            data=buffer.getvalue(),
            file_name=f"{title.lower().replace(' ', '_')}.png",
            mime="image/png"
        )
