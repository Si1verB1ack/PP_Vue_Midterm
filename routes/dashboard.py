from app import app, render_template


@app.route("/")
@app.route("/admin")
@app.route("/admin/dashboard")
def dashboard():
    module = {
        'main': 'Users'
    }
    return render_template("admin/index.html", module=module)
