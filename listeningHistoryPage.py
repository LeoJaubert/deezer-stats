import pandas as pd
import streamlit as st
import numpy as np
import altair as alt

def formatProperlyDataframe(df):
    #Clear all songs listened less than 30 seconds to be counted
    df = df[df["Listening Time"] > 29]

    #Clear every "hole" in the index
    df = df.reset_index(drop = True)

    #Start index at 1 instead of 0
    df.index = df.index + 1

    #Convert "Date" column from string to datetime and sets the correct timezone (UTC +1)
    df["Date"] = pd.to_datetime(df["Date"], errors = "coerce", utc = True)
    df["Date"] = df["Date"].dt.tz_convert("Europe/Paris")

    return df

def showListeningTimeByYear(df):
    df = df.copy()

    df["Année"] = df["Date"].dt.year

    yearly_stats = df.groupby("Année").agg(
        Morceaux_ecoutes=("Date", "count"),
        Minutes_ecoutees=("Listening Time", lambda x: int(np.ceil(x.sum() / 60)))
    ).reset_index()

    yearly_stats = yearly_stats.rename(
        columns={
            "Morceaux_ecoutes": "Morceaux écoutés",
            "Minutes_ecoutees": "Minutes écoutées"
        }
    )

    chart = (
        alt.Chart(yearly_stats)
        .transform_fold(
            ["Morceaux écoutés", "Minutes écoutées"],
            as_=["Type", "Valeur"]
        )
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "Année:O",
                title="Année"
            ),
            y=alt.Y(
                "Valeur:Q",
                title="Valeur",
                axis=alt.Axis(
                    grid=True,
                    gridColor="grey",
                    gridOpacity=0.25
                )
            ),
            color=alt.Color(
                "Type:N",
                title="Légende"
            ),
            tooltip=[
                alt.Tooltip("Année:O", title="Année"),
                alt.Tooltip("Type:N", title="Type"),
                alt.Tooltip("Valeur:Q", title="Valeur")
            ]
        )
    )

    st.altair_chart(chart)

def findEveryYearInDateColumn(df):
    df["Date"] = pd.to_datetime(df["Date"])
    years = sorted(df["Date"].dt.year.unique().tolist())
    years.insert(0, 'All time')

    return years

def calculateTopArtists(df, year_chosen):
    #Duplicate every song in featuring to count it for each artist of the song
    df_with_duplicated_featuring_songs = df.copy()
    df_with_duplicated_featuring_songs["Artist"] = df_with_duplicated_featuring_songs["Artist"].str.split(",")
    df_with_duplicated_featuring_songs = df_with_duplicated_featuring_songs.explode("Artist")
    df_with_duplicated_featuring_songs["Artist"] = df_with_duplicated_featuring_songs["Artist"].str.strip()

    #Filter according to the year chosen
    if year_chosen != "All time":
        df_with_duplicated_featuring_songs = df_with_duplicated_featuring_songs[df_with_duplicated_featuring_songs["Date"].dt.year == year_chosen]

    #Create table with artists, songs listened and minutes listened (rounded to superior)
    top_artists = (
        df_with_duplicated_featuring_songs.groupby("Artist")
        .agg(
            Morceaux_ecoutes = ("Artist", "count"),
            Minutes_ecoutees = ("Listening Time", lambda x: int(np.ceil(x.sum() / 60)))
        )
        .sort_values(by = "Morceaux_ecoutes", ascending = False)
        .head(50)
        .reset_index()
    )

    #Rename columns
    top_artists = top_artists.rename(
        columns = {
            "Artist": "Artiste",
            "Morceaux_ecoutes": "Morceaux écoutés",
            "Minutes_ecoutees": "Minutes écoutées"
        }
    )

    return top_artists

def calculateTopTracks(df, year_chosen):
    #Filter according to the year chosen
    if year_chosen != "All time":
        df = df[df["Date"].dt.year == year_chosen]

    top_tracks = (
        df.groupby(["Song Title", "Artist"])
        .agg(
            Fois_ecoute=("Song Title", "count"),
            Minutes_ecoutees=("Listening Time", lambda x: int(np.ceil(x.sum() / 60)))
        )
        .sort_values(by="Fois_ecoute", ascending=False)
        .head(50)
        .reset_index()
    )

    top_tracks = top_tracks.rename(
        columns={
            "Song Title": "Morceau",
            "Artist": "Artiste",
            "Fois_ecoute": "Nombre d'écoutes",
            "Minutes_ecoutees": "Minutes écoutées"
        }
    )

    return top_tracks

def calculateTopAlbums(df, year_chosen):
    if year_chosen != "All time":
        df = df[df["Date"].dt.year == year_chosen]

    top_albums = (
        df.groupby(["Album Title", "Artist"])
        .agg(
            Fois_ecoute=("Album Title", "count"),
            Minutes_ecoutees=("Listening Time", lambda x: int(np.ceil(x.sum() / 60)))
        )
        .sort_values(by="Fois_ecoute", ascending=False)
        .head(50)
        .reset_index()
    )

    top_albums = top_albums.rename(
        columns={
            "Album Title": "Album",
            "Artist": "Artiste",
            "Fois_ecoute": "Nombre d'écoutes",
            "Minutes_ecoutees": "Minutes écoutées"
        }
    )

    return top_albums

def colorTopRows(row):
    if row.name == 0:
        return ["background-color: #FFD700"] * len(row)
    elif row.name == 1:
        return ["background-color: #C0C0C0"] * len(row)
    elif row.name == 2:
        return ["background-color: #CD7F32"] * len(row)
    elif row.name >= 3 and row.name <= 9:
        return ["background-color: #D9ADFF"] * len(row)
    else:
        return [""] * len(row)

def printData(type_data, top, x_col, y_col_1, y_col_2):
    if type_data == 'Tableau':
        styled_top = (
            top
            .style
            .apply(colorTopRows, axis = 1)
        )
        st.dataframe(styled_top, hide_index = True)
    else:
        chart_df = (
            top
            .head(50)
            .melt(
                id_vars = x_col,
                value_vars = [y_col_1, y_col_2],
                var_name = "Type",
                value_name = "Valeur"
            )
        )
        st.bar_chart(
            chart_df,
            x = x_col,
            y = "Valeur",
            color = "Type",
            stack = False
        )

def showListeningTimeByDayOfTheWeek(df, year_chosen):
    df = df.copy()

    if year_chosen != "All time":
        df = df[df["Date"].dt.year == year_chosen]

    df["Jour"] = df["Date"].dt.dayofweek
    jours_labels = {0: "Lundi", 1: "Mardi", 2: "Mercredi", 3: "Jeudi", 4: "Vendredi", 5: "Samedi", 6: "Dimanche"}

    df_day = (
        df.groupby("Jour")
        .agg(Minutes_ecoutees=("Listening Time", lambda x: int(np.ceil(x.sum() / 60))))
        .reset_index()
    )

    df_day["Jour_label"] = df_day["Jour"].map(jours_labels)

    ordre_jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    base = alt.Chart(df_day).encode(
        theta=alt.Theta("Minutes_ecoutees:Q", stack=True),
        color=alt.Color("Jour_label:N", sort=ordre_jours, title="Jour de la semaine"),
        order=alt.Order("Jour:Q"),
        tooltip=[alt.Tooltip("Jour_label:N", title="Jour"), alt.Tooltip("Minutes_ecoutees:Q", title="Minutes")]
    )

    chart = base.mark_arc(outerRadius = 150)

    st.altair_chart(chart)

def showListeningTimeByMonth(df, year_chosen):
    if year_chosen != "All time":
        df = df[df["Date"].dt.year == year_chosen]

    df = df.copy()
    df["Mois_num"] = df["Date"].dt.month
    df["Mois"] = df["Date"].dt.month_name(locale="fr_FR")

    monthly_stats = (
        df.groupby(["Mois_num", "Mois"])
        .agg(
            **{
                "Morceaux écoutés": ("Date", "count"),
                "Minutes écoutées": ("Listening Time", lambda x: int(np.ceil(x.sum() / 60)))
            }
        )
        .reset_index()
    )

    chart = (
        alt.Chart(monthly_stats)
        .transform_fold(
            ["Morceaux écoutés", "Minutes écoutées"],
            as_=["Type", "Valeur"]
        )
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "Mois:N",
                sort=alt.SortField(
                    field="Mois_num",
                    order="ascending"
                ),
                title="Mois"
            ),
            y=alt.Y(
                "Valeur:Q",
                title="Valeur",
                axis=alt.Axis(
                    grid=True,
                    gridColor="grey",
                    gridOpacity=0.25
                )
            ),
            color=alt.Color("Type:N", title="Légende"),
            tooltip=[
                alt.Tooltip("Mois:N", title="Mois"),
                alt.Tooltip("Type:N", title="Type"),
                alt.Tooltip("Valeur:Q", title="Valeur")
            ]
        )
    )

    st.altair_chart(chart)

def showListeningTimeByHour(df, year_chosen):
    df = df.copy()
    df = df.dropna(subset=["Date"])

    if year_chosen != "All time":
        df = df[df["Date"].dt.year == year_chosen]

    df["Heure"] = df["Date"].dt.hour

    hourly_stats = (
        df.groupby("Heure")
        .agg(
            Morceaux_ecoutes=("Date", "count"),
            Minutes_ecoutees=("Listening Time", lambda x: int(np.ceil(x.sum() / 60)))
        )
        .reindex(range(24), fill_value=0)
        .reset_index()
    )

    chart_df = hourly_stats.melt(
        id_vars=["Heure"],
        value_vars=["Morceaux_ecoutes", "Minutes_ecoutees"],
        var_name="Type",
        value_name="Valeur"
    )

    chart_df["Type"] = chart_df["Type"].replace({
        "Morceaux_ecoutes": "Morceaux écoutés",
        "Minutes_ecoutees": "Minutes écoutées"
    })

    chart_df["Heure_label"] = chart_df["Heure"].apply(lambda x: f"{x}h - {x+1}h")

    chart = (
        alt.Chart(chart_df)
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "Heure:O",
                title="Heure de la journée",
                axis=alt.Axis(
                    labelExpr='datum.value + "h - " + (datum.value+1) + "h"'
                )
            ),
            y=alt.Y(
                "Valeur:Q",
                title="Valeur",
                axis=alt.Axis(
                    grid=True,
                    gridColor="grey",
                    gridOpacity=0.25
                )
            ),
            color=alt.Color("Type:N", title="Légende"),
            tooltip=[
                alt.Tooltip("Heure_label:O", title="Heure de la journée"),
                alt.Tooltip("Type:N", title="Type"),
                alt.Tooltip("Valeur:Q", title="Valeur"),
            ]
        )
    )

    st.altair_chart(chart)

def calculateListeningTime(df, year_chosen):
    #Filter according to the year chosen
    if year_chosen != "All time":
        df = df[df["Date"].dt.year == year_chosen]

    totalsec = df['Listening Time'].sum()
    totalhours = round(totalsec / 3600)
    totaldays = totalhours // 24
    modulototaldays = totalhours % 24

    return totalhours, totaldays, modulototaldays

def showListeningTimeByNight(df, year_chosen):
    df = df.copy()

    if year_chosen != "All time":
        df = df[df["Date"].dt.year == year_chosen]

    df["Heure"] = df["Date"].dt.hour

    #Define night time as 22h - 6h
    night_mask = (df["Heure"] >= 22) | (df["Heure"] < 6)

    total_listens = len(df)
    night_listens = night_mask.sum()

    night_percentage = round((night_listens / total_listens) * 100, 1)

    return night_percentage

def findMostListenedDay(df, year_chosen):
    df = df.copy()

    if year_chosen != "All time":
        df = df[df["Date"].dt.year == year_chosen]

    df["Jour"] = df["Date"].dt.date

    daily_stats = (
        df.groupby("Jour")
        .agg(
            tracksvalue=("Date", "count"),
            minutesvalue=("Listening Time", lambda x: int(np.ceil(x.sum() / 60)))
        )
        .sort_values("minutesvalue", ascending=False)
    )

    top_day = daily_stats.iloc[0]
    day_date = daily_stats.index[0]

    #Correctly format date
    mostlistenedday = day_date.strftime("%d/%m/%Y")

    return mostlistenedday, top_day["tracksvalue"], top_day["minutesvalue"]

def findFirstAndLastTrack(df, year_chosen):
    df = df.copy()

    if year_chosen != "All time":
        df = df[df["Date"].dt.year == year_chosen]

    first_row = df.loc[df["Date"].idxmin()]
    first_track_title = first_row["Song Title"]
    first_track_artist = first_row["Artist"]
    first_track_date = first_row["Date"].strftime("%d/%m/%Y à %H:%M")

    last_row = df.loc[df["Date"].idxmax()]
    last_track_title = last_row["Song Title"]
    last_track_artist = last_row["Artist"]
    last_track_date = last_row["Date"].strftime("%d/%m/%Y à %H:%M")

    return first_track_title, first_track_artist, first_track_date, last_track_title, last_track_artist, last_track_date

def calculateDiversity(df, year_chosen):
    df = df.copy()

    if year_chosen != "All time":
        df = df[df["Date"].dt.year == year_chosen]

    nb_tracks_listened = len(df)

    nb_unique_tracks_listened = len(df[["Song Title", "Artist"]].drop_duplicates())

    ratio_repetition = round(nb_tracks_listened / nb_unique_tracks_listened, 2)
    ratio_diversite = round(nb_unique_tracks_listened / nb_tracks_listened * 100, 2)

    return nb_tracks_listened, nb_unique_tracks_listened, ratio_repetition, ratio_diversite

def stat_card(title, value, description):
    st.markdown(
        f"""<div style="background: #dddde0;border: 1px solid rgba(162, 56, 255, 0.18);border-radius: 14px;padding: 18px 20px;margin-bottom: 12px;box-shadow: 0 4px 18px rgba(0, 0, 0, 0.3);">
              <div style="color: #6a6a82;font-size: 0.75rem;text-transform: uppercase;letter-spacing: 0.06em;margin-bottom: 4px;">{title}</div>
              <div style="color: #000000;font-size: 2rem;font-weight: 700;margin-bottom: 4px;">{value}</div>
              <div style="color: #4a4a5a;font-size: 0.8rem;font-weight: 500;">{description}</div>
            </div>""",
        unsafe_allow_html = True
    )

#--------------Code starts here--------------#
def listeningHistory(sheet):
    df = sheet
    df = formatProperlyDataframe(df)

    st.title("📊 Stats approfondies", anchor = False)
    st.markdown("---")

    #Calculate and display evolution of listening time by year
    st.subheader("📶 Évolution annuelle de l'écoute", anchor = False)
    showListeningTimeByYear(df)

    years = findEveryYearInDateColumn(df)
    col_sel, col_radio = st.columns([1, 3], gap = "xxlarge")
    with col_sel:
        year_chosen = st.selectbox("Année", years)
    with col_radio:
        type_data = st.radio(
            label = "Affichage des top 50",
            options = ["Tableau", "Graphique"],
            horizontal = True,
        )

    #Calculate all infos that will be displayed in stat cards
    totalhours, totaldays, modulototaldays = calculateListeningTime(df, year_chosen)
    nb_tracks, nb_unique, ratio_rep, ratio_div = calculateDiversity(df, year_chosen)
    most_day, tracks_val, minutes_val = findMostListenedDay(df, year_chosen)
    ft_title, ft_artist, ft_date, lt_title, lt_artist, lt_date = findFirstAndLastTrack(df, year_chosen)

    #Display listening time and number of listened tracks
    k1, k2 = st.columns(2, gap = "medium")
    with k1:
        stat_card(
            title = "Temps d'écoute",
            value = totalhours,
            description = f"heures, soit {totaldays} jours et {modulototaldays} heures"
        )
    with k2:
        stat_card(
            title = "Morceaux",
            value = f"{nb_tracks:,}".replace(",", " "),
            description = "titres écoutés"
        )

    #Display day with most listening time and diversity of listened tracks
    k1, k2 = st.columns(2, gap = "medium")
    with k1:
        stat_card(
            title = "Jour le plus écouté",
            value = most_day,
            description = f"{tracks_val} morceaux - {minutes_val} minutes"
        )
    with k2:
        stat_card(
            title = "Diversité",
            value = ratio_div,
            description = "% de morceaux écoutés une seule fois"
        )

    #Display stats about diversity
    k1, k2 = st.columns(2, gap = "medium")
    with k1:
        stat_card(
            title = "Ratio répétition",
            value = ratio_rep,
            description = "écoutes d'un même morceau en moyenne"
        )
    with k2:
        stat_card(
            title = "Morceaux uniques",
            value = nb_unique,
            description = "titres écoutés une seule fois"
        )

    #Display first and last track listened
    k1, k2 = st.columns(2, gap = "medium")
    with k1:
        stat_card(
            title = "Premier morceau écouté",
            value = ft_title,
            description = f"de {ft_artist} - {ft_date}"
        )
    with k2:
        stat_card(
            title = "Dernier morceau écouté",
            value = lt_title,
            description = f" de {lt_artist} - {lt_date}"
        )

    #Calculate and display top 50 of most streamed artists
    st.subheader("🧑‍🎤 Top 50 — Artistes", anchor = False)
    top_artists = calculateTopArtists(df, year_chosen)
    printData(
        type_data = type_data,
        top = top_artists,
        x_col = "Artiste",
        y_col_1 = "Morceaux écoutés",
        y_col_2 = "Minutes écoutées"
    )

    #Calculate and display top 50 of most streamed tracks
    st.subheader("🎵 Top 50 — Morceaux", anchor = False)
    top_tracks = calculateTopTracks(df, year_chosen)
    printData(
        type_data = type_data,
        top = top_tracks,
        x_col = "Morceau",
        y_col_1 = "Nombre d'écoutes",
        y_col_2 = "Minutes écoutées"
    )

    #Calculate and display top 50 of most streamed albums
    st.subheader("💿 Top 50 — Albums", anchor = False)
    top_albums = calculateTopAlbums(df, year_chosen)
    printData(
        type_data = type_data,
        top = top_albums,
        x_col = "Album",
        y_col_1 = "Nombre d'écoutes",
        y_col_2 = "Minutes écoutées"
    )

    #Calculate and display repartition of listening time by day of the week
    st.subheader("📅 Répartition par jour de la semaine", anchor = False)
    showListeningTimeByDayOfTheWeek(df, year_chosen)

    #Calculate and display evolution of listening time by month
    st.subheader("📈 Évolution mensuelle", anchor = False)
    showListeningTimeByMonth(df, year_chosen)

    #Calculate and display evolution of listening time by hour
    st.subheader("🕑 Tendance par heure", anchor = False)
    showListeningTimeByHour(df, year_chosen)

    #Calculate and display listening time by night
    st.subheader("🌙 Jour / Nuit", anchor = False)
    night_pct = showListeningTimeByNight(df, year_chosen)
    day_pct = 100 - night_pct
    st.markdown(
        f"""<div style="display:flex; gap:0; border-radius:10px; overflow:hidden; height:28px; margin:8px 0 4px;">
              <div style="width:{day_pct}%; background:linear-gradient(90deg,#A238FF,#c060ff);
                          display:flex; align-items:center; justify-content:center;
                          color:#fff; font-size:0.8rem; font-weight:600;">
                  ☀️ {day_pct}%
              </div>
              <div style="width:{night_pct}%; background:linear-gradient(90deg,#1e1e34,#2a2a4a);
                          display:flex; align-items:center; justify-content:center;
                          color:#8080a0; font-size:0.8rem; font-weight:600;">
                  🌙 {night_pct}%
              </div>
            </div>
            <p style="color:#5a5a72; font-size:0.75rem; margin:0;">Jour 6h–22h · Nuit 22h–6h</p>""",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.caption("_Les morceaux écoutés moins de 30 secondes ne sont pas comptabilisés, comme dans les statistiques officielles._")
    st.caption("_Les morceaux en featuring sont comptabilisés pour tous les artistes en featuring._")