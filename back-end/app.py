from flask import Flask, request, jsonify, Response
from flask_jwt_extended import JWTManager, create_access_token, decode_token
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import mysql.connector
from datetime import datetime
import csv
import io
import os
import bcrypt

app = Flask(__name__)
CORS(app)
app.config["JWT_SECRET_KEY"] = "supersecretkey"
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

BASE_URL = "/api"
token_blocklist = set()

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'Tolls'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

def verify_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT password_hash, operator FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    conn.close()
    if user and bcrypt.check_password_hash(user['password_hash'], password):
        return {
            "username": username,
            "operator": user["operator"]
        }
    return None

def custom_jwt_required():
    auth_header = request.headers.get("Authorization") or request.headers.get("X-OBSERVATORY-AUTH")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"msg": "Missing or invalid Authorization Header"}), 401

    token = auth_header.split(" ")[1]
    try:
        decoded_token = decode_token(token)
        if decoded_token["jti"] in token_blocklist:
            return jsonify({"msg": "Token has been revoked"}), 401
        return decoded_token
    except Exception:
        return jsonify({"msg": "Invalid token"}), 401

def authorize_access(decoded_token, station_id):
    if decoded_token["sub"] == "admin":
        return True

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  
    cursor.execute("SELECT opid FROM toll_stations WHERE toll_id = %s", (station_id,))
    station_owner = cursor.fetchone()

    return decoded_token["sub"] == station_owner['opid']

def empty_response(format_type):
    if format_type == "json":
        return jsonify({
            "stationID": "",
            "stationOperator": "",
            "requestTimestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "periodFrom": "",
            "periodTo": "",
            "nPasses": 0,
            "passList": []
        }), 200
    else:
        return Response("", mimetype="text/csv")

def admin_required(decoded_token):
    """Ensure the user is an admin"""
    if isinstance(decoded_token, tuple):
        return decoded_token  # Return error response if token is invalid
    if decoded_token["sub"] != "admin":
        return jsonify({"error": "Unauthorized"}), 401
    return None

@app.route(BASE_URL + "/login", methods=["POST"])
def login_route():
    username = request.form.get("username")
    password = request.form.get("password")
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    
    user_info = verify_user(username, password)
    if user_info:
        access_token = create_access_token(
            identity=user_info["username"],  # Set identity to username (string)
            additional_claims={"operator": user_info["operator"]}  # Add operator as a claim
        )
        return jsonify({"token": access_token})
    return jsonify({"error": "Invalid username or password"}), 401

@app.route(BASE_URL + "/logout", methods=["POST"])
def logout_route():
    decoded_token = custom_jwt_required()
    if isinstance(decoded_token, tuple):
        return decoded_token
    jti = decoded_token["jti"]
    token_blocklist.add(jti)
    return "", 200

@app.route(BASE_URL + "/tollstations", methods=["GET"])
def get_tollstations():
    # Έλεγχος authentication με το JWT
    decoded_token = custom_jwt_required()
    if isinstance(decoded_token, tuple):
        # Επιστρέφει το σφάλμα που δημιουργεί η συνάρτηση αν υπάρχει πρόβλημα με το token
        return decoded_token

    # Λαμβάνουμε το username από το token (η συνάρτηση create_access_token θέτει το sub ως username)
    username = decoded_token["sub"]

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Εάν ο χρήστης είναι admin, επιλέγουμε όλους τους σταθμούς
        if username == "admin":
            query = "SELECT toll_id AS TollID, name FROM toll_stations"
            cursor.execute(query)
        else:
            # Εάν ο χρήστης δεν είναι admin, επιστρέφουμε μόνο τους σταθμούς που έχουν opid ίσο με το username
            query = "SELECT toll_id AS TollID, name FROM toll_stations WHERE opid = %s"
            
            cursor.execute(query, (username,))
        
        stations = cursor.fetchall()
        conn.close()
        return jsonify(stations), 200

    except mysql.connector.Error as err:
        return jsonify({"status": "failed", "info": str(err)}), 500



@app.route(BASE_URL + "/admin/users", methods=["GET"])
def get_users():
    """Admin-only: List all users with customizable output format"""
    decoded_token = custom_jwt_required()
    if isinstance(decoded_token, tuple):
        return decoded_token  # Authentication failed
    if decoded_token["sub"] != "admin":
        return jsonify({"error": "Unauthorized"}), 401
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Removed opID from the query
        cursor.execute("SELECT id, username FROM users ORDER BY id ASC")
        users = cursor.fetchall()
        conn.close()
        output_format = request.args.get("format", "json").lower()
        if output_format == "json":
            return jsonify({"status": "OK", "users": users}), 200
        else:
            si = io.StringIO()
            writer = csv.writer(si)
            writer.writerow(["id", "username"])  # CSV header without opid
            for user in users:
                writer.writerow([user["id"], user["username"]])
            output = si.getvalue()
            return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=users.csv"})
    except mysql.connector.Error as err:
        return jsonify({"status": "failed", "info": str(err)}), 500

@app.route(BASE_URL + "/passAnalysis/<string:stationOpID>/<string:tagOpID>/<string:date_from>/<string:date_to>", methods=["GET"])
def get_pass_analysis_route(stationOpID, tagOpID, date_from, date_to):
    """Retrieve pass details for a specific station operator and tag operator within a date range"""
    decoded_token = custom_jwt_required()
    if isinstance(decoded_token, tuple):
        return decoded_token
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        date_from = datetime.strptime(date_from, "%Y%m%d").strftime("%Y-%m-%d")
        date_to = datetime.strptime(date_to, "%Y%m%d").strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT p.id AS passID, p.timestamp, p.tag_ref AS tagID, 
                   p.charge AS passCharge, ts.toll_id AS stationID
            FROM passes p
            JOIN toll_stations ts ON p.toll_id = ts.toll_id
            WHERE ts.opid = %s AND p.tag_home_id = %s
                  AND DATE(p.timestamp) BETWEEN %s AND %s
            ORDER BY p.timestamp ASC
        """, (stationOpID, tagOpID, date_from, date_to))
        passes = cursor.fetchall()
        conn.close()
        response = {
            "stationOpID": stationOpID,
            "tagOpID": tagOpID,
            "requestTimestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "periodFrom": date_from,
            "periodTo": date_to,
            "nPasses": len(passes),
            "passList": [
                {
                    "passIndex": idx + 1,
                    "passID": p["passID"],
                    "stationID": p["stationID"],
                    "timestamp": p["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                    "tagID": p["tagID"],
                    "passCharge": float(p["passCharge"])
                }
                for idx, p in enumerate(passes)
            ]
        }
        output_format = request.args.get("format", "json")
        if output_format == "json":
            return jsonify(response), 200
        else:
            csv_output = io.StringIO()
            writer = csv.writer(csv_output)
            writer.writerow(["passIndex", "passID", "stationID", "timestamp", "tagID", "passCharge"])
            for p in response["passList"]:
                writer.writerow([p["passIndex"], p["passID"], p["stationID"], p["timestamp"], p["tagID"], p["passCharge"]])
            return Response(csv_output.getvalue(), mimetype="text/csv")
    except mysql.connector.Error as err:
        return jsonify({"status": "failed", "info": str(err)}), 500

@app.route(BASE_URL + "/passesCost/<string:tollOpID>/<string:tagOpID>/<string:date_from>/<string:date_to>", methods=["GET"])
def get_passes_cost_route(tollOpID, tagOpID, date_from, date_to):
    """Retrieve total number of passes and cost between two operators in a date range"""
    decoded_token = custom_jwt_required()
    if isinstance(decoded_token, tuple):
        return decoded_token
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        date_from = datetime.strptime(date_from, "%Y%m%d").strftime("%Y-%m-%d")
        date_to = datetime.strptime(date_to, "%Y%m%d").strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT COUNT(*) AS nPasses, SUM(p.charge) AS passesCost
            FROM passes p
            JOIN toll_stations ts ON p.toll_id = ts.toll_id
            WHERE ts.opid = %s AND p.tag_home_id = %s
                  AND DATE(p.timestamp) BETWEEN %s AND %s
        """, (tollOpID, tagOpID, date_from, date_to))
        result = cursor.fetchone()
        conn.close()
        response = {
            "tollOpID": tollOpID,
            "tagOpID": tagOpID,
            "requestTimestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "periodFrom": date_from,
            "periodTo": date_to,
            "nPasses": result["nPasses"] or 0,
            "passesCost": float(result["passesCost"] or 0)
        }
        output_format = request.args.get("format", "json")
        if output_format == "json":
            return jsonify(response), 200
        else:
            return Response(f"tollOpID,tagOpID,requestTimestamp,periodFrom,periodTo,nPasses,passesCost\n"
                            f"{tollOpID},{tagOpID},{response['requestTimestamp']},{date_from},{date_to},"
                            f"{response['nPasses']},{response['passesCost']}",
                            mimetype="text/csv")
    except mysql.connector.Error as err:
        return jsonify({"status": "failed", "info": str(err)}), 500


@app.route(BASE_URL + "/admin/usermod", methods=["POST"])
def usermod():
    decoded_token = custom_jwt_required()
    if isinstance(decoded_token, tuple):
        return decoded_token
    if decoded_token["sub"] != "admin":
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    username = data.get("username")
    password = data.get("password")
    operator = data.get("operator")

    if not all([username, password]):
        return jsonify({"error": "Username and password required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)  # <-- FIX HERE

    try:
        if operator:
            cursor.execute("SELECT toll_id FROM toll_stations WHERE opid = %s", (username,))
            if not cursor.fetchone():
                return jsonify({"error": "Invalid operator ID"}), 400

        password_hash = bcrypt.generate_password_hash(password.encode("utf-8")).decode("utf-8")
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user:
            cursor.execute("""
                UPDATE users 
                SET password_hash = %s, operator = %s
                WHERE username = %s
            """, (password_hash, operator, username))
            action = "updated"
        else:
            cursor.execute("""
                INSERT INTO users (username, password_hash, operator) 
                VALUES (%s, %s, %s)
            """, (username, password_hash, operator))
            action = "created"

        conn.commit()
        return jsonify({"status": "OK", "info": f"User {username} {action} successfully"}), 200

    except mysql.connector.Error as err:
        return jsonify({"status": "failed", "info": str(err)}), 500
    finally:
        conn.close()

@app.route(BASE_URL + "/tollStationPasses/<string:tollStationID>/<string:date_from>/<string:date_to>", methods=["GET"])
def get_toll_station_passes_route(tollStationID, date_from, date_to):
    decoded_token = custom_jwt_required()
    if isinstance(decoded_token, tuple):
        return decoded_token

    if not authorize_access(decoded_token, tollStationID):
        return empty_response(request.args.get("format", "csv"))

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        date_from = datetime.strptime(date_from, "%Y%m%d").strftime("%Y-%m-%d")
        date_to = datetime.strptime(date_to, "%Y%m%d").strftime("%Y-%m-%d")
        
        cursor.execute("SELECT operator FROM toll_stations WHERE toll_id = %s", (tollStationID,))
        station_info = cursor.fetchone()
        if not station_info:
            return jsonify({"status": "failed", "info": "Toll station not found"}), 404

        cursor.execute("""
            SELECT distinct
    p.id AS passID, 
    p.timestamp, 
    p.tag_ref AS tagID, 
    ts_provider.operator AS tagProvider, 
    CASE 
        WHEN ts_provider.operator = ts_input.operator THEN 'home' 
        ELSE 'visitor' 
    END AS passType,
    p.charge AS passCharge
FROM passes p
JOIN toll_stations ts_input ON ts_input.toll_id = %s  -- Get the operator of the input toll_id
JOIN toll_stations ts ON p.toll_id = ts.toll_id
JOIN toll_stations ts_provider ON p.tag_home_id = ts_provider.opid  -- Get tagProvider using tag_home_id
WHERE p.toll_id = %s 
AND DATE(p.timestamp) BETWEEN %s AND %s
ORDER BY p.timestamp ASC;



        """, (tollStationID, tollStationID, date_from, date_to))
        passes = cursor.fetchall()
        conn.close()

        response = {
            "stationID": tollStationID,
            "stationOperator": station_info["operator"],
            "requestTimestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "periodFrom": date_from,
            "periodTo": date_to,
            "nPasses": len(passes),
            "passList": [
                {
                    "passIndex": idx + 1,
                    "passID": p["passID"],
                    "timestamp": p["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                    "tagID": p["tagID"],
                    "tagProvider": p["tagProvider"],
                    "passType": p["passType"],
                    "passCharge": float(p["passCharge"])
                }
                for idx, p in enumerate(passes)
            ]
        }
        
        output_format = request.args.get("format", "json")
        if output_format == "json":
            return jsonify(response), 200
        else:
            csv_output = io.StringIO()
            writer = csv.writer(csv_output)
            writer.writerow(["passIndex", "passID", "timestamp", "tagID", "tagProvider", "passType", "passCharge"])
            for p in response["passList"]:
                writer.writerow([p["passIndex"], p["passID"], p["timestamp"], p["tagID"], p["tagProvider"], p["passType"], p["passCharge"]])
            return Response(csv_output.getvalue(), mimetype="text/csv")

    except mysql.connector.Error as err:
        return jsonify({"status": "failed", "info": str(err)}), 500

@app.route(BASE_URL + "/admin/healthcheck", methods=["GET"])
def healthcheck():
    """Check system health"""
    decoded_token = custom_jwt_required()
    if isinstance(decoded_token, tuple):
        return decoded_token
    if decoded_token["sub"] != "admin":
        return jsonify({"error": "Unauthorized"}), 401

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check database connection
        cursor.execute("SELECT 1")
        db_status = "OK" if cursor.fetchone() else "Failed"

        # Check table status
        cursor.execute("SHOW TABLES LIKE 'passes'")
        passes_table = "OK" if cursor.fetchone() else "Missing"

        cursor.execute("SHOW TABLES LIKE 'toll_stations'")
        stations_table = "OK" if cursor.fetchone() else "Missing"

        cursor.execute("SHOW TABLES LIKE 'users'")
        users_table = "OK" if cursor.fetchone() else "Missing"

        conn.close()

        return jsonify({
            "status": "OK",
            "dbconnection": db_status,
            "tables": {
                "passes": passes_table,
                "toll_stations": stations_table,
                "users": users_table
            }
        }), 200

    except mysql.connector.Error as err:
        return jsonify({"status": "failed", "info": str(err)}), 500

@app.route(BASE_URL + "/admin/resetpasses", methods=["POST"])
def reset_passes():
    """Reset the passes table"""
    decoded_token = custom_jwt_required()
    if isinstance(decoded_token, tuple):
        return decoded_token
    if decoded_token["sub"] != "admin":
        return jsonify({"error": "Unauthorized"}), 401

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Truncate the passes table
        cursor.execute("TRUNCATE TABLE passes")
        conn.commit()
        conn.close()

        return jsonify({"status": "OK", "info": "Passes table reset successfully"}), 200

    except mysql.connector.Error as err:
        return jsonify({"status": "failed", "info": str(err)}), 500

@app.route(BASE_URL + "/admin/addpasses", methods=["POST"])
def add_passes():
    """Admin-only: Upload a CSV file to add new passes"""
    decoded_token = custom_jwt_required()
    admin_check = admin_required(decoded_token)
    if admin_check:
        return admin_check
    if "file" not in request.files:
        return jsonify({"status": "failed", "info": "No file provided"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"status": "failed", "info": "Empty filename"}), 400
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        stream = io.StringIO(file.stream.read().decode("utf-8"))
        reader = csv.reader(stream)
        next(reader)  # Skip header row
        skipped_passes = set()
        for row in reader:
            toll_id = row[1]
            cursor.execute("SELECT COUNT(*) FROM toll_stations WHERE toll_id = %s", (toll_id,))
            exists = cursor.fetchone()[0]
            if exists:
                cursor.execute("""
                    INSERT INTO passes (timestamp, toll_id, tag_ref, tag_home_id, charge)
                    VALUES (%s, %s, %s, %s, %s)
                """, row)
            else:
                skipped_passes.add(toll_id)
        conn.commit()
        conn.close()
        if skipped_passes:
            return jsonify({"status": "partial", "info": f"Some passes were skipped due to missing toll_id: {skipped_passes}"}), 206
        else:
            return jsonify({"status": "OK"}), 200
    except mysql.connector.Error as err:
        return jsonify({"status": "failed", "info": str(err)}), 500

@app.route(BASE_URL + "/chargesBy/<string:tollOpID>/<string:date_from>/<string:date_to>", methods=["GET"])
def get_charges_by_route(tollOpID, date_from, date_to):
    """Retrieve charges owed by other operators to the toll operator"""
    decoded_token = custom_jwt_required()
    if isinstance(decoded_token, tuple):
        return decoded_token
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        date_from = datetime.strptime(date_from, "%Y%m%d").strftime("%Y-%m-%d")
        date_to = datetime.strptime(date_to, "%Y%m%d").strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT p.tag_home_id AS visitingOpID, COUNT(*) AS nPasses, SUM(p.charge) AS passesCost
            FROM passes p
            JOIN toll_stations ts ON p.toll_id = ts.toll_id
            WHERE ts.opid = %s AND p.tag_home_id <> ts.opid
                  AND DATE(p.timestamp) BETWEEN %s AND %s
            GROUP BY p.tag_home_id
        """, (tollOpID, date_from, date_to))
        charges = cursor.fetchall()
        conn.close()
        response = {
            "tollOpID": tollOpID,
            "requestTimestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "periodFrom": date_from,
            "periodTo": date_to,
            "vOpList": [
                {
                    "visitingOpID": c["visitingOpID"],
                    "nPasses": c["nPasses"],
                    "passesCost": float(c["passesCost"])
                }
                for c in charges
            ]
        }
        output_format = request.args.get("format", "json")
        if output_format == "json":
            return jsonify(response), 200
        else:
            csv_output = io.StringIO()
            writer = csv.writer(csv_output)
            writer.writerow(["visitingOpID", "nPasses", "passesCost"])
            for c in response["vOpList"]:
                writer.writerow([c["visitingOpID"], c["nPasses"], c["passesCost"]])
            return Response(csv_output.getvalue(), mimetype="text/csv")
    except mysql.connector.Error as err:
        return jsonify({"status": "failed", "info": str(err)}), 500


@app.route(BASE_URL + "/user-info", methods=["GET"])
def get_user_info():
    decoded_token = custom_jwt_required()
    if isinstance(decoded_token, tuple):
        return decoded_token
    
    username = decoded_token["sub"]
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT operator FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        return jsonify({
            "username": username,
            "operator": user["operator"]
        }), 200
        
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        conn.close()

@app.route(BASE_URL + "/admin/resetstations", methods=["POST"])
def reset_stations():
    """Admin-only: Reset toll stations from CSV file"""
    decoded_token = custom_jwt_required()
    admin_check = admin_required(decoded_token)
    if admin_check:
        return admin_check
    csv_file = "tollstations2024.csv"
    if not os.path.exists(csv_file):
        return jsonify({"status": "failed", "info": "CSV file not found"}), 400
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM passes")
        cursor.execute("DELETE FROM toll_stations")
        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                cursor.execute("""
                    INSERT INTO toll_stations 
                    (opid, operator, toll_id, name, payment_method, locality, road, latitude, longitude, email, price1, price2, price3, price4) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, row)
        conn.commit()
        conn.close()
        return jsonify({"status": "OK"}), 200
    except mysql.connector.Error as err:
        return jsonify({"status": "failed", "info": str(err)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=9115, host="0.0.0.0")