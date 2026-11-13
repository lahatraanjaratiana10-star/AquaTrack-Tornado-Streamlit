from api_client import (
    add_consumption,
    delete_consumption,
    get_consumption_data,
    update_profile,
)
import pandas as pd
import streamlit as st


def render_main_app(username):
  try:
    data = get_consumption_data(username)
  except Exception:
    st.error("Perte de connexion avec le serveur Tornado.")
    st.stop()

  goal = data["daily_goal"]
  effective_ml = data["total_effective"]
  raw_ml = data["total_raw"]
  items = data["today_items"]
  weekly = data["weekly_stats"]
  pct = int((effective_ml / goal) * 100) if goal > 0 else 0

  # --- Barre latérale ---
  with st.sidebar:
    st.title("🌊 AquaTrack Pro")
    st.write(f"Bienvenue, **{username}** 👋")
    st.divider()
    menu = st.radio(
        "Navigation",
        ["📊 Tableau de bord", "📈 Analyses & Graphiques", "⚙️ Objectifs & Profil"],
    )
    st.divider()
    if pct >= 100:
      st.success("🏆 Badge : Maître de l'Hydratation !")
    elif pct >= 50:
      st.info("⚡ Badge : À mi-chemin, continue !")
    else:
      st.warning("🌱 Badge : Pense à boire un verre !")
    st.divider()
    if st.button("🚪 Déconnexion", use_container_width=True):
      st.session_state.user = None
      st.rerun()

  # --- Page 1 : Tableau de bord ---
  if menu == "📊 Tableau de bord":
    st.markdown(
        """
            <div class="main-header">
                <h2>Tableau de bord d'hydratation</h2>
                <p>Chaque boisson a un taux d'hydratation réel différent (Eau = 100%, Café = 80%)</p>
            </div>
        """,
        unsafe_allow_html=True,
    )

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Hydratation Réelle", f"{effective_ml} ml", f"{pct}% de l'objectif")
    k2.metric("Volume Total Bu", f"{raw_ml} ml", f"{len(items)} prises")
    k3.metric("Objectif Quotidien", f"{goal} ml")
    k4.metric("Reste à boire", f"{max(0, goal - effective_ml)} ml")

    st.progress(min(effective_ml / goal, 1.0) if goal > 0 else 0.0)
    st.write("")

    col_add, col_list = st.columns([1, 1.3], gap="large")
    with col_add:
      st.subheader("➕ Ajouter une boisson")
      drink = st.selectbox(
          "Type de boisson",
          [
              "💧 Eau plate",
              "🫧 Eau gazeuse",
              "🍵 Thé / Infusion",
              "☕ Café",
              "🧃 Jus / Boisson",
          ],
      )
      b1, b2, b3 = st.columns(3)
      if b1.button("🥛 200 ml", use_container_width=True):
        add_consumption(username, drink, 200)
        st.rerun()
      if b2.button("🥤 330 ml", use_container_width=True):
        add_consumption(username, drink, 330)
        st.rerun()
      if b3.button("🍼 500 ml", use_container_width=True):
        add_consumption(username, drink, 500)
        st.rerun()

      custom_val = st.slider("Sélectionner en ml", 50, 1500, 250, step=25)
      if st.button("Valider l'ajout", type="primary", use_container_width=True):
        add_consumption(username, drink, custom_val)
        st.rerun()

    with col_list:
      st.subheader("🕒 Journal d'aujourd'hui")
      if not items:
        st.info("Aucune boisson enregistrée aujourd'hui.")
      else:
        for item in items:
          c_info, c_del = st.columns([4, 1])
          c_info.write(
              f"**{item['time']}** — {item['drink_type']} : **{item['amount_ml']} ml** *(hydratation : {item['effective_ml']} ml)*"
          )
          if c_del.button("🗑️", key=f"del_{item['id']}"):
            delete_consumption(item["id"])
            st.rerun()

  # --- Page 2 : Analyses & Graphiques ---
  elif menu == "📈 Analyses & Graphiques":
    st.header("📈 Statistiques & Tendances")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
      st.subheader("Évolution sur les 7 derniers jours (ml)")
      if weekly:
        st.bar_chart(
            pd.DataFrame(weekly).set_index("date")["total"], color="#0096c7"
        )
      else:
        st.info("Pas encore assez de données sur la semaine.")
    with col_g2:
      st.subheader("Répartition par boisson (Aujourd'hui)")
      if items:
        by_drink = pd.DataFrame(items).groupby("drink_type")["amount_ml"].sum()
        st.bar_chart(by_drink, color="#48cae4")
      else:
        st.info("Ajoute des boissons aujourd'hui pour voir la répartition.")

  # --- Page 3 : Objectifs & Profil ---
  elif menu == "⚙️ Objectifs & Profil":
    st.header("⚙️ Paramètres & Calculateur d'objectif")
    with st.form("profile_form"):
      new_weight = st.number_input(
          "Ton poids actuel (kg)",
          min_value=30.0,
          max_value=200.0,
          value=float(data["weight_kg"]),
      )
      st.caption(f"💡 Objectif recommandé : **{int(new_weight * 35)} ml / jour**")
      new_goal = st.number_input(
          "Objectif quotidien personnalisé (ml)",
          min_value=500,
          max_value=6000,
          value=int(goal),
          step=100,
      )
      if st.form_submit_button("Enregistrer mes préférences", type="primary"):
        update_profile(username, new_weight, new_goal)
        st.success("Profil mis à jour !")
        st.rerun()