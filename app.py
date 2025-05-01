from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
import os
import base64
from bson.objectid import ObjectId

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["event_explore"]
events_collection = db["events"]
admins_collection = db["admins"]
registrations_collection = db["registrations"]

# Static folder setup
UPLOAD_FOLDER = "static/images/"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Dummy admin
ADMIN_CREDENTIALS = {"username": "admin", "password": "admin123"}

@app.route("/")
def index():
    events = events_collection.find()
    return render_template("index.html", events=events)

@app.route("/event/<event_id>")
def event_detail(event_id):
    event = events_collection.find_one({"_id": ObjectId(event_id)})
    if not event:
        return "Event not found", 404
    return render_template("event_detail.html", event=event)

@app.route("/register/<event_id>", methods=["GET", "POST"])
def register(event_id):
    event = events_collection.find_one({"_id": ObjectId(event_id)})
    if not event:
        return "Event not found", 404

    if request.method == "POST":
        name = request.form.get("name")
        college = request.form.get("college")
        email = request.form.get("email")
        phone = request.form.get("phone")

        if name and college and email and phone:
            registrations_collection.insert_one({
                "event_id": event_id,
                "name": name,
                "college": college,
                "email": email,
                "phone": phone
            })
            flash("Event registered successfully!", "success")
        else:
            flash("All fields are required!", "danger")

    return render_template("register.html", event=event)

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN_CREDENTIALS["username"] and password == ADMIN_CREDENTIALS["password"]:
            session["admin"] = True
            flash("Login successful!", "success")
            return redirect(url_for("admin_panel"))
        else:
            flash("Invalid credentials!", "danger")

    return render_template("login.html")

@app.route("/admin/panel")
def admin_panel():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    events = events_collection.find()
    return render_template("admin_panel.html", events=events)

@app.route("/edit-event/<event_id>", methods=["GET", "POST"])
def edit_event(event_id):
    event = events_collection.find_one({"_id": ObjectId(event_id)})

    if not event:
        return "Event not found", 404

    if request.method == "POST":
        updated_event = {
            "name": request.form.get("name"),
            "description": request.form.get("description"),
            "venue": request.form.get("venue"),
            "date": request.form.get("date"),
            "time": request.form.get("time"),
            "category": request.form.get("category"),
        }

        events_collection.update_one({"_id": ObjectId(event_id)}, {"$set": updated_event})
        flash("Event updated successfully!", "success")
        return redirect(url_for("admin_panel"))

    return render_template("edit_event.html", event=event)

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    flash("Logged out successfully.", "info")
    return redirect(url_for("admin_login"))

@app.route("/event-registrations/<event_id>")
def event_registrations(event_id):
    event = events_collection.find_one({"_id": ObjectId(event_id)})
    registrations = registrations_collection.find({"event_id": event_id})

    if not event:
        return "Event not found", 404

    return render_template("event_registrations.html", event=event, registrations=registrations)

@app.route("/add-event", methods=["GET", "POST"])
def add_event():
    if "admin" not in session:
        flash("Unauthorized access!", "danger")
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        event_name = request.form.get("name")
        event_description = request.form.get("description")
        event_venue = request.form.get("venue")
        event_date = request.form.get("date")
        event_time = request.form.get("time")
        event_category = request.form.get("category")
        event_image = request.files.get("image")

        if not all([event_name, event_description, event_venue, event_date, event_time, event_category, event_image]):
            flash("All fields are required!", "danger")
            return redirect(url_for("add_event"))

        image_data = base64.b64encode(event_image.read()).decode("utf-8")

        event_data = {
            "name": event_name,
            "description": event_description,
            "venue": event_venue,
            "date": event_date,
            "time": event_time,
            "category": event_category,
            "image": image_data
        }

        events_collection.insert_one(event_data)
        flash("Event added successfully!", "success")
        return redirect(url_for("admin_panel"))

    return render_template("add_event.html")

@app.route("/delete-event/<event_id>")
def delete_event(event_id):
    if "admin" not in session:
        flash("Unauthorized access!", "danger")
        return redirect(url_for("admin_login"))

    event = events_collection.find_one({"_id": ObjectId(event_id)})
    if not event:
        flash("Event not found!", "danger")
        return redirect(url_for("admin_panel"))

    events_collection.delete_one({"_id": ObjectId(event_id)})
    flash("Event deleted successfully!", "success")
    return redirect(url_for("admin_panel"))

# ✅ Correct place to run app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render uses environment PORT
    app.run(host="0.0.0.0", port=port, debug=True)
