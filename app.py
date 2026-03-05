"""
ACEest Fitness & Gym - Flask Web Application
A fitness and gym management web application built with Flask.
"""

from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

# ─────────────────────────────────────────────
# In-memory data store (replaces SQLite for web)
# ─────────────────────────────────────────────

clients_db = {}

PROGRAMS = {
    "fat_loss_3day": {
        "name": "Fat Loss (FL) – 3 Day",
        "factor": 22,
        "description": "3-day full-body fat loss programme",
        "workout": (
            "Mon: Back Squat 5x5 + Core AMRAP\n"
            "Wed: Bench Press + 21-15-9 WOD\n"
            "Fri: Zone 2 Cardio 30 min"
        ),
        "diet": (
            "Breakfast: Egg Whites + Oats\n"
            "Lunch: Grilled Chicken + Brown Rice\n"
            "Dinner: Fish Curry + Millet Roti\n"
            "Target: ~2000 kcal"
        ),
    },
    "fat_loss_5day": {
        "name": "Fat Loss (FL) – 5 Day",
        "factor": 24,
        "description": "5-day split, higher-volume fat loss",
        "workout": (
            "Mon: Full Body HIIT\n"
            "Tue: Upper Body Strength\n"
            "Wed: Cardio + Core\n"
            "Thu: Lower Body Strength\n"
            "Fri: Circuit Training"
        ),
        "diet": (
            "Breakfast: Smoothie Bowl\n"
            "Lunch: Turkey Wrap + Salad\n"
            "Dinner: Grilled Fish + Veggies\n"
            "Target: ~2200 kcal"
        ),
    },
    "muscle_gain_ppl": {
        "name": "Muscle Gain (MG) – PPL",
        "factor": 35,
        "description": "Push / Pull / Legs hypertrophy",
        "workout": (
            "Mon: Push – Bench 5x5, OHP 4x8, Flies\n"
            "Tue: Pull – Deadlift 4x6, Rows, Curls\n"
            "Wed: Legs – Squat 5x5, Leg Press, Lunges\n"
            "Thu: Push – Incline Press, Dips\n"
            "Fri: Pull – Barbell Rows, Pull-ups\n"
            "Sat: Legs – Front Squat, RDL"
        ),
        "diet": (
            "Breakfast: 4 Eggs + PB Oats\n"
            "Lunch: Chicken Biryani (250g Chicken)\n"
            "Dinner: Mutton Curry + Jeera Rice\n"
            "Target: ~3200 kcal"
        ),
    },
    "beginner": {
        "name": "Beginner (BG)",
        "factor": 26,
        "description": "3-day simple beginner full-body",
        "workout": (
            "Full-Body Circuit (3 days/week):\n"
            "- Air Squats 3x15\n"
            "- Ring Rows 3x10\n"
            "- Push-ups 3x12\n"
            "- Plank 3x30s\n"
            "Focus: Technique mastery & consistency"
        ),
        "diet": (
            "Balanced Meals:\n"
            "Idli / Dosa / Chapati + Dal\n"
            "Protein Target: 120 g/day"
        ),
    },
}


# ─────────────────────────────────────────────
# Utility helpers
# ─────────────────────────────────────────────


def calculate_calories(weight: float, program_key: str) -> int:
    """Return estimated daily calories = weight × programme factor."""
    program = PROGRAMS.get(program_key)
    if program is None:
        raise ValueError(f"Unknown programme: {program_key}")
    if weight <= 0:
        raise ValueError("Weight must be positive")
    return int(weight * program["factor"])


def calculate_bmi(weight: float, height_cm: float) -> float:
    """Return BMI = weight / (height_m²).  Height supplied in cm."""
    if height_cm <= 0:
        raise ValueError("Height must be positive")
    if weight <= 0:
        raise ValueError("Weight must be positive")
    height_m = height_cm / 100.0
    return round(weight / (height_m ** 2), 2)


def bmi_category(bmi: float) -> str:
    """Return a human-readable BMI category string."""
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


# ─────────────────────────────────────────────
# HTML template (single-page)
# ─────────────────────────────────────────────


INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ACEest Fitness &amp; Gym</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
               background: #1a1a1a; color: #eee; }
        header { background: #d4af37; color: #000; text-align: center; padding: 1.2rem; }
        header h1 { font-size: 2rem; }
        .container { max-width: 1100px; margin: 2rem auto; padding: 0 1rem; }
        .card { background: #2a2a2a; border-radius: 10px; padding: 1.5rem;
                margin-bottom: 1.5rem; }
        .card h2 { color: #d4af37; margin-bottom: .8rem; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1.2rem; }
        .program { background: #333; border-radius: 8px; padding: 1rem;
                   transition: transform .2s; }
        .program:hover { transform: translateY(-4px); }
        .program h3 { color: #d4af37; }
        pre { white-space: pre-wrap; color: #ccc; font-size: .9rem; }
        footer { text-align: center; padding: 1rem; color: #666; font-size: .85rem; }
    </style>
</head>
<body>
    <header>
        <h1>ACEest Functional Fitness &amp; Gym</h1>
        <p>Your journey to peak performance starts here</p>
    </header>
    <div class="container">
        <div class="card">
            <h2>Our Programmes</h2>
            <div class="grid">
                {% for key, p in programs.items() %}
                <div class="program">
                    <h3>{{ p.name }}</h3>
                    <p><em>{{ p.description }}</em></p>
                    <h4 style="margin-top:.6rem; color:#aaa;">Workout</h4>
                    <pre>{{ p.workout }}</pre>
                    <h4 style="margin-top:.6rem; color:#aaa;">Nutrition</h4>
                    <pre>{{ p.diet }}</pre>
                </div>
                {% endfor %}
            </div>
        </div>
        <div class="card">
            <h2>Quick Stats</h2>
            <p>Capacity: <strong>150 users</strong> &nbsp;|&nbsp;
               Area: <strong>10 000 sq ft</strong> &nbsp;|&nbsp;
               Break-even: <strong>250 members</strong></p>
        </div>
    </div>
    <footer>&copy; 2026 ACEest Fitness &amp; Gym. All rights reserved.</footer>
</body>
</html>
"""

# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────


@app.route("/")
def index():
    """Render the home page with programme information."""
    return render_template_string(INDEX_HTML, programs=PROGRAMS)


@app.route("/health")
def health():
    """Health-check endpoint used by Docker / CI."""
    return jsonify({"status": "healthy", "app": "ACEest Fitness & Gym"})


# --- Programmes -----------------------------------------------------------

@app.route("/api/programs", methods=["GET"])
def get_programs():
    """Return all available fitness programmes."""
    return jsonify(PROGRAMS)


@app.route("/api/programs/<program_key>", methods=["GET"])
def get_program(program_key):
    """Return details for a single programme."""
    program = PROGRAMS.get(program_key)
    if program is None:
        return jsonify({"error": "Programme not found"}), 404
    return jsonify(program)


# --- Calorie Calculator ----------------------------------------------------

@app.route("/api/calculate_calories", methods=["POST"])
def api_calculate_calories():
    """Calculate daily calories.  Expects JSON {weight, program_key}."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    weight = data.get("weight")
    program_key = data.get("program_key")

    if weight is None or program_key is None:
        return jsonify({"error": "weight and program_key are required"}), 400

    try:
        calories = calculate_calories(float(weight), program_key)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"calories": calories, "program_key": program_key, "weight": weight})


# --- BMI Calculator --------------------------------------------------------

@app.route("/api/bmi", methods=["POST"])
def api_bmi():
    """Calculate BMI.  Expects JSON {weight, height_cm}."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    weight = data.get("weight")
    height_cm = data.get("height_cm")

    if weight is None or height_cm is None:
        return jsonify({"error": "weight and height_cm are required"}), 400

    try:
        bmi = calculate_bmi(float(weight), float(height_cm))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({
        "bmi": bmi,
        "category": bmi_category(bmi),
        "weight": weight,
        "height_cm": height_cm,
    })


# --- Client CRUD ----------------------------------------------------------

@app.route("/api/clients", methods=["GET"])
def list_clients():
    """Return all registered clients."""
    return jsonify(list(clients_db.values()))


@app.route("/api/clients", methods=["POST"])
def create_client():
    """Register a new client.  Expects JSON {name, age, weight, height_cm, program_key}."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    name = data.get("name")
    if not name:
        return jsonify({"error": "name is required"}), 400
    if name in clients_db:
        return jsonify({"error": "Client already exists"}), 409

    age = data.get("age")
    weight = data.get("weight")
    height_cm = data.get("height_cm")
    program_key = data.get("program_key", "beginner")

    try:
        calories = calculate_calories(float(weight), program_key) if weight else None
        bmi = calculate_bmi(float(weight), float(height_cm)) if (weight and height_cm) else None
    except ValueError:
        calories = None
        bmi = None

    client = {
        "name": name,
        "age": age,
        "weight": weight,
        "height_cm": height_cm,
        "program_key": program_key,
        "calories": calories,
        "bmi": bmi,
        "bmi_category": bmi_category(bmi) if bmi else None,
    }
    clients_db[name] = client
    return jsonify(client), 201


@app.route("/api/clients/<name>", methods=["GET"])
def get_client(name):
    """Retrieve a single client by name."""
    client = clients_db.get(name)
    if client is None:
        return jsonify({"error": "Client not found"}), 404
    return jsonify(client)


@app.route("/api/clients/<name>", methods=["DELETE"])
def delete_client(name):
    """Remove a client by name."""
    if name not in clients_db:
        return jsonify({"error": "Client not found"}), 404
    del clients_db[name]
    return jsonify({"message": f"Client '{name}' deleted"}), 200


# ─────────────────────────────────────────────
# Entrypoint
# ─────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
