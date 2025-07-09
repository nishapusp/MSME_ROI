import streamlit as st

# Default EBLR
DEFAULT_EBLR = 8.25

# Credit rating spreads (for loans > ₹50 lakh)
credit_spread = {
    "CR1": 0.50, "CR2": 0.75, "CR3": 1.75, "CR4": 2.00,
    "CR5": 3.50, "CR6": 6.85, "CR7": 6.95, "CR8": 7.05,
    "CR9": 7.05, "CR10": 7.05
}

# Collateral-based concessions
collateral_discount = {
    "0-50%": 0.00,
    "50-100%": 0.10,
    "100-150%": 0.25,
    "150%+": 0.50
}

# Tenure-based premium (for Term Loans > ₹25 lakh and >1 year)
tenure_premium = {
    "Up to 1 year": 0.00,
    "Greater than 1 year & up to 3 years": 0.10,
    "Greater than 3 years & up to 5 years": 0.25,
    "Greater than 5 years & up to 10 years": 0.50,
    "Greater than 10 years": 1.00
}

# Base spread only for loans ≤ 50 lakh
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

st.title("Non-Schematic MSME Loan ROI Calculator (v4)")

# Inputs
eblr = st.number_input("Enter EBLR (%)", value=DEFAULT_EBLR, step=0.01)
loan_type = st.selectbox("Select Loan Type", ["CC/WCDL", "Term Loan"])
amount = st.number_input("Enter Loan Amount in ₹ Lakhs", min_value=1.0, step=0.1)
security = st.selectbox("Select Security Type", ["Secured", "Unsecured/CGTMSE"])
collateral = st.selectbox("Select Collateral Coverage (%)", list(collateral_discount.keys()))

rating_spread = 0.0
tenure_spread = 0.0
base_spread = 0.0

if amount > 50:
    rating = st.selectbox("Select Internal Credit Rating", list(credit_spread.keys()))
    rating_spread = credit_spread.get(rating, 0.0)

if loan_type == "Term Loan" and amount > 25:
    tenure = st.selectbox("Select Total Loan Tenure (Including Moratorium)", list(tenure_premium.keys()))
    tenure_spread = tenure_premium.get(tenure, 0.0)

if amount <= 50:
    base_spread = get_base_spread(loan_type, amount, security)

collateral_concession = collateral_discount.get(collateral, 0.0)

roi = round(eblr + base_spread + rating_spread + tenure_spread - collateral_concession, 2)

# Display Output
st.markdown("---")
st.subheader(f"Calculated ROI: {roi}%")
st.text(f"Base EBLR: {eblr}%")
st.text(f"Loan Type: {loan_type}")
st.text(f"Loan Amount: ₹{amount} Lakh")
st.text(f"Security Type: {security}")
st.text(f"Base Spread (≤ ₹50L): {base_spread}%")
st.text(f"Rating Spread (> ₹50L): {rating_spread}%")
st.text(f"Tenure Premium (if TL > ₹25L): {tenure_spread}%")
st.text(f"Collateral Concession: -{collateral_concession}%")
