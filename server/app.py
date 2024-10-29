import os

from flask import Flask, jsonify, make_response, request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import Hero, HeroPower, Power, db

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


# home
@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


# get all heroes
@app.route("/heroes", methods=["GET"])
def get_heroes():
    heroes = Hero.query.all()
    return jsonify([hero.to_dict(rules=("-hero_powers",)) for hero in heroes]), 200


# get hero by id
@app.route("/heroes/<int:id>", methods=["GET"])
def get_hero_by_id(id):
    hero = db.session.get(Hero, id)
    if not hero:
        return jsonify({"error": "Hero not found"}), 404
    return jsonify(hero.to_dict()), 200


# get all powers
@app.route("/powers", methods=["GET"])
def get_powers():
    powers = Power.query.all()
    return (
        jsonify([power.to_dict(rules=("-hero_powers", "-heroes")) for power in powers]),
        200,
    )


# get power by id
@app.route("/powers/<int:id>", methods=["GET"])
def get_power_by_id(id):
    power = db.session.get(Power, id)
    if not power:
        return jsonify({"error": "Power not found"}), 404
    return jsonify(power.to_dict(rules=("-hero_powers", "-heroes"))), 200


# update powers
@app.route("/powers/<int:id>", methods=["PATCH"])
def patch_power_by_id(id):
    power = db.session.get(Power, id)
    if not power:
        return jsonify({"error": "Power not found"}), 404

    data = request.get_json()
    description = data.get("description", "")

    if len(description) < 20:
        return jsonify({"errors": ["validation errors"]}), 400

    power.description = description
    db.session.commit()
    return jsonify(power.to_dict()), 200


# create power
@app.route("/hero_powers", methods=["POST"])
def create_hero_power():
    data = request.get_json()
    strength = data.get("strength")
    hero_id = data.get("hero_id")
    power_id = data.get("power_id")

    if strength not in ["Strong", "Weak", "Average"]:
        return jsonify({"errors": ["validation errors"]}), 400

    hero = db.session.get(Hero, hero_id)
    power = db.session.get(Power, power_id)
    if not hero or not power:
        return jsonify({"error": "Hero or Power not found"}), 404

    hero_power = HeroPower(strength=strength, hero_id=hero_id, power_id=power_id)
    db.session.add(hero_power)
    db.session.commit()

    return jsonify(hero_power.to_dict()), 200


if __name__ == "_main_":
    app.run(port=5555, debug=True)