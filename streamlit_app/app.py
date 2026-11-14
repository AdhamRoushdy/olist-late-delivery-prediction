
import streamlit as st
import pandas as pd
import joblib
from pathlib import Path

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Late Delivery Predictor",
    page_icon="📦",
    layout="wide"
)

# ==========================================
# 2. CUSTOM UI STYLING
# ==========================================

st.markdown("""
<style>

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

h1 {
    font-size: 2.5rem !important;
    font-weight: 800 !important;
    letter-spacing: -1px;
}

h2, h3 {
    font-weight: 700 !important;
}

div[data-baseweb="input"] input {
    border-radius: 8px;
}

div.stFormSubmitButton > button {
    border-radius: 10px;
    height: 48px;
    font-weight: 700;
    background: #2563eb;
    color: white;
    border: none;
    transition: 0.2s;
}

div.stFormSubmitButton > button:hover {
    background: #1d4ed8;
    color: white;
    border: none;
}

hr {
    margin-top: 1.5rem;
    margin-bottom: 1.5rem;
    border-color: rgba(128,128,128,0.2);
}

div[data-testid="stAlert"] {
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. LOAD MODEL
# ==========================================

MODEL_PATH = Path(__file__).parent / "xgb_model_v3.pkl"

@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)

model = load_model()

THRESHOLD = 0.65


# ==========================================
# 4. APP HEADER
# ==========================================


st.markdown("""
<div style="
    font-size:14px;
    color:#3b82f6;
    font-weight:700;
    letter-spacing:2px;
">
    E-COMMERCE INTELLIGENCE
</div>

<h1 style="margin:5px 0 8px 0;">
    📦 Late Delivery Predictor
</h1>

<p style="color:gray; font-size:16px;">
    AI-powered delivery risk assessment system
</p>
""", unsafe_allow_html=True)


st.info(
    "📌 Enter the order details below to analyze "
    "its potential late-delivery risk."
)


# ==========================================
# 5. INPUT FORM
# ==========================================

with st.form("prediction_form"):

    # --------------------------------------
    # PURCHASE INFORMATION
    # --------------------------------------

    st.subheader("📅 Purchase Information")

    col1, col2, col3 = st.columns(3)

    with col1:
        purchase_year = st.number_input(
            "Purchase Year",
            min_value=2016,
            max_value=2030,
            value=2018,
            step=1
        )

        purchase_month = st.number_input(
            "Purchase Month",
            min_value=1,
            max_value=12,
            value=5
        )

    with col2:
        purchase_day = st.number_input(
            "Purchase Day",
            min_value=1,
            max_value=31,
            value=15
        )

        purchase_hour = st.number_input(
            "Purchase Hour",
            min_value=0,
            max_value=23,
            value=12
        )

    with col3:
        purchase_day_of_week = st.number_input(
            "Day of Week (Monday=0, Sunday=6)",
            min_value=0,
            max_value=6,
            value=2
        )

    st.divider()

    # --------------------------------------
    # ORDER INFORMATION
    # --------------------------------------

    st.subheader("🛒 Order Information")

    col1, col2, col3 = st.columns(3)

    with col1:
        total_items = st.number_input(
            "Total Items",
            min_value=1,
            value=1
        )

        total_price = st.number_input(
            "Total Price",
            min_value=0.0,
            value=100.0
        )

        avg_item_price = st.number_input(
            "Average Item Price",
            min_value=0.0,
            value=100.0
        )

    with col2:
        total_freight = st.number_input(
            "Total Freight",
            min_value=0.0,
            value=20.0
        )

        unique_sellers = st.number_input(
            "Unique Sellers",
            min_value=1,
            value=1
        )

    with col3:
        total_payment = st.number_input(
            "Total Payment",
            min_value=0.0,
            value=120.0
        )

        payment_installments = st.number_input(
            "Payment Installments",
            min_value=0,
            value=1
        )

    st.divider()

    # --------------------------------------
    # PAYMENT INFORMATION
    # --------------------------------------

    st.subheader("💳 Payment Information")

    col1, col2 = st.columns(2)

    with col1:
        payment_types = st.number_input(
            "Number of Payment Types",
            min_value=0,
            value=1
        )

    with col2:
        payment_records = st.number_input(
            "Number of Payment Records",
            min_value=0,
            value=1
        )

    st.divider()

    # --------------------------------------
    # PRODUCT INFORMATION
    # --------------------------------------

    st.subheader("📦 Product Information")

    col1, col2, col3 = st.columns(3)

    with col1:
        avg_product_weight_g = st.number_input(
            "Average Product Weight (g)",
            min_value=0.0,
            value=500.0
        )

        total_product_weight_g = st.number_input(
            "Total Product Weight (g)",
            min_value=0.0,
            value=500.0
        )

    with col2:
        avg_product_volume_cm3 = st.number_input(
            "Average Product Volume (cm³)",
            min_value=0.0,
            value=1000.0
        )

        total_product_volume_cm3 = st.number_input(
            "Total Product Volume (cm³)",
            min_value=0.0,
            value=1000.0
        )

    with col3:
        avg_product_photos_qty = st.number_input(
            "Average Product Photos",
            min_value=0.0,
            value=3.0
        )

        product_categories = st.number_input(
            "Number of Product Categories",
            min_value=1,
            value=1
        )

    st.divider()

    # --------------------------------------
    # CUSTOMER INFORMATION
    # --------------------------------------

    st.subheader("📍 Customer Information")

    brazilian_states = [
        "AC", "AL", "AP", "AM", "BA", "CE", "DF",
        "ES", "GO", "MA", "MT", "MS", "MG", "PA",
        "PB", "PR", "PE", "PI", "RJ", "RN", "RS",
        "RO", "RR", "SC", "SP", "SE", "TO"
    ]

    col1, col2, col3 = st.columns(3)

    with col1:
        customer_zip_code_prefix = st.number_input(
            "Customer ZIP Code Prefix",
            min_value=0,
            max_value=99999,
            value=1000
        )

    with col2:
        customer_city = st.text_input(
            "Customer City",
            placeholder="e.g. sao paulo"
        )

    with col3:
        customer_state = st.selectbox(
            "Customer State",
            brazilian_states,
            index=brazilian_states.index("SP")
        )

    st.divider()

    # --------------------------------------
    # SHIPPING DISTANCE
    # --------------------------------------

    st.subheader("🚚 Shipping Distance")

    col1, col2 = st.columns(2)

    with col1:
        avg_distance_km = st.number_input(
            "Average Distance (km)",
            min_value=0.0,
            value=400.0
        )

    with col2:
        max_distance_km = st.number_input(
            "Maximum Distance (km)",
            min_value=0.0,
            value=400.0
        )

    st.divider()

    predict_button = st.form_submit_button(
        "🔍 Predict Delivery Risk",
        use_container_width=True
    )


# ==========================================
# 6. PREDICTION
# ==========================================

if predict_button:

    if not customer_city.strip():

        st.error("Please enter the customer city.")

    else:

        input_data = pd.DataFrame([{

            "purchase_year": purchase_year,
            "purchase_month": purchase_month,
            "purchase_day": purchase_day,
            "purchase_hour": purchase_hour,
            "purchase_day_of_week": purchase_day_of_week,

            "total_items": total_items,
            "total_price": total_price,
            "total_freight": total_freight,
            "avg_item_price": avg_item_price,
            "unique_sellers": unique_sellers,

            "total_payment": total_payment,
            "payment_installments": payment_installments,
            "payment_types": payment_types,
            "payment_records": payment_records,

            "avg_product_weight_g": avg_product_weight_g,
            "total_product_weight_g": total_product_weight_g,
            "avg_product_volume_cm3": avg_product_volume_cm3,
            "total_product_volume_cm3": total_product_volume_cm3,
            "avg_product_photos_qty": avg_product_photos_qty,
            "product_categories": product_categories,

            "customer_zip_code_prefix": customer_zip_code_prefix,
            "customer_city": customer_city.strip().lower(),
            "customer_state": customer_state,

            "avg_distance_km": avg_distance_km,
            "max_distance_km": max_distance_km

        }])

        # Exact feature order used during training
        expected_features = (
            model.named_steps["preprocessor"].feature_names_in_
        )

        input_data = input_data[list(expected_features)]

        # Model prediction
        risk_score = float(
            model.predict_proba(input_data)[0, 1]
        )

        prediction = int(risk_score >= THRESHOLD)

        risk_percent = risk_score * 100

        # ----------------------------------
        # RESULT STATUS
        # ----------------------------------

        if prediction == 1:

            status = "HIGH RISK"
            color = "#ef4444"
            background = "#3b1717"
            message = (
                "This order has a high predicted risk "
                "of late delivery."
            )
            icon = "⚠️"

        else:

            status = "LOWER RISK"
            color = "#22c55e"
            background = "#153323"
            message = (
                "This order has a lower predicted risk "
                "of late delivery."
            )
            icon = "✓"

        # ----------------------------------
        # RESULT CARD
        # ----------------------------------

        st.divider()

        st.subheader("📊 Prediction Result")

        with st.container(border=True):

            col1, col2 = st.columns([2, 1])

            with col1:

                st.markdown(
                    f"""
                    <p style="
                        color:gray;
                        margin-bottom:0;
                        font-size:15px;
                    ">
                        Estimated Late-Delivery Risk Score
                    </p>

                    <h1 style="
                        color:{color};
                        font-size:48px;
                        margin-top:0;
                    ">
                        {risk_percent:.2f}%
                    </h1>
                    """,
                    unsafe_allow_html=True
                )

            with col2:

                st.markdown(
                    f"""
                    <div style="
                        background:{background};
                        color:{color};
                        padding:14px;
                        border-radius:12px;
                        text-align:center;
                        font-weight:800;
                        margin-top:15px;
                    ">
                        {icon} {status}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.progress(risk_score)

            st.markdown(
    f"""
    <div style="
        background:{background};
        padding:15px;
        border-radius:10px;
        margin-top:15px;
    ">
        <span style="color:{color}; font-weight:700;">
            {status}
        </span>

    </div>
    """,
    unsafe_allow_html=True
)