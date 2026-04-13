from flask import Flask, render_template, request
app = Flask(__name__)

@app.route("/simple_form", methods=["GET", "POST"])
def simple_form():
    username = None
    if request.method == "POST":
        username = request.form.get("username")
    return render_template("simple_form.html", username=username)
@app.route("/form_validation", methods=["GET", "POST"])
def form_validation():
    username = None
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        if not username.strip():
            error = "Pole nie może być puste."
            username = None
    return render_template("simple_form.html", username=username, error=error)






@app.route("/calc", methods=["GET", "POST"])
def calc():
    result = None
    error = None
    if request.method == "POST":
        a = request.form.get("a")
        b = request.form.get("b")
        operation = request.form.get("operation")
        if not a or not b:
            error = "Pola nie mogą być puste."
            return render_template("calc.html", result=None, error=error)
        if operation=='/' and  b == 0:
            error = "Nie można dzielić przez zero."
            return render_template("calc.html", result=None, error=error)
        result = eval(f"{a} {operation} {b}")
    return render_template("calc.html", result=result, error=error)










app.run(debug=True)