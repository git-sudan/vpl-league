import streamlit as st
import json
import pandas as pd
import os

st.set_page_config(
        page_title="VPL Fantasy League",
        page_icon="🏏",
        layout="wide"
)


# Load player and match data
with open("data/players.json") as f:
    players_data = json.load(f)

with open("data/matches.json") as f:
    matches_data = json.load(f)

custom_css = """
    <style>
        [data-testid="stSidebar"] ul {
            padding-left: 0px;
        }
        [data-testid="stSidebar"] ul > li > div[role="button"] {
            border-radius: 0px !important;
            padding: 10px !important;
            margin-bottom: 5px !important;
            text-align: center !important;
            background-color: #f0f2f6 !important;
            border: 1px solid #e0e0e0 !important;
        }
        [data-testid="stSidebar"] ul > li > div[role="button"]:hover {
            background-color: #e0e2e6 !important;
        }
    </style>
    """
st.markdown(custom_css, unsafe_allow_html=True)
# Sidebar navigation
page = st.sidebar.radio("Go to", ["Select Team", "Leaderboard", "View My Teams"])

# --- Select Team Page ---
# --- Select Team Page ---
if page == "Select Team":
    st.title("🏏 VPL Fantasy League")

    match = st.selectbox(
        "Select Match",
        matches_data,
        format_func=lambda x: f"{x['match_id']}: {x['team_a']} vs {x['team_b']}"
    )

    team_a = match["team_a"]
    team_b = match["team_b"]
    team_a_players = players_data[team_a]
    team_b_players = players_data[team_b]

    # Add team name in brackets
    all_players = [(player, team_a) for player in team_a_players] + [(player, team_b) for player in team_b_players]

    name = st.text_input("Enter your name")
    mobile = st.text_input("Enter your mobile number")
    selected_players = []

    st.write(f"**Select 7 Players**")
    for player, team in all_players:
        label = f"{player} ({team})"
        if len(selected_players) < 7:
            if st.checkbox(label, key=label):
                selected_players.append(player)
        else:
            st.checkbox(label, key=label, disabled=True)

    st.info(f"Players selected: {len(selected_players)} / 7. Players remaining: {7 - len(selected_players)}")

    if st.button("Submit Team"):
        if not name or not mobile:
            st.warning("Please enter your name and mobile number.")
        elif len(selected_players) != 7:
            st.warning("Please select exactly 7 players.")
        else:
            df = pd.DataFrame({
                "match_id": match["match_id"],
                "name": name,
                "mobile": mobile,
                "player": selected_players
            })

            if not os.path.exists("teams.csv"):
                df.to_csv("teams.csv", index=False)
            else:
                df.to_csv("teams.csv", mode="a", header=False, index=False)

            st.success("✅ Team submitted successfully!")

# --- Leaderboard Page ---
elif page == "Leaderboard":
    st.title("📊 Match Leaderboard")

    if not os.path.exists("results.csv"):
        st.info("No results uploaded yet.")
    else:
        df = pd.read_csv("results.csv")
        match_ids = df["match_id"].unique()
        selected_match_id = st.selectbox("Select Match", match_ids)

        match_df = df[df["match_id"] == selected_match_id]
        leaderboard = match_df.groupby("mobile")["points"].sum().reset_index().sort_values(by="points", ascending=False)
        st.dataframe(leaderboard)

        if not leaderboard.empty:
            st.success(f"🏆 Winner: {leaderboard.iloc[0]['mobile']} with {leaderboard.iloc[0]['points']} points")

# --- View My Teams Page ---
# --- View All Submitted Teams (One Row per Team) ---
# --- View All Submitted Teams (One Row per Team, Clean Mobile Display) ---
# --- View All Submitted Teams (Wider Table View) ---
# --- View All Submitted Teams (Wider View + Match Teams Displayed) ---
elif page == "View My Teams":
    st.title("📋 All Submitted Teams")

    if not os.path.exists("teams.csv"):
        st.info("No teams submitted yet.")
    else:
        df = pd.read_csv("teams.csv")

        if "mobile" not in df.columns:
            st.error("The uploaded data does not contain a 'mobile' column.")
        else:
            # Clean and transform
            df["mobile"] = df["mobile"].astype(str).str.replace(",", "").str.strip()

            # Load matches
            with open("data/matches.json") as f:
                matches_data = json.load(f)

            match_map = {
                str(match["match_id"]): f"{match['team_a']} vs {match['team_b']}"
                for match in matches_data
            }

            grouped = (
                df.groupby(["match_id", "name", "mobile"])["player"]
                .apply(lambda x: ", ".join(x))
                .reset_index()
                .rename(columns={"player": "players"})
            )

            grouped["match"] = grouped["match_id"].astype(str).map(match_map)
            grouped = grouped[["match", "name", "mobile", "players"]]
            grouped.index = grouped.index + 1

            st.dataframe(grouped, use_container_width=True)

