"""
ACEest Fitness & Gym - Flask Web Application
A fitness and gym management web application built with Flask.
"""

from flask import Flask, jsonify, request, render_template_string
import logging

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ============================================================================
# DATA STORAGE
# ============================================================================

clients_db = {}

# ============================================================================
# CONSTANTS - Fitness Programmes
# ============================================================================

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

# ============================================================================
# UTILITY HELPER FUNCTIONS - Business Logic
# ============================================================================


def calculate_calories(weight: float, program_key: str) -> int:
    """Return estimated daily calories = weight × programme factor.

    Calculates calorie requirement by multiplying body weight by
    the programme-specific calorie factor.

    Args:
        weight: Body weight in kilograms (must be > 0)
        program_key: Key of fitness programme (see PROGRAMS)

    Returns:
        Estimated daily calories as integer

    Raises:
        ValueError: If weight <= 0 or programme doesn't exist

    Example:
        >>> calculate_calories(80, "muscle_gain_ppl")
        2800
    """
    # Type validation
    if not isinstance(weight, (int, float)):
        raise ValueError(
            f"Weight must be a number, got {type(weight).__name__}"
        )
    if not isinstance(program_key, str):
        raise ValueError(
            f"Programme key must be string, got {type(program_key).__name__}"
        )

    # Normalize and lookup programme
    program_key_normalized = program_key.lower().strip()
    program = PROGRAMS.get(program_key_normalized)

    # Validate programme exists
    if program is None:
        valid_keys = ", ".join(PROGRAMS.keys())
        raise ValueError(
            f"Unknown programme: '{program_key}'. Valid options: {valid_keys}"
        )

    # Validate weight is positive
    if weight <= 0:
        raise ValueError(f"Weight must be positive (received: {weight} kg)")

    # Calculate calories using programme factor
    calories = int(weight * program["factor"])
    return calories


def calculate_bmi(weight: float, height_cm: float) -> float:
    """Return BMI = weight / (height_m²). Height supplied in cm.

    Calculates Body Mass Index from weight and height.
    Formula: BMI = weight(kg) / (height(m))²

    Args:
        weight: Body weight in kilograms (must be > 0)
        height_cm: Height in centimeters (must be > 0)

    Returns:
        BMI value rounded to 2 decimal places

    Raises:
        ValueError: If weight or height <= 0

    Example:
        >>> calculate_bmi(75, 180)
        23.15
    """
    # Validate height
    if height_cm <= 0:
        raise ValueError(
            f"Height must be positive (received: {height_cm} cm)"
        )

    # Validate weight
    if weight <= 0:
        raise ValueError(f"Weight must be positive (received: {weight} kg)")

    # Convert height to meters and calculate BMI
    height_m = height_cm / 100.0
    bmi_value = round(weight / (height_m ** 2), 2)
    return bmi_value


def bmi_category(bmi: float) -> str:
    """Return a human-readable BMI category string.

    Categorizes BMI value into health categories according to
    WHO standards.

    Args:
        bmi: BMI value to categorize

    Returns:
        Category string: "Underweight", "Normal weight", "Overweight", or "Obese"

    Example:
        >>> bmi_category(23.15)
        "Normal weight"
    """
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


# ============================================================================
# HTML TEMPLATE - Web UI
# ============================================================================

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

# ============================================================================
# API ROUTES - RESTful Endpoints
# ============================================================================


@app.route("/")
def index():
    """Render the home page with programme information."""
    logger.info("Home page accessed")
    return render_template_string(INDEX_HTML, programs=PROGRAMS)


@app.route("/health")
def health():
    """Health-check endpoint used by Docker / CI."""
    logger.debug("Health check requested")
    return jsonify({"status": "healthy", "app": "ACEest Fitness & Gym"})


# --- Programmes Endpoints ---


@app.route("/api/programs", methods=["GET"])
def get_programs():
    """Return all available fitness programmes.

    GET /api/programs

    Returns:
        JSON: Dictionary of all programmes with full details
    """
    logger.info("All programmes requested")
    return jsonify(PROGRAMS)


@app.route("/api/programs/<program_key>", methods=["GET"])
def get_program(program_key):
    """Return details for a single programme.

    GET /api/programs/<program_key>

    Args:
        program_key: Key of the programme to retrieve

    Returns:
        JSON: Programme details
        HTTP 404: If programme not found
    """
    logger.info(f"Programme requested: {program_key}")
    program = PROGRAMS.get(program_key)
    if program is None:
        logger.warning(f"Programme not found: {program_key}")
        return jsonify({"error": "Programme not found"}), 404
    return jsonify(program)


# --- Calorie Calculator Endpoint ---


@app.route("/api/calculate_calories", methods=["POST"])
def api_calculate_calories():
    """Calculate daily calories based on weight and programme.

    POST /api/calculate_calories

    Request JSON:
        weight (float): Body weight in kilograms
        program_key (str): Fitness programme key

    Returns:
        JSON: {calories, program_key, weight}
        HTTP 400: Invalid or missing parameters

    Example:
        {"weight": 80, "program_key": "muscle_gain_ppl"}
        Returns: {"calories": 2800, "program_key": "muscle_gain_ppl", "weight": 80}
    """
    logger.info(f"Calorie calculation requested from {request.remote_addr}")

    # Parse JSON body
    data = request.get_json(silent=True)
    if not data:
        logger.warning("JSON body missing in calorie calculation request")
        return jsonify({"error": "JSON body required"}), 400

    # Extract parameters
    weight = data.get("weight")
    program_key = data.get("program_key")

    # Validate required fields
    if weight is None or program_key is None:
        logger.warning(
            f"Missing parameters - weight: {weight}, program_key: {program_key}"
        )
        return jsonify(
            {"error": "weight and program_key are required"}
        ), 400

    # Calculate and handle errors
    try:
        calories = calculate_calories(float(weight), program_key)
        logger.info(
            f"Calculated {calories} calories for {weight}kg, "
            f"programme: {program_key}"
        )
    except ValueError as exc:
        logger.error(f"Calorie calculation error: {str(exc)}")
        return jsonify({"error": str(exc)}), 400

    # Return successful response
    return jsonify({
        "calories": calories,
        "program_key": program_key,
        "weight": weight
    })


# --- BMI Calculator Endpoint ---


@app.route("/api/bmi", methods=["POST"])
def api_bmi():
    """Calculate BMI and categorize health status.

    POST /api/bmi

    Request JSON:
        weight (float): Body weight in kilograms
        height_cm (float): Height in centimeters

    Returns:
        JSON: {bmi, category, weight, height_cm}
        HTTP 400: Invalid or missing parameters

    Example:
        {"weight": 75, "height_cm": 180}
        Returns: {"bmi": 23.15, "category": "Normal weight", ...}
    """
    logger.info(f"BMI calculation requested from {request.remote_addr}")

    # Parse JSON body
    data = request.get_json(silent=True)
    if not data:
        logger.warning("JSON body missing in BMI calculation request")
        return jsonify({"error": "JSON body required"}), 400

    # Extract parameters
    weight = data.get("weight")
    height_cm = data.get("height_cm")

    # Validate required fields
    if weight is None or height_cm is None:
        logger.warning(
            f"Missing parameters - weight: {weight}, height_cm: {height_cm}"
        )
        return jsonify(
            {"error": "weight and height_cm are required"}
        ), 400

    # Calculate and handle errors
    try:
        bmi = calculate_bmi(float(weight), float(height_cm))
        category = bmi_category(bmi)
        logger.info(
            f"Calculated BMI {bmi} ({category}) for {weight}kg, {height_cm}cm"
        )
    except ValueError as exc:
        logger.error(f"BMI calculation error: {str(exc)}")
        return jsonify({"error": str(exc)}), 400

    # Return successful response
    return jsonify({
        "bmi": bmi,
        "category": category,
        "weight": weight,
        "height_cm": height_cm,
    })


# --- Client CRUD Endpoints ---


@app.route("/api/clients", methods=["GET"])
def list_clients():
    """Return all registered clients.

    GET /api/clients

    Returns:
        JSON: Array of client profiles
    """
    logger.info(f"List clients requested. Total: {len(clients_db)}")
    return jsonify(list(clients_db.values()))


@app.route("/api/clients", methods=["POST"])
def create_client():
    """Register a new client with profile information.

    POST /api/clients

    Request JSON:
        name (str, required): Unique client name
        age (int, optional): Client age
        weight (float, optional): Weight in kg
        height_cm (float, optional): Height in cm
        program_key (str, optional): Programme (default: "beginner")

    Returns:
        JSON: Created client profile (HTTP 201)
        HTTP 400: Missing or invalid parameters
        HTTP 409: Client name already exists
    """
    logger.info(f"Create client requested from {request.remote_addr}")

    # Parse JSON body
    data = request.get_json(silent=True)
    if not data:
        logger.warning("JSON body missing in create client request")
        return jsonify({"error": "JSON body required"}), 400

    # Extract and validate name
    name = data.get("name")
    if not name:
        logger.warning("Client name missing")
        return jsonify({"error": "name is required"}), 400

    # Check for duplicate
    if name in clients_db:
        logger.warning(f"Duplicate client name: {name}")
        return jsonify({"error": "Client already exists"}), 409

    # Extract optional fields
    age = data.get("age")
    weight = data.get("weight")
    height_cm = data.get("height_cm")
    program_key = data.get("program_key", "beginner")

    # Calculate derived fields
    try:
        calories = calculate_calories(
            float(weight), program_key
        ) if weight else None
        bmi = calculate_bmi(
            float(weight), float(height_cm)
        ) if (weight and height_cm) else None
    except ValueError:
        calories = None
        bmi = None

    # Create client record
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

    # Store and log
    clients_db[name] = client
    logger.info(f"Created new client: {name}")
    return jsonify(client), 201


@app.route("/api/clients/<name>", methods=["GET"])
def get_client(name):
    """Retrieve a single client by name.

    GET /api/clients/<name>

    Args:
        name: Client name (URL parameter)

    Returns:
        JSON: Client profile
        HTTP 404: Client not found
    """
    logger.info(f"Get client requested: {name}")
    client = clients_db.get(name)
    if client is None:
        logger.warning(f"Client not found: {name}")
        return jsonify({"error": "Client not found"}), 404
    return jsonify(client)


@app.route("/api/clients/<name>", methods=["DELETE"])
def delete_client(name):
    """Remove a client by name.

    DELETE /api/clients/<name>

    Args:
        name: Client name (URL parameter)

    Returns:
        JSON: Success message
        HTTP 404: Client not found
    """
    logger.info(f"Delete client requested: {name}")
    if name not in clients_db:
        logger.warning(f"Client not found for deletion: {name}")
        return jsonify({"error": "Client not found"}), 404

    del clients_db[name]
    logger.info(f"Deleted client: {name}")
    return jsonify({"message": f"Client '{name}' deleted"}), 200


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    logger.info("Starting ACEest Fitness & Gym application...")
    app.run(host="0.0.0.0", port=8080, debug=True)
