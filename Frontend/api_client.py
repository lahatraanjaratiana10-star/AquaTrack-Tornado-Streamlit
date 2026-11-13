import requests

API_URL = "http://127.0.0.1:8888/api"


def login_user(username, password):
  return requests.post(
      f"{API_URL}/login", json={"username": username, "password": password}
  )


def register_user(username, password, weight):
  return requests.post(
      f"{API_URL}/register",
      json={"username": username, "password": password, "weight": weight},
  )


def get_consumption_data(username):
  res = requests.get(f"{API_URL}/consumption", params={"username": username})
  return res.json()


def add_consumption(username, drink_type, amount_ml):
  requests.post(
      f"{API_URL}/consumption",
      json={
          "username": username,
          "drink_type": drink_type,
          "amount_ml": amount_ml,
      },
  )


def delete_consumption(item_id):
  requests.delete(f"{API_URL}/consumption", params={"id": item_id})


def update_profile(username, weight_kg, daily_goal):
  requests.post(
      f"{API_URL}/profile",
      json={
          "username": username,
          "weight_kg": weight_kg,
          "daily_goal": daily_goal,
      },
  )