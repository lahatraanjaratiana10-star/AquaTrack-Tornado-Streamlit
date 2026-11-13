from api_client import login_user, register_user
import streamlit as st


def render_auth_page():
  _, col_center, _ = st.columns([1, 2, 1])
  with col_center:
    st.markdown(
        """
            <div class="main-header" style="text-align:center;">
                <h1>🌊 AquaTrack Pro</h1>
                <p>Moins de gaspillage, plus de contrôle.</p>
            </div>
        """,
        unsafe_allow_html=True,
    )

    tab_login, tab_register = st.tabs(["Se connecter", "Créer un compte"])

    with tab_login:
      with st.form("login_form"):
        u = st.text_input("Identifiant")
        p = st.text_input("Mot de passe", type="password")
        if st.form_submit_button("Accéder au Dashboard", use_container_width=True):
          try:
            r = login_user(u, p)
            if r.status_code == 200:
              st.session_state.user = r.json()
              st.rerun()
            else:
              st.error("Identifiants incorrects.")
          except Exception:
            st.error("Serveur Tornado hors ligne (port 8888).")

    with tab_register:
      with st.form("register_form"):
        new_u = st.text_input("Choisir un identifiant")
        new_p = st.text_input("Choisir un mot de passe", type="password")
        weight = st.number_input(
            "Votre poids (kg)", min_value=30.0, max_value=200.0, value=65.0
        )
        if st.form_submit_button(
            "Démarrer mon suivi", use_container_width=True
        ):
          try:
            r = register_user(new_u, new_p, weight)
            if r.status_code == 201:
              st.success(
                  f"Compte créé ! Objectif calculé : {r.json()['daily_goal']} ml/jour."
              )
            else:
              st.error(r.json().get("error", "Erreur d'inscription"))
          except Exception:
            st.error("Serveur Tornado hors ligne.")