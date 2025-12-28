from flask import Flask, render_template, request, redirect, url_for, flash
from app.core import RecordManager

app = Flask(__name__)
app.secret_key = "dev-key" 

manager = RecordManager()



@app.route("/")
def index():
    query = request.args.get("q", "")
    records = manager.search(query) if query else manager.records.values()
    return render_template("index.html", records=records, query=query)



# ADD 

@app.route("/add", methods=["GET", "POST"])
def add():
    record = None  # no record exists yet
    if request.method == "POST":
        try:
            name = request.form.get("name") or None
            gender = request.form.get("gender") or None
            phone = request.form.get("phone") or None
            age_raw = request.form.get("age")
            age = None

            # Validate age
            if age_raw:
                try:
                    age = int(age_raw)
                    if age < 0 or age > 55:
                        flash("Age must be between 0 and 55.")
                        return render_template("add.html", record=record)
                except ValueError:
                    flash("Invalid age entered.")
                    return render_template("add.html", record=record)

            # Validate gender
            if gender not in ["Male", "Female"]:
                flash("Please select a valid gender.")
                return render_template("add.html", record=record)

            # ARC logic
            arc = None
            arc_link = None
            if gender == "Female":
                arc = request.form.get("arc") == "yes"
                if arc:
                    arc_link = request.form.get("arc_link") or None

            # Add record
            new_record = manager.add_record(
                name=name,
                gender=gender,
                age=age,
                arc=arc,
                arc_link=arc_link,
                phone=phone
            )
            flash(f"Record added successfully! New ID: {new_record['id']}")
            return redirect(url_for("index"))

        except Exception as e:
            flash(str(e))

    return render_template("add.html", record=record)



# ---------- DELETE ----------
@app.route("/delete/<record_id>", methods=["POST"])
def delete(record_id):
    try:
        manager.delete_record(record_id)  # delete from DB and in-memory
        flash("Record deleted successfully")
    except KeyError:
        flash("Record not found")
    except Exception as e:
        flash(f"Error deleting record: {str(e)}")
    
    return redirect(url_for("index"))





@app.route("/edit/<record_id>", methods=["GET", "POST"])
def edit(record_id):
    record = manager.records.get(record_id)
    if not record:
        flash("Record not found")
        return redirect(url_for("index"))

    if request.method == "POST":
        try:
            updates = {}

            # Handle editable fields
            for field in ["name", "age", "phone"]:
                value = request.form.get(field) or None
                if field == "age" and value is not None:
                    try:
                        value = int(value)
                        if value < 0 or value > 55:
                            flash("Age must be between 0 and 55.")
                            return render_template("edit.html", record=record)
                    except ValueError:
                        flash("Invalid age entered.")
                        return render_template("edit.html", record=record)

                if value != record.get(field):
                    updates[field] = value


            # Handle ARC link if record has ARC
            if record.get("gender") == "Female" and record.get("arc"):
                new_link = request.form.get("arc_link") or None
                if new_link != record.get("arc_link"):
                    updates["arc_link"] = new_link

            # Update record
            updated_records = manager.edit_record(record_id, **updates)
            flash("Record updated successfully")
            return redirect(url_for("index"))

            # return redirect(url_for("edit", record_id=updated_records["id"]))

            

        except Exception as e:
            flash(str(e))
            return render_template("edit.html", record=record)

    return render_template("edit.html", record=record)


