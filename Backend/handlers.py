import json
import sqlite3
from database import get_connection, hash_password
import tornado.web


class BaseHandler(tornado.web.RequestHandler):

  def set_default_headers(self):
    self.set_header("Access-Control-Allow-Origin", "*")
    self.set_header("Access-Control-Allow-Headers", "Content-Type")
    self.set_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")

  def options(self, *args):
    self.set_status(204)
    self.finish()


class RegisterHandler(BaseHandler):

  def post(self):
    try:
      data = json.loads(self.request.body)
      username = data.get("username", "").strip()
      password = data.get("password", "")
      weight = float(data.get("weight", 65.0))
      goal = int(weight * 35)

      if not username or not password:
        self.set_status(400)
        self.write({"error": "Champs obligatoires manquants"})
        return

      conn = get_connection()
      cursor = conn.cursor()
      cursor.execute(
          "INSERT INTO users (username, password, daily_goal, weight_kg) VALUES"
          " (?, ?, ?, ?)",
          (username, hash_password(password), goal, weight),
      )
      conn.commit()
      conn.close()

      self.set_status(201)
      self.write({"message": "Compte créé", "daily_goal": goal})
    except sqlite3.IntegrityError:
      self.set_status(400)
      self.write({"error": "Nom d'utilisateur déjà pris"})


class LoginHandler(BaseHandler):

  def post(self):
    data = json.loads(self.request.body)
    username = data.get("username", "").strip()
    password = data.get("password", "")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, daily_goal, weight_kg FROM users WHERE username = ?"
        " AND password = ?",
        (username, hash_password(password)),
    )
    user = cursor.fetchone()
    conn.close()

    if user:
      self.write({
          "username": user[0],
          "daily_goal": user[1],
          "weight_kg": user[2],
      })
    else:
      self.set_status(401)
      self.write({"error": "Identifiants incorrects"})


class ProfileHandler(BaseHandler):

  def post(self):
    data = json.loads(self.request.body)
    username = data.get("username")
    daily_goal = int(data.get("daily_goal", 2000))
    weight_kg = float(data.get("weight_kg", 65.0))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET daily_goal = ?, weight_kg = ? WHERE username = ?",
        (daily_goal, weight_kg, username),
    )
    conn.commit()
    conn.close()
    self.write({"message": "Profil mis à jour", "daily_goal": daily_goal})


class ConsumptionHandler(BaseHandler):
  HYDRATION_FACTORS = {
      "💧 Eau plate": 1.0,
      "🫧 Eau gazeuse": 1.0,
      "🍵 Thé / Infusion": 0.95,
      "☕ Café": 0.80,
      "🧃 Jus / Boisson": 0.85,
  }

  def get(self):
    username = self.get_argument("username", "")
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """SELECT id, drink_type, amount_ml, effective_ml, created_at 
           FROM consumptions 
           WHERE username = ? AND date(created_at) = date('now', 'localtime')
           ORDER BY created_at DESC""",
        (username,),
    )
    today_rows = cursor.fetchall()

    cursor.execute(
        """SELECT date(created_at) as day, SUM(effective_ml) as total 
           FROM consumptions 
           WHERE username = ? AND date(created_at) >= date('now', '-6 days', 'localtime')
           GROUP BY day ORDER BY day ASC""",
        (username,),
    )
    weekly_rows = cursor.fetchall()

    cursor.execute(
        "SELECT daily_goal, weight_kg FROM users WHERE username = ?",
        (username,),
    )
    user_info = cursor.fetchone()
    conn.close()

    self.write({
        "daily_goal": user_info[0] if user_info else 2000,
        "weight_kg": user_info[1] if user_info else 65.0,
        "total_raw": sum(r[2] for r in today_rows),
        "total_effective": sum(r[3] for r in today_rows),
        "today_items": [
            {
                "id": r[0],
                "drink_type": r[1],
                "amount_ml": r[2],
                "effective_ml": r[3],
                "time": r[4].split(" ")[1][:5] if " " in r[4] else r[4],
            }
            for r in today_rows
        ],
        "weekly_stats": [{"date": r[0], "total": r[1]} for r in weekly_rows],
    })

  def post(self):
    data = json.loads(self.request.body)
    username = data.get("username")
    drink_type = data.get("drink_type", "💧 Eau plate")
    amount_ml = int(data.get("amount_ml", 250))

    effective_ml = int(
        amount_ml * self.HYDRATION_FACTORS.get(drink_type, 1.0)
    )

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO consumptions (username, drink_type, amount_ml, effective_ml, created_at)
           VALUES (?, ?, ?, ?, datetime('now', 'localtime'))""",
        (username, drink_type, amount_ml, effective_ml),
    )
    conn.commit()
    conn.close()

    self.set_status(201)
    self.write({"message": "Ajouté", "effective_ml": effective_ml})

  def delete(self):
    item_id = self.get_argument("id", "")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM consumptions WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    self.write({"message": "Supprimé"})