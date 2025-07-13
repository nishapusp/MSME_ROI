import streamlit as st
import uuid

# === Constants ===
DEFAULT_EBLR = 8.25  # Default External Benchmark Lending Rate (Minimum Benchmark)

# Base spreads for MSME loans <= ₹50 Lakh (Annexure I, Table A)
msme_spread_table_a = {
    "Up to ₹50,000": 1.50,
    "₹50,000 to ₹2 Lakh": 1.75,
    "₹2 Lakh to ₹10 Lakh": 2.75,
    "₹10 Lakh to ₹50 Lakh": 2.25
}

# Spreads for MSME loans > ₹50 Lakh to ₹5 Crore (Annexure I, Table B)
msme_spread_table_b = {
    "CR1": [0.75, 0.40, 0.70, 0.95, 1.65],
    "CR2": [1.20, 0.65, 1.15, 1.45, 1.85],
    "CR3": [2.00, 0.70, 1.50, 1.95, 2.15],
    "CR4": [3.00, 0.75, 2.00, 2.45, 2.65],
    "CR5": [4.90, 2.45, 2.95, 3.40, 3.60],
    "CR6": [5.75, 3.15, 3.65, 4.10, 4.30],
    "CR7": [5.85, 3.25, 3.75, 4.20, 4.40],
    "CR8-CR10": [5.95, 3.35, 3.85, 4.30, 4.50]
}

# Spreads for MSME loans > ₹25 Crore (Annexure I, Table C)
msme_spread_table_c = {
    "CR1": {"AAA": 0.15, "AA": 0.20, "A": 0.25, "BBB": 0.35, "BB & Below": 0.35, "Unrated": 0.35},
    "CR2": {"AAA": 0.15, "AA": 0.20, "A": 0.25, "BBB": 0.35, "BB & Below": 0.35, "Unrated": 0.35},
    "CR3": {"AAA": 0.15, "AA": 0.20, "A": 0.25, "BBB": 0.35, "BB & Below": 0.35, "Unrated": 0.35},
    "CR4": {"AAA": 0.15, "AA": 0.20, "A": 0.25, "BBB": 0.35, "BB & Below": 0.35, "Unrated": 0.35},
    "CR5": {"AAA": 0.35, "AA": 0.35, "A": 0.35, "BBB": 0.35, "BB & Below": 0.35, "Unrated": 0.35},
    "CR6": {"AAA": 0.35, "AA": 0.35, "A": 0.35, "BBB": 0.35, "BB & Below": 0.35, "Unrated": 0.35},
    "CR7": {"AAA": 0.35, "AA": 0.35, "A": 0.35, "BBB": 0.35, "BB & Below": 0.35, "Unrated": 0.35},
    "CR8-CR10": {"AAA": 0.35, "AA": 0.35, "A": 0.35, "BBB": 0.35, "BB & Below": 0.35, "Unrated": 0.35}
}

# Additional Credit Risk Premium for Term Loans > ₹25 Lakh (Annexure I, Table D)
additional_credit_risk_premium = {
    ">1 to 3 years": 0.10,
    ">3 to 5 years": 0.25,
    ">5 to 10 years": 0.50,
    ">10 years": 1.00
}

# Collateral-based concessions for General MSME Loans and schemes using card rates (Annexure I, Table E)
collateral_concession = {
    "<50%": 0.00,
    "50% to <75%": 0.00,
    "75% to <100%": 0.10,
    "100% to <150%": 0.25,
    "150% and above": 0.50,
    "200% and above": 0.50
}

# Spreads for Union MSME Suvidha > ₹500 Lakh, 50% collateral (Page 22)
suvidha_above_500_collateral_50 = {
    "CR1": 0.35,
    "CR2": 0.45,
    "CR3": 0.55,
    "CR4": 0.60,
    "CR5": 1.10
}

# Schemes where card rates (Tables A, B, C) are used for certain loan amounts
CARD_RATE_SCHEMES = {
    "General MSME Loans": {"all": True},
    "Union Nari Shakti": {">2500": True},
    "Union MSME Superfast": {">2500": True},
    "Union Parivahan": {"all": True},
    "Union Progress": {"all": True},
    "Union Mudra": {"all": True},
    "Union Turnover Plus": {"all": True},
    "Union Ayushman Plus": {">2500": True},
    "Union LAP": {">2500": True},
    "Union Solar": {">2500": True},
    "Union Equipment Finance": {">2500": True},
    "Union Contractor": {">2500": True},
    "Union Residential Real Estate Inventory Support": {">2500": True}
}

# Schemes where Table D tenor premium does not apply (built-in risk premiums)
NO_TENOR_PREMIUM_SCHEMES = [
    "Union Residential Real Estate Inventory Support"
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

# Scheme selection (only if amount >= ₹10 Lakh)
schemes = [
    "General MSME Loans", "Union Nari Shakti", "Union MSME Superfast", "Union MSME Suvidha", "Union Parivahan",
    "Union Turnover Plus", "Union Ayushman Plus", "Union Progress", "Union Mudra", "Union LAP",
    "Union Solar", "Union Equipment Finance", "Union Contractor", "Union Residential Real Estate Inventory Support"
]
scheme = None
if amount >= 10:
    scheme = st.selectbox("Select Scheme", schemes)
else:
    scheme = "General MSME Loans"
    st.warning("Loan amount must be ₹10 Lakh or above to select a specific scheme. Using General MSME rates.")

# Loan type
loan_type_options = ["Cash Credit", "Overdraft"] if scheme == "Union MSME Suvidha" else ["Cash Credit/Working Capital"] if scheme == "Union MSME Superfast" else ["Cash Credit/Working Capital", "Term Loan"]
loan_type = st.selectbox("Select Loan Type", loan_type_options)

# Security type
security_options = ["Collateral Security Available", "CGTMSE"] if scheme in ["General MSME Loans", "Union Nari Shakti", "Union Parivahan", "Union Progress", "Union Mudra", "Union Turnover Plus", "Union Ayushman Plus", "Union Solar", "Union Equipment Finance", "Union Contractor"] else ["Collateral Security Available", "Hybrid"] if scheme == "Union MSME Suvidha" else ["Collateral Security Available"]
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
elif scheme == "Union Residential Real Estate Inventory Support":
    collateral_options = ["100% to <150%", "150% and above"]
    st.info("For Union Residential Real Estate Inventory Support, minimum collateral coverage is 133%.")
elif scheme == "Union MSME Superfast":
    internal_rating_temp = st.session_state.get("internal_rating", None)
    if internal_rating_temp in ["CR1", "CR2"]:
        collateral_options = ["50% to <75%", "75% to <100%", "100% to <150%", "150% and above"]
        st.info("For Union MSME Superfast with CR1 or CR2, minimum collateral coverage is 50%.")
    elif internal_rating_temp in ["CR3", "CR4"]:
        collateral_options = ["75% to <100%", "100% to <150%", "150% and above"]
        st.info("For Union MSME Superfast with CR3 or CR4, minimum collateral coverage is 75%.")
    else:
        collateral_options = ["75% to <100%", "100% to <150%", "150% and above"]
        st.info("For Union MSME Superfast, select an internal rating to confirm collateral requirements.")
elif security == "CGTMSE":
    collateral_options = []
else:
    collateral_options = ["<50%", "50% to <75%", "75% to <100%", "100% to <150%", "150% and above"]
collateral = None
if security != "CGTMSE" and collateral_options:
    collateral = st.selectbox("Select Collateral Coverage", collateral_options)
elif security == "CGTMSE":
    st.info("CGTMSE security implies no collateral coverage.")

# Tenor input only for Term Loan
tenor = None
if loan_type == "Term Loan":
    tenor = st.selectbox("Select Loan Tenor", ["Up to 1 year", ">1 to 3 years", ">3 to 5 years", ">5 to 10 years", ">10 years"])

# Rating inputs
internal_rating = None
external_rating = None
if amount > 50 or (scheme == "Union MSME Superfast" and amount >= 10) or (scheme in ["Union Nari Shakti", "Union Ayushman Plus", "Union LAP", "Union Solar", "Union Equipment Finance", "Union Contractor"] and amount > 25):
    internal_rating = st.selectbox("Select Internal Credit Rating", list(msme_spread_table_b.keys()))
    st.session_state["internal_rating"] = internal_rating
if amount > 2500 or (scheme == "Union Ayushman Plus" and amount > 2500):
    external_rating = st.selectbox("Select External Credit Rating", ["AAA", "AA", "A", "BBB", "BB & Below", "Unrated"])

# Additional inputs for specific schemes
is_digitized_turnover = st.checkbox("Digitized Sales Turnover >50%", value=False) if scheme == "Union Turnover Plus" else False

# === Eligibility Check ===
eligible = True
if scheme == "Union MSME Suvidha":
    if amount <= 500 and collateral in ["<50%", "50% to <75%", None]:
        eligible = False
        st.error("Ineligible for Union MSME Suvidha: Loan amount ≤ ₹500 Lakh requires minimum 75% collateral coverage.")
    elif amount > 500 and collateral == "<50%":
        eligible = False
        st.error("Ineligible for Union MSME Suvidha: Loan amount > ₹500 Lakh requires minimum 50% collateral coverage.")
    elif loan_type == "Overdraft" and collateral not in ["100% to <150%", "150% and above"]:
        eligible = False
        st.error("Ineligible for Union MSME Suvidha Overdraft: Minimum collateral coverage is 125%.")
elif scheme == "Union MSME Superfast" and internal_rating in ["CR1", "CR2"] and collateral == "<50%":
    eligible = False
    st.error("Ineligible for Union MSME Superfast: CR1 or CR2 requires minimum 50% collateral coverage.")
elif scheme == "Union MSME Superfast" and internal_rating in ["CR3", "CR4"] and collateral in ["<50%", "50% to <75%"]:
    eligible = False
    st.error("Ineligible for Union MSME Superfast: CR3 or CR4 requires minimum 75% collateral coverage.")
elif scheme == "Union LAP" and collateral != "200% and above":
    eligible = False
    st.error("Ineligible for Union LAP: Minimum collateral coverage is 200%.")
elif scheme == "Union Residential Real Estate Inventory Support" and collateral not in ["100% to <150%", "150% and above"]:
    eligible = False
    st.error("Ineligible for Union Residential Real Estate Inventory Support: Minimum collateral coverage is 133%.")

# === ROI Calculation Logic ===
def calculate_roi():
    if not eligible:
        return None, None, None, None
    roi = eblr
    spread = 0.0
    concession = 0.0
    tenor_premium = 0.0
    apply_concession = False

    # Check if scheme uses card rates
    if scheme in CARD_RATE_SCHEMES:
        if CARD_RATE_SCHEMES[scheme].get("all", False) or \
           (scheme == "Union Nari Shakti" and amount > 2500) or \
           (scheme == "Union MSME Superfast" and amount > 2500) or \
           (scheme == "Union Ayushman Plus" and amount > 2500) or \
           (scheme in ["Union LAP", "Union Solar", "Union Equipment Finance", "Union Contractor", "Union Residential Real Estate Inventory Support"] and amount > 2500):
            apply_concession = True if security != "CGTMSE" else False

    # General MSME Loans (Annexure I)
    if scheme == "General MSME Loans":
        if amount <= 50:
            for k, v in msme_spread_table_a.items():
                range_str = k.split("₹")[-1].split(" to ")[-1] if "to" in k else k.split("₹")[-1]
                range_str = range_str.split()[0].replace(",", "")
                upper_limit = float(range_str) * (100 if "Crore" in k else 1)
                if amount <= upper_limit:
                    spread = v
                    break
            else:
                spread = 2.25
        else:
            spreads = msme_spread_table_b.get(internal_rating, [5.95] * 5)
            idx = {"AAA": 0, "AA": 1, "A": 2, "BBB": 3, "BB & Below": 4, "Unrated": 4}.get(external_rating, 4) if amount > 2500 else 4 if security == "CGTMSE" else 0
            spread = msme_spread_table_c.get(internal_rating, {}).get(external_rating, 0.35) if amount > 2500 else spreads[idx]
        roi += spread
        if apply_concession:
            concession = collateral_concession.get(collateral, 0.0)
            roi -= concession
        if loan_type == "Term Loan" and tenor != "Up to 1 year" and amount > 25:
            tenor_premium = additional_credit_risk_premium.get(tenor, 0.0)
            roi += tenor_premium

    # Union MSME Suvidha (Pages 21-22)
    elif scheme == "Union MSME Suvidha":
        if amount <= 50:
            spread = 1.25 if collateral == "100% to <150%" else 1.35
        elif amount <= 500:
            cr_map = {
                "CR1": {"75% to <100%": 0.40, "100% to <150%": 0.25, "150% and above": 0.20},
                "CR2": {"75% to <100%": 0.50, "100% to <150%": 0.40, "150% and above": 0.30},
                "CR3": {"75% to <100%": 0.60, "100% to <150%": 0.45, "150% and above": 0.35},
                "CR4": {"75% to <100%": 0.65, "100% to <150%": 0.50, "150% and above": 0.40},
                "CR5": {"75% to <100%": 1.15, "100% to <150%": 1.00, "150% and above": 0.70}
            }
            spread = cr_map.get(internal_rating, {}).get(collateral, 1.25)
        else:
            spread = suvidha_above_500_collateral_50.get(internal_rating, 1.10) if collateral == "50% to <75%" else msme_spread_table_c.get(internal_rating, {}).get(external_rating, 0.35)
            apply_concession = True if collateral != "50% to <75%" and security != "CGTMSE" else False
        roi += spread
        if apply_concession:
            concession = collateral_concession.get(collateral, 0.0)
            roi -= concession
        if loan_type == "Overdraft":
            roi += 0.25
        if loan_type == "Term Loan" and tenor != "Up to 1 year" and amount > 25:
            tenor_premium = additional_credit_risk_premium.get(tenor, 0.0)
            roi += tenor_premium

    # Union Nari Shakti (Page 13)
    elif scheme == "Union Nari Shakti":
        if amount <= 25:
            spread = 2.25
        elif amount <= 50:
            spread = 1.90
        else:
            cr_map = {"CR1": 1.50, "CR2": 1.75, "CR3": 2.00, "CR4": 2.25, "CR5": 2.50}
            spread = cr_map.get(internal_rating, 2.50)
            if amount > 2500:
                spread = msme_spread_table_c.get(internal_rating, {}).get(external_rating, 0.35)
        roi += spread
        if apply_concession:
            concession = collateral_concession.get(collateral, 0.0)
            roi -= concession
        if loan_type == "Term Loan" and tenor != "Up to 1 year" and amount > 25 and scheme not in NO_TENOR_PREMIUM_SCHEMES:
            tenor_premium = additional_credit_risk_premium.get(tenor, 0.0)
            roi += tenor_premium

    # Union MSME Superfast (Page 15)
    elif scheme == "Union MSME Superfast":
        spread_map = {"CR1": 0.85, "CR2": 1.10, "CR3": 1.10, "CR4": 1.35}
        spread = spread_map.get(internal_rating, 1.50)
        if amount > 2500:
            spread = msme_spread_table_c.get(internal_rating, {}).get(external_rating, 0.35)
        roi += spread
        if apply_concession:
            concession = collateral_concession.get(collateral, 0.0)
            roi -= concession
        if loan_type == "Term Loan" and tenor != "Up to 1 year" and amount > 25 and scheme not in NO_TENOR_PREMIUM_SCHEMES:
            tenor_premium = additional_credit_risk_premium.get(tenor, 0.0)
            roi += tenor_premium

    # Union Parivahan, Union Progress, Union Mudra (Page 13, 15)
    elif scheme in ["Union Parivahan", "Union Progress", "Union Mudra"]:
        if amount <= 50:
            for k, v in msme_spread_table_a.items():
                range_str = k.split("₹")[-1].split(" to ")[-1] if "to" in k else k.split("₹")[-1]
                range_str = range_str.split()[0].replace(",", "")
                upper_limit = float(range_str) * (100 if "Crore" in k else 1)
                if amount <= upper_limit:
                    spread = v
                    break
            else:
                spread = 2.25
        else:
            spreads = msme_spread_table_b.get(internal_rating, [5.95] * 5)
            idx = {"AAA": 0, "AA": 1, "A": 2, "BBB": 3, "BB & Below": 4, "Unrated": 4}.get(external_rating, 4) if amount > 2500 else 4 if security == "CGTMSE" else 0
            spread = msme_spread_table_c.get(internal_rating, {}).get(external_rating, 0.35) if amount > 2500 else spreads[idx]
        roi += spread
        if apply_concession:
            concession = collateral_concession.get(collateral, 0.0)
            roi -= concession
        if loan_type == "Term Loan" and tenor != "Up to 1 year" and amount > 25 and scheme not in NO_TENOR_PREMIUM_SCHEMES:
            tenor_premium = additional_credit_risk_premium.get(tenor, 0.0)
            roi += tenor_premium

    # Union Turnover Plus (Page 14)
    elif scheme == "Union Turnover Plus":
        if amount <= 50:
            for k, v in msme_spread_table_a.items():
                range_str = k.split("₹")[-1].split(" to ")[-1] if "to" in k else k.split("₹")[-1]
                range_str = range_str.split()[0].replace(",", "")
                upper_limit = float(range_str) * (100 if "Crore" in k else 1)
                if amount <= upper_limit:
                    spread = v
                    break
            else:
                spread = 2.25
        else:
            spreads = msme_spread_table_b.get(internal_rating, [5.95] * 5)
            idx = {"AAA": 0, "AA": 1, "A": 2, "BBB": 3, "BB & Below": 4, "Unrated": 4}.get(external_rating, 4) if amount > 2500 else 4 if security == "CGTMSE" else 0
            spread = msme_spread_table_c.get(internal_rating, {}).get(external_rating, 0.35) if amount > 2500 else spreads[idx]
        roi += spread
        if apply_concession:
            concession = collateral_concession.get(collateral, 0.0)
            roi -= concession
        if is_digitized_turnover:
            roi = max(roi - 0.50, eblr)
        if loan_type == "Term Loan" and tenor != "Up to 1 year" and amount > 25 and scheme not in NO_TENOR_PREMIUM_SCHEMES:
            tenor_premium = additional_credit_risk_premium.get(tenor, 0.0)
            roi += tenor_premium

    # Union Ayushman Plus (Page 14)
    elif scheme == "Union Ayushman Plus":
        if amount <= 2500:
            spreads = {
                "CR1": {"AAA/A1+": 0.25, "AA/A1": 0.25, "A/A2": 0.25, "BBB/A3": 0.25, "A4 & Below": 0.50, "Unrated": 1.00},
                "CR2": {"AAA/A1+": 0.25, "AA/A1": 0.25, "A/A2": 0.25, "BBB/A3": 0.50, "A4 & Below": 1.00, "Unrated": 1.00},
                "CR3": {"AAA/A1+": 0.25, "AA/A1": 0.25, "A/A2": 0.25, "BBB/A3": 0.75, "A4 & Below": 1.00, "Unrated": 1.00},
                "CR4": {"AAA/A1+": 0.25, "AA/A1": 0.25, "A/A2": 0.50, "BBB/A3": 1.00, "A4 & Below": 1.00, "Unrated": 1.00},
                "CR5": {"AAA/A1+": 0.50, "AA/A1": 0.75, "A/A2": 1.00, "BBB/A3": 1.50, "A4 & Below": 2.00, "Unrated": 2.25}
            }
            external_key = external_rating if amount > 2500 else "AAA/A1+"
            spread = spreads.get(internal_rating, {}).get(external_key, 1.00)
        else:
            spread = msme_spread_table_c.get(internal_rating, {}).get(external_rating, 0.35)
        roi += spread
        if apply_concession:
            concession = collateral_concession.get(collateral, 0.0)
            roi -= concession
        if loan_type == "Term Loan" and tenor != "Up to 1 year" and amount > 25 and scheme not in NO_TENOR_PREMIUM_SCHEMES:
            tenor_premium = additional_credit_risk_premium.get(tenor, 0.0)
            roi += tenor_premium

    # Union LAP (Page 16)
    elif scheme == "Union LAP":
        if amount <= 25:
            spread = 2.25
        elif amount <= 50:
            spread = 2.25
        else:
            cr_map = {"Micro": {"CR1": 2.00, "CR2": 2.00, "CR3": 2.00, "CR4": 2.25, "CR5": 2.50},
                      "Medium": {"CR1": 2.50, "CR2": 2.50, "CR3": 2.50, "CR4": 2.75, "CR5": 3.00}}
            spread = cr_map.get("Micro", {}).get(internal_rating, 2.50)
            if amount > 2500:
                spread = msme_spread_table_c.get(internal_rating, {}).get(external_rating, 0.35)
        roi += spread
        if apply_concession:
            concession = collateral_concession.get(collateral, 0.0)
            roi -= concession
        if loan_type == "Term Loan" and tenor != "Up to 1 year" and amount > 25 and scheme not in NO_TENOR_PREMIUM_SCHEMES:
            tenor_premium = additional_credit_risk_premium.get(tenor, 0.0)
            roi += tenor_premium

    # Union Solar (Page 17)
    elif scheme == "Union Solar":
        if amount <= 25:
            spread = 0.50
        elif amount <= 50:
            spread = 0.75
        else:
            cr_map = {"CR1": 0.50, "CR2": 0.55, "CR3": 0.65, "CR4": 0.80, "CR5": 1.00}
            spread = cr_map.get(internal_rating, 1.00)
            if amount > 2500:
                spread = msme_spread_table_c.get(internal_rating, {}).get(external_rating, 0.35)
        roi += spread
        if apply_concession:
            concession = collateral_concession.get(collateral, 0.0)
            roi -= concession
        if loan_type == "Term Loan" and tenor != "Up to 1 year" and amount > 25 and scheme not in NO_TENOR_PREMIUM_SCHEMES:
            tenor_premium = additional_credit_risk_premium.get(tenor, 0.0)
            roi += tenor_premium

    # Union Equipment Finance (Page 17)
    elif scheme == "Union Equipment Finance":
        if amount <= 25:
            spread = 1.25
        elif amount <= 50:
            spread = 1.25
        else:
            cr_map = {"CR1": 0.25, "CR2": 0.50, "CR3": 0.75, "CR4": 1.00, "CR5": 1.25}
            spread = cr_map.get(internal_rating, 1.25)
            if amount > 2500:
                spread = msme_spread_table_c.get(internal_rating, {}).get(external_rating, 0.35)
        roi += spread
        if apply_concession:
            concession = collateral_concession.get(collateral, 0.0)
            roi -= concession
        if loan_type == "Term Loan" and tenor != "Up to 1 year" and amount > 25 and scheme not in NO_TENOR_PREMIUM_SCHEMES:
            tenor_premium = additional_credit_risk_premium.get(tenor, 0.0)
            roi += tenor_premium

    # Union Contractor (Page 18)
    elif scheme == "Union Contractor":
        if amount <= 25:
            spread = 1.13
        elif amount <= 50:
            spread = 1.40
        else:
            cr_map = {
                "Micro": {"CR1": 0.90, "CR2": 1.00, "CR3": 1.10, "CR4": 1.40, "CR5": 1.60},
                "Small & Medium": {"CR1": 1.00, "CR2": 1.10, "CR3": 1.25, "CR4": 1.50, "CR5": 1.75}
            }
            spread = cr_map.get("Small & Medium", {}).get(internal_rating, 1.75)
            if amount > 2500:
                spread = msme_spread_table_c.get(internal_rating, {}).get(external_rating, 0.35)
        roi += spread
        if apply_concession:
            concession = collateral_concession.get(collateral, 0.0)
            roi -= concession
        if loan_type == "Term Loan" and tenor != "Up to 1 year" and amount > 25 and scheme not in NO_TENOR_PREMIUM_SCHEMES:
            tenor_premium = additional_credit_risk_premium.get(tenor, 0.0)
            roi += tenor_premium

    # Union Residential Real Estate Inventory Support (Page 19)
    elif scheme == "Union Residential Real Estate Inventory Support":
        if tenor == "Up to 1 year":
            spread = 2.60
        elif tenor == ">1 to 3 years":
            spread = 3.60
        elif tenor == ">3 to 5 years":
            spread = 4.10
        else:  # >5 years
            spread = 4.10
        if amount > 2500:
            spread = msme_spread_table_c.get(internal_rating, {}).get(external_rating, 0.35)
        roi += spread
        if apply_concession:
            concession = collateral_concession.get(collateral, 0.0)
            roi -= concession
        # No Table D premium, as spreads include tenor-based risk

    return round(roi, 2), spread, concession, tenor_premium

# === Calculate ROI ===
roi, spread, concession, tenor_premium = calculate_roi()

# === Output ===
st.markdown("---")
if roi is not None:
    st.subheader(f"Calculated ROI: {roi}%")
    st.text(f"Scheme: {scheme}")
    st.text(f"Loan Amount: ₹{amount} Lakh")
    st.text(f"Loan Type: {loan_type}, Security: {security}")
    if collateral:
        st.text(f"Collateral Coverage: {collateral}")
    if tenor:
        st.text(f"Loan Tenor: {tenor}")
    if internal_rating:
        st.text(f"Internal Rating: {internal_rating}")
    if external_rating:
        st.text(f"External Rating: {external_rating}")
    if is_digitized_turnover:
        st.text("Digitized Sales Turnover >50%: Yes")
    st.text(f"Debug Info: Spread = {spread}%, Concession = {concession}%, Tenor Premium = {tenor_premium}%")
else:
    st.error("ROI cannot be calculated due to ineligibility.")