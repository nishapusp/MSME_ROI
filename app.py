import streamlit as st

# === Constants ===
DEFAULT_EBLR = 8.25

# Rating-based spreads for non-schematic fallback logic
credit_spread = {
    "CR1": 0.50, "CR2": 0.75, "CR3": 1.75, "CR4": 2.00,
    "CR5": 3.50, "CR6": 6.85, "CR7": 6.95, "CR8": 7.05,
    "CR9": 7.05, "CR10": 7.05
}

# Collateral discount logic (used in some schemes)
collateral_discount = {
    "0-50%": 0.00,
    "50-100%": 0.10,
    "100-150%": 0.25,
    "150%+": 0.50
}

# Base spreads for general MSME logic (loans <= ₹50L)
def get_base_spread(loan_type, amount, security):
    if loan_type == "CC/WCDL":
        if amount <= 10:
            return 1.50 if security == "Secured" else 2.50
        elif amount <= 50:
            return 2.00 if security == "Secured" else 2.50
    elif loan_type == "Term Loan":
        if amount <= 10:
            return 1.75 if security == "Secured" else 2.75
        elif amount <= 50:
            return 2.25 if security == "Secured" else 2.75
    return 0.0

# === Streamlit UI ===
st.title("MSME Loan ROI Calculator (Schematic + Non-Schematic)")

# Basic Inputs
eblr = st.number_input("Enter EBLR (%)", value=DEFAULT_EBLR, step=0.01)
loan_type = st.selectbox("Select Loan Type", ["CC/WCDL", "Term Loan"])
amount = st.number_input("Enter Loan Amount in ₹ Lakhs", min_value=1.0, step=0.1)
security = st.selectbox("Select Security Type", ["Secured", "Unsecured/CGTMSE"])
collateral = st.selectbox("Select Collateral Coverage (%)", list(collateral_discount.keys()))
scheme = st.selectbox("Select Scheme (if applicable)", [
    "None", "Union Nari Shakti", "Union MSME Superfast", "Union MSME Suvidha"
])

# Rating inputs
internal_rating = external_rating = None
if amount >= 50:
    internal_rating = st.selectbox("Select Internal Credit Rating", list(credit_spread.keys()))
if amount > 250:
    external_rating = st.selectbox("Select External Credit Rating", ["AAA", "AA", "A", "BBB", "BB & Below", "Unrated"])

# === ROI Calculation Logic ===
def calculate_nari_shakti(amount, rating, collateral):
    if amount <= 25:
        return eblr + 2.25
    elif amount <= 50:
        return eblr + 1.90
    else:
        # For >₹50L: spread based on rating + collateral (simplified)
        cr_map = {
            "CR1": 1.50, "CR2": 1.75, "CR3": 2.00, "CR4": 2.25, "CR5": 2.50
        }
        spread = cr_map.get(rating, 2.50)
        if collateral == "150%+": spread -= 0.25
        elif collateral == "100-150%": spread -= 0.15
        return eblr + spread

def calculate_msmse_superfast(rating):
    spread_map = {"CR1": 0.85, "CR2": 1.10, "CR3": 1.10, "CR4": 1.35}
    return eblr + spread_map.get(rating, 1.50)

def calculate_msmse_suvidha(amount, rating, collateral):
    if amount <= 50:
        return eblr + (1.25 if collateral == "100-150%" else 1.35)
    else:
        cr_map = {
            "CR1": {"75-100": 0.40, "100-150": 0.25, "150%+": 0.20},
            "CR2": {"75-100": 0.50, "100-150": 0.40, "150%+": 0.30},
            "CR3": {"75-100": 0.60, "100-150": 0.45, "150%+": 0.35},
            "CR4": {"75-100": 0.65, "100-150": 0.50, "150%+": 0.40},
            "CR5": {"75-100": 1.15, "100-150": 1.00, "150%+": 0.70}
        }
        spread = cr_map.get(rating, {}).get(collateral, 1.25)
        return eblr + spread

# === Calculate ROI ===
if scheme == "Union Nari Shakti":
    roi = round(calculate_nari_shakti(amount, internal_rating, collateral), 2)
elif scheme == "Union MSME Superfast":
    roi = round(calculate_msmse_superfast(internal_rating), 2)
elif scheme == "Union MSME Suvidha":
    roi = round(calculate_msmse_suvidha(amount, internal_rating, collateral), 2)
else:
    base_spread = get_base_spread(loan_type, amount, security) if amount < 50 else 0.0
    rating_spread = credit_spread.get(internal_rating, 0.0) if amount >= 50 else 0.0
    collateral_concession = collateral_discount.get(collateral, 0.0)
    roi = round(eblr + base_spread + rating_spread - collateral_concession, 2)

# === Output ===
st.markdown("---")
st.subheader(f"Calculated ROI: {roi}%")
st.text(f"Scheme: {scheme}")
st.text(f"Loan Amount: ₹{amount} Lakh")
st.text(f"Loan Type: {loan_type}, Security: {security}")
if internal_rating: st.text(f"Internal Rating: {internal_rating}")
if external_rating: st.text(f"External Rating: {external_rating}")
