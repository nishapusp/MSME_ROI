import streamlit as st
import uuid

# === Constants ===
DEFAULT_EBLR = 8.25  # Default External Benchmark Lending Rate

# Spreads for MSME loans <= ₹50 Lakh (Annexure I, Table A)
msme_spread_table_a = {
    "Up to ₹50,000": 1.50,
    "₹50,000 to ₹2 Lakh": 1.75,
    "₹2 Lakh to ₹10 Lakh": 2.75,
    "₹10 Lakh to ₹50 Lakh": 2.25
}

# Spreads for MSME loans > ₹50 Lakh to ₹5 Crore (Annexure I, Table B)
msme_spread_table_b = {
    "CR1": 0.50,
    "CR2": 0.75,
    "CR3": 1.75,
    "CR4": 2.00,
    "CR5": 3.50,
    "CR6": 6.85,
    "CR7": 6.95,
    "CR8-CR10": 7.05
}

# Spreads for MSME loans > ₹5 Crore (Annexure I, Table C)
msme_spread_table_c = {
    "> ₹5 Crore to ≤ ₹25 Crore": {
        "CR1": 1.30,
        "CR2": 1.55,
        "CR3": 2.00,
        "CR4": 3.00,
        "CR5": 4.90,
        "CR6": 5.75,
        "CR7": 5.85,
        "CR8-CR10": 5.95
    },
    "> ₹25 Crore": {
        "CR1": {"AAA": 0.55, "AA": 0.80, "A": 1.05, "BBB": 1.50, "BB & Below": 2.80, "Unrated": 1.70, "A1+": 0.55, "A1": 0.80, "A2": 1.05, "A3": 1.50},
        "CR2": {"AAA": 0.60, "AA": 0.90, "A": 1.20, "BBB": 1.65, "BB & Below": 2.95, "Unrated": 1.85, "A1+": 0.60, "A1": 0.90, "A2": 1.20, "A3": 1.65},
        "CR3": {"AAA": 0.70, "AA": 1.10, "A": 1.50, "BBB": 1.95, "BB & Below": 3.25, "Unrated": 2.15, "A1+": 0.70, "A1": 1.10, "A2": 1.50, "A3": 1.95},
        "CR4": {"AAA": 0.75, "AA": 1.35, "A": 2.00, "BBB": 2.45, "BB & Below": 3.70, "Unrated": 2.65, "A1+": 0.75, "A1": 1.35, "A2": 2.00, "A3": 2.45},
        "CR5": {"AAA": 2.45, "AA": 2.70, "A": 2.95, "BBB": 3.40, "BB & Below": 4.65, "Unrated": 3.60, "A1+": 2.45, "A1": 2.70, "A2": 2.95, "A3": 3.40},
        "CR6": {"AAA": 3.15, "AA": 3.35, "A": 3.65, "BBB": 4.10, "BB & Below": 5.30, "Unrated": 4.30, "A1+": 3.15, "A1": 3.35, "A2": 3.65, "A3": 4.10},
        "CR7": {"AAA": 3.25, "AA": 3.45, "A": 3.75, "BBB": 4.20, "BB & Below": 5.40, "Unrated": 4.40, "A1+": 3.25, "A1": 3.45, "A2": 3.75, "A3": 4.20},
        "CR8-CR10": {"AAA": 3.35, "AA": 3.55, "A": 3.85, "BBB": 4.30, "BB & Below": 5.50, "Unrated": 4.50, "A1+": 3.35, "A1": 3.55, "A2": 3.85, "A3": 4.30}
    }
}

# Additional Credit Risk Premium for Term Loans > ₹25 Lakh (Annexure I, Table D)
additional_credit_risk_premium = {
    ">1 to 3 years": 0.10,
    ">3 to 5 years": 0.25,
    ">5 to 10 years": 0.50,
    ">10 years": 1.00
}

# Collateral-based concessions (Annexure I, Table E)
collateral_concession = {
    "<50%": 0.00,
    "50% to <75%": 0.00,
    "75% to <100%": 0.10,
    "100% to <150%": 0.25,
    "150% and above": 0.50
}

# Union MSME Suvidha spreads (Annexure II, Page 21)
suvidha_spreads = {
    "₹10 Lakh to ₹50 Lakh": {
        "75% to <100%": 1.35,
        "100% and above": 1.25
    },
    "₹50 Lakh to ₹5 Crore": {
        "CR1": [0.40, 0.25, 0.20],
        "CR2": [0.50, 0.40, 0.30],
        "CR3": [0.60, 0.45, 0.35],
        "CR4": [0.65, 0.50, 0.40],
        "CR5": [1.15, 1.00, 0.70]
    },
    "> ₹5 Crore": {
        "CR1": [0.45, 0.70],
        "CR2": [0.55, 0.85],
        "CR3": [0.70, 0.95],
        "CR4": [0.85, 1.05],
        "CR5": [1.45, 1.55]
    }
}

# Union LAP spreads (Annexure II, Page 16)
union_lap_spreads = {
    "Up to ₹25 Lakh": 2.25,
    "₹25 Lakh to ₹50 Lakh": 2.25,
    "> ₹50 Lakh": {
        "CR1": {"Micro": 2.00, "Medium": 2.50},
        "CR2": {"Micro": 2.00, "Medium": 2.50},
        "CR3": {"Micro": 2.00, "Medium": 2.50},
        "CR4": {"Micro": 2.25, "Medium": 2.75},
        "CR5": {"Micro": 2.75, "Medium": 3.25}
    }
}

# Schemes where card rates (Tables A, B, C) are used
CARD_RATE_SCHEMES = {
    "General MSME Loans": {"all": True},
    "Union Nari Shakti": {">50": True},
    "Union MSME Superfast": {">50": True},
    "Union Parivahan": {"all": True},
    "Union Progress": {"all": True},
    "Union Mudra": {"all": True},
    "Union Turnover Plus": {"all": True},
    "Union Ayushman Plus": {">2500": True},
    "Union Solar": {">50": True},
    "Union Equipment Finance": {">50": True},
    "Union Contractor": {">50": True},
    "Union Rent": {">50": True}
}

# Schemes where Table D tenor premium does not apply
NO_TENOR_PREMIUM_SCHEMES = [
    "Union LAP",
    "Union Ayushman Plus",
    "Union Turnover Plus"
]

# === Streamlit UI ===
st.title("MSME Loan ROI Calculator")

# Basic Inputs with Validation
eblr = st.number_input("Enter EBLR (%)", value=DEFAULT_EBLR, step=0.01, min_value=0.0)
if eblr <= 0:
    st.warning("EBLR should be a positive value.")
amount = st.number_input("Enter Loan Amount in ₹ Lakhs", min_value=0.01, step=0.1)
if amount <= 0:
    st.warning("Loan amount must be positive.")

# Scheme selection
schemes = [
    "General MSME Loans", "Union Nari Shakti", "Union MSME Superfast", "Union MSME Suvidha",
    "Union Parivahan", "Union Turnover Plus", "Union Ayushman Plus", "Union Progress",
    "Union Mudra", "Union LAP", "Union Solar", "Union Equipment Finance",
    "Union Contractor", "Union Rent"
]
if amount <= 10:
    scheme = "General MSME Loans"
    st.warning("Loan amount must be > ₹10 Lakh to select specific schemes like Union MSME Suvidha. Using General MSME rates.")
else:
    scheme = st.selectbox("Select Scheme", schemes)

# Loan type
loan_type_options = (
    ["Cash Credit", "Term Loan", "Overdraft"] if scheme == "Union MSME Suvidha" else
    ["Term Loan", "Overdraft"] if scheme == "Union LAP" else
    ["Cash Credit/Working Capital"] if scheme == "Union MSME Superfast" else
    ["Cash Credit/Working Capital", "Term Loan"]
)
loan_type = st.selectbox("Select Loan Type", loan_type_options)

# Security type
security_options = (
    ["Collateral Security Available", "CGTMSE"] if scheme in [
        "General MSME Loans", "Union Nari Shakti", "Union Parivahan", "Union Progress",
        "Union Mudra", "Union Turnover Plus", "Union Ayushman Plus", "Union Solar",
        "Union Equipment Finance", "Union Contractor", "Union Rent"
    ] else
    ["Collateral Security Available", "Hybrid"] if scheme == "Union MSME Suvidha" else
    ["Collateral Security Available"]
)
security = st.selectbox("Select Security Type", security_options)

# Collateral selection
collateral_options = list(collateral_concession.keys())
if scheme == "Union MSME Suvidha":
    if loan_type == "Overdraft":
        collateral_options = ["100% to <150%", "150% and above"]
        st.info("For Union MSME Suvidha Overdraft, minimum collateral coverage is 125%.")
    elif amount <= 500:
        collateral_options = ["75% to <100%", "100% to <150%", "150% and above"]
        st.info("For Union MSME Suvidha with loan amount ≤ ₹500 Lakh, minimum collateral coverage is 75%.")
    else:
        collateral_options = ["50% to <75%", "75% to <100%", "100% to <150%", "150% and above"]
        st.info("For Union MSME Suvidha with loan amount > ₹500 Lakh, minimum collateral coverage is 50%.")
elif scheme == "Union LAP":
    collateral_options = ["200% and above"]
    st.info("For Union LAP, minimum collateral coverage is 200%.")
elif scheme == "Union Rent":
    collateral_options = ["100% to <150%", "150% and above"]
    st.info("For Union Rent, minimum collateral coverage is assumed 100% (pending scheme details).")
collateral = st.selectbox("Select Collateral Coverage", collateral_options)

# Tenor for term loans
tenor = None
if loan_type == "Term Loan":
    tenor_options = list(additional_credit_risk_premium.keys())
    tenor = st.selectbox("Select Loan Tenor", tenor_options)

# Internal rating for loans > ₹50 Lakh
internal_rating = None
if amount > 50 and (scheme in CARD_RATE_SCHEMES and CARD_RATE_SCHEMES[scheme].get("all", False) or
                    (scheme in CARD_RATE_SCHEMES and amount > float(list(CARD_RATE_SCHEMES[scheme].keys())[0])) or
                    scheme == "Union MSME Suvidha"):
    internal_rating = st.selectbox("Select Internal Rating", ["CR1", "CR2", "CR3", "CR4", "CR5", "CR6", "CR7", "CR8-CR10"])
elif scheme == "Union LAP" and amount > 50:
    internal_rating = st.selectbox("Select Internal Rating", ["CR1", "CR2", "CR3", "CR4", "CR5"])

# External rating for loans > ₹25 Crore
external_rating = None
if amount > 2500 and scheme in CARD_RATE_SCHEMES and (CARD_RATE_SCHEMES[scheme].get("all", False) or
                                                     amount > float(list(CARD_RATE_SCHEMES[scheme].keys())[0])):
    external_rating = st.selectbox("Select External Rating", ["AAA", "AA", "A", "BBB", "BB & Below", "Unrated", "A1+", "A1", "A2", "A3"])

# Calculate ROI
def calculate_roi(eblr, amount, scheme, loan_type, security, collateral, tenor, internal_rating, external_rating):
    roi = eblr
    spread = 0.0
    premium = 0.0
    concession = collateral_concession.get(collateral, 0.0)
    debug_info = {
        "EBLR": f"{eblr:.2f}%",
        "Spread": "N/A",
        "Spread Source": "N/A",
        "Additional Credit Risk Premium": "0.00%",
        "Collateral Concession": f"{concession:.2f}%",
        "Final ROI": "N/A"
    }

    if scheme == "Union MSME Suvidha":
        if amount <= 10:
            st.error("Union MSME Suvidha is only for loans > ₹10 Lakh.")
            return None, {"Error": "Union MSME Suvidha is only for loans > ₹10 Lakh."}
        if amount <= 50:
            spread = suvidha_spreads["₹10 Lakh to ₹50 Lakh"]["75% to <100%"] if collateral == "75% to <100%" else suvidha_spreads["₹10 Lakh to ₹50 Lakh"]["100% and above"]
            debug_info["Spread Source"] = "Suvidha ₹10 Lakh to ₹50 Lakh"
        elif amount <= 500:
            if not internal_rating:
                st.error("Internal rating is required for loans > ₹50 Lakh.")
                return None, {"Error": "Internal rating is required for loans > ₹50 Lakh."}
            collateral_index = {"75% to <100%": 0, "100% to <150%": 1, "150% and above": 2}.get(collateral, 1)
            spread = suvidha_spreads["₹50 Lakh to ₹5 Crore"][internal_rating][collateral_index]
            debug_info["Spread Source"] = f"Suvidha ₹50 Lakh to ₹5 Crore, Collateral Index {collateral_index}"
        else:
            if not internal_rating:
                st.error("Internal rating is required for loans > ₹50 Lakh.")
                return None, {"Error": "Internal rating is required for loans > ₹50 Lakh."}
            collateral_index = 0 if collateral in ["50% to <75%", "75% to <100%", "100% to <150%"] else 1
            spread = suvidha_spreads["> ₹5 Crore"][internal_rating][collateral_index]
            debug_info["Spread Source"] = f"Suvidha > ₹5 Crore, Collateral Index {collateral_index}"
        if loan_type == "Overdraft":
            spread += 0.25  # 25 bps additional for OD over Cash Credit
        if loan_type == "Term Loan" and amount > 25:
            premium = additional_credit_risk_premium.get(tenor, 0.0)
            debug_info["Additional Credit Risk Premium"] = f"{premium:.2f}%"
    elif scheme == "Union LAP":
        if amount <= 50:
            spread = union_lap_spreads["Up to ₹25 Lakh"] if amount <= 25 else union_lap_spreads["₹25 Lakh to ₹50 Lakh"]
            debug_info["Spread Source"] = "LAP ≤ ₹50 Lakh"
        else:
            if not internal_rating:
                st.error("Internal rating is required for loans > ₹50 Lakh.")
                return None, {"Error": "Internal rating is required for loans > ₹50 Lakh."}
            spread = union_lap_spreads["> ₹50 Lakh"][internal_rating]["Micro"]  # Assuming Micro for MSME
            debug_info["Spread Source"] = "LAP > ₹50 Lakh, Micro"
    elif scheme == "Union Rent":
        st.warning("Union Rent rates are not specified. Using General MSME rates until specific rates are provided.")
        debug_info["Warning"] = "Union Rent rates are not specified. Using General MSME rates."
        if amount <= 0.5:
            spread = msme_spread_table_a["Up to ₹50,000"]
            debug_info["Spread Source"] = "Table A: Up to ₹50,000"
        elif amount <= 2:
            spread = msme_spread_table_a["₹50,000 to ₹2 Lakh"]
            debug_info["Spread Source"] = "Table A: ₹50,000 to ₹2 Lakh"
        elif amount <= 10:
            spread = msme_spread_table_a["₹2 Lakh to ₹10 Lakh"]
            debug_info["Spread Source"] = "Table A: ₹2 Lakh to ₹10 Lakh"
        elif amount <= 50:
            spread = msme_spread_table_a["₹10 Lakh to ₹50 Lakh"]
            debug_info["Spread Source"] = "Table A: ₹10 Lakh to ₹50 Lakh"
        elif amount <= 500:
            if not internal_rating:
                st.error("Internal rating is required for loans > ₹50 Lakh.")
                return None, {"Error": "Internal rating is required for loans > ₹50 Lakh."}
            spread = msme_spread_table_b[internal_rating]
            debug_info["Spread Source"] = f"Table B: {internal_rating}"
        elif amount <= 2500:
            if not internal_rating:
                st.error("Internal rating is required for loans > ₹5 Crore.")
                return None, {"Error": "Internal rating is required for loans > ₹5 Crore."}
            spread = msme_spread_table_c["> ₹5 Crore to ≤ ₹25 Crore"][internal_rating]
            debug_info["Spread Source"] = f"Table C: > ₹5 Crore to ≤ ₹25 Crore, {internal_rating}"
        else:
            if not internal_rating or not external_rating:
                st.error("Internal and external ratings are required for loans > ₹25 Crore.")
                return None, {"Error": "Internal and external ratings are required for loans > ₹25 Crore."}
            spread = msme_spread_table_c["> ₹25 Crore"][internal_rating][external_rating]
            debug_info["Spread Source"] = f"Table C: > ₹25 Crore, {internal_rating}, {external_rating}"
        if loan_type == "Term Loan" and amount > 25 and scheme not in NO_TENOR_PREMIUM_SCHEMES:
            premium = additional_credit_risk_premium.get(tenor, 0.0)
            debug_info["Additional Credit Risk Premium"] = f"{premium:.2f}%"
    else:
        if amount <= 0.5:
            spread = msme_spread_table_a["Up to ₹50,000"]
            debug_info["Spread Source"] = "Table A: Up to ₹50,000"
        elif amount <= 2:
            spread = msme_spread_table_a["₹50,000 to ₹2 Lakh"]
            debug_info["Spread Source"] = "Table A: ₹50,000 to ₹2 Lakh"
        elif amount <= 10:
            spread = msme_spread_table_a["₹2 Lakh to ₹10 Lakh"]
            debug_info["Spread Source"] = "Table A: ₹2 Lakh to ₹10 Lakh"
        elif amount <= 50:
            spread = msme_spread_table_a["₹10 Lakh to ₹50 Lakh"]
            debug_info["Spread Source"] = "Table A: ₹10 Lakh to ₹50 Lakh"
        elif amount <= 500:
            if not internal_rating:
                st.error("Internal rating is required for loans > ₹50 Lakh.")
                return None, {"Error": "Internal rating is required for loans > ₹50 Lakh."}
            spread = msme_spread_table_b[internal_rating]
            debug_info["Spread Source"] = f"Table B: {internal_rating}"
        elif amount <= 2500:
            if not internal_rating:
                st.error("Internal rating is required for loans > ₹5 Crore.")
                return None, {"Error": "Internal rating is required for loans > ₹5 Crore."}
            spread = msme_spread_table_c["> ₹5 Crore to ≤ ₹25 Crore"][internal_rating]
            debug_info["Spread Source"] = f"Table C: > ₹5 Crore to ≤ ₹25 Crore, {internal_rating}"
        else:
            if not internal_rating or not external_rating:
                st.error("Internal and external ratings are required for loans > ₹25 Crore.")
                return None, {"Error": "Internal and external ratings are required for loans > ₹25 Crore."}
            spread = msme_spread_table_c["> ₹25 Crore"][internal_rating][external_rating]
            debug_info["Spread Source"] = f"Table C: > ₹25 Crore, {internal_rating}, {external_rating}"
        if loan_type == "Term Loan" and amount > 25 and scheme not in NO_TENOR_PREMIUM_SCHEMES:
            premium = additional_credit_risk_premium.get(tenor, 0.0)
            debug_info["Additional Credit Risk Premium"] = f"{premium:.2f}%"

    roi += spread + premium - concession
    debug_info["Spread"] = f"{spread:.2f}%"
    debug_info["Final ROI"] = f"{roi:.2f}%"
    return roi, debug_info

# Button to calculate
if st.button("Calculate ROI"):
    roi, debug_info = calculate_roi(eblr, amount, scheme, loan_type, security, collateral, tenor, internal_rating, external_rating)
    if roi is not None:
        st.success(f"Effective Rate of Interest (ROI): {roi:.2f}%")
        st.write("Calculation Details:")
        for key, value in debug_info.items():
            if key not in ["Error", "Warning"]:
                st.write(f"{key}: {value}")
        if "Warning" in debug_info:
            st.warning(debug_info["Warning"])
    else:
        st.error(debug_info.get("Error", "Please check input values and try again."))

# Session state for unique run ID
if 'run_id' not in st.session_state:
    st.session_state.run_id = str(uuid.uuid4())
