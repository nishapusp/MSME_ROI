from flask import Flask, render_template, request

app = Flask(__name__)

# Default EBLR (can be replaced by user input)
DEFAULT_EBLR = 8.25

# Spread by credit rating (CR1 to CR10)
credit_spread = {
    "CR1": 0.50, "CR2": 0.75, "CR3": 1.75, "CR4": 2.00,
    "CR5": 3.50, "CR6": 6.85, "CR7": 6.95, "CR8": 7.05,
    "CR9": 7.05, "CR10": 7.05
}

# Additional credit risk premium based on loan tenure
tenor_premium = {
    "1-3": 0.10, "3-5": 0.25, "5-10": 0.50, "10+": 1.00
}

# Scheme-based concessions
scheme_concessions = {
    "None": 0.0,
    "Union Start-Up": 0.50,
    "CGTMSE": 0.25
}

# Collateral-based concessions
collateral_concessions = {
    "0-50": 0.00,
    "50-100": 0.10,
    "100-150": 0.25,
    "150+": 0.50
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            eblr = float(request.form.get("eblr", DEFAULT_EBLR))
            rating = request.form["rating"]
            tenure = request.form["tenure"]
            scheme = request.form["scheme"]
            collateral = request.form["collateral"]

            spread = credit_spread.get(rating, 0)
            premium = tenor_premium.get(tenure, 0)
            scheme_discount = scheme_concessions.get(scheme, 0)
            collateral_discount = collateral_concessions.get(collateral, 0)

            roi = eblr + spread + premium - scheme_discount - collateral_discount
            roi = round(roi, 2)

            return render_template("result.html", roi=roi, eblr=eblr, spread=spread, premium=premium,
                                   scheme_discount=scheme_discount, collateral_discount=collateral_discount)
        except Exception as e:
            return f"Error: {str(e)}"

    return render_template("form.html", default_eblr=DEFAULT_EBLR)

if __name__ == "__main__":
    app.run(debug=True)
