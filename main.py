from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # Loop through each column in the data record using Dictionary Comprehension
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    # Fetch a random cafe from our database
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    # Return a random cafe details in JSON format
    return jsonify(cafe=random_cafe.to_dict())


# HTTP GET - Read Record
@app.route("/all")
def get_all_cafes():
    all_cafes = db.session.query(Cafe).all()
    # Return all cafes into JSON format using List Comprehension
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])


# Search a cafe by location
@app.route("/search")
def search_by_location():
    query_location = request.args.get("loc")
    search_results = Cafe.query.filter_by(location=query_location).all()
    cafes = [cafe.to_dict() for cafe in search_results]
    if len(cafes) > 0:
        return jsonify(cafes)
    else:
        return jsonify(error={"Not Found": "There is no cafe at this location."})


# HTTP POST - Create Record
# Add new cafe to the database
@app.route("/add", methods=["POST"])
def post_new_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "The new cafe was added."})


# HTTP PUT/PATCH - Update Record
@app.route("/update_price/<int:cafe_id>", methods=["PATCH", "GET"])
def patch_new_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        cafe.coffee_price = str(new_price)
        db.session.commit()
        return jsonify(response={"success": f"Successfully updated the price for {cafe.name} cafe for {cafe.coffee_price}"})
    else:
        return jsonify(response={"error": f"A cafe with that id was not found inside the database"})


# HTTP DELETE - Delete Record
@app.route("/report_closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api_key")
    if api_key == "SecretAPIKey":
        cafe = db.session.query(Cafe).get(cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"Success": f"Successfully deleted the {cafe.name} cafe from the database."})
        else:
            return jsonify(response={"Error": "Cafe not found"})
    else:
        return jsonify(response={"Forbidden": "Invalid API KEy"})


if __name__ == '__main__':
    app.run(debug=True)
