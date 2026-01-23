import pandas as pd
import streamlit as st
import numpy as np
import altair as alt

def filterNonListenedSongs(df):
    #Clear all songs not listened more than 29 seconds to be counted
    df = df[df["Listening Time"] > 29]

    #Clear every "hole" in the index
    df = df.reset_index(drop = True)

    #Start index at 1 instead of 0
    df.index = df.index + 1

    return df

def calculateTopArtists(df, year_chosen):
    #Duplicate every song in featuring to count it for each artist of the song
    df_with_duplicated_featuring_songs = df.copy()
    df_with_duplicated_featuring_songs["Artist"] = df_with_duplicated_featuring_songs["Artist"].str.split(",")
    df_with_duplicated_featuring_songs = df_with_duplicated_featuring_songs.explode("Artist")
    df_with_duplicated_featuring_songs["Artist"] = df_with_duplicated_featuring_songs["Artist"].str.strip()

    #Filter according to the year chosen
    if year_chosen == "All time":
        pass
    else:
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
    if year_chosen == "All time":
        pass
    else:
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

def calculateListeningTime(df, year_chosen):
    #Filter according to the year chosen
    if year_chosen == "All time":
        pass
    else:
        df = df[df["Date"].dt.year == year_chosen]

    totalsec = df['Listening Time'].sum()
    totalhour = round(totalsec / 3600)
    totaldays = totalhour // 24
    modulototaldays = totalhour % 24
    return totalhour, totaldays, modulototaldays

def findEveryYearInDateColumn(df):
    df["Date"] = pd.to_datetime(df["Date"])
    years = sorted(df["Date"].dt.year.unique().tolist())
    years.insert(0, 'All time')
    return years

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
            y=alt.Y("Valeur:Q", title="Valeur"),
            color=alt.Color("Type:N", title="Type"),
            tooltip=[
                alt.Tooltip("Mois:N", title="Mois"),
                alt.Tooltip("Type:N", title="Type"),
                alt.Tooltip("Valeur:Q", title="Valeur")
            ]
        )
    )

    st.altair_chart(chart)

def showListeningTimeByYear(df):
    df = df.copy()

    # Conversion en datetime
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Créer la colonne Année
    df["Année"] = df["Date"].dt.year

    # Ensuite tu peux grouper
    yearly_stats = df.groupby("Année").agg(
        Morceaux_ecoutes=("Date", "count"),
        Minutes_ecoutees=("Listening Time", lambda x: int(np.ceil(x.sum() / 60)))
    ).reset_index()

    # Renommage propre
    yearly_stats = yearly_stats.rename(
        columns={
            "Morceaux_ecoutes": "Morceaux écoutés",
            "Minutes_ecoutees": "Minutes écoutées"
        }
    )

    # Création du graphique
    chart = (
        alt.Chart(yearly_stats)
        .transform_fold(
            ["Morceaux écoutés", "Minutes écoutées"],
            as_=["Type", "Valeur"]
        )
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "Année:O",              # Ordinal = ordre conservé
                title="Année"
            ),
            y=alt.Y(
                "Valeur:Q",
                title="Valeur"
            ),
            color=alt.Color(
                "Type:N",
                title="Type"
            ),
            tooltip=[
                alt.Tooltip("Annee:O", title="Année"),
                alt.Tooltip("Type:N", title="Type"),
                alt.Tooltip("Valeur:Q", title="Valeur")
            ]
        )
    )

    st.altair_chart(chart)

#--------------Code starts here--------------#
def listeningHistory(file_path):
    df = pd.read_excel(file_path, sheet_name="10_listeningHistory")

    df = filterNonListenedSongs(df)

    st.title("📊 Stats approfondies")
    st.markdown("---")

    st.subheader("📈 Évolution annuelle de l’écoute")

    showListeningTimeByYear(df)

    years = findEveryYearInDateColumn(df)
    year_chosen = st.selectbox("Choix de l'année", years)

    st.subheader("📈 Évolution mensuelle de l’écoute")

    showListeningTimeByMonth(df, year_chosen)

    data_types = ['Tableau', 'Graphique']
    type_data = st.radio('Type de données', data_types)

    #Calculate and print top 50 of most streamed artists
    st.subheader("🧑‍🎤 Top 50 des artistes les plus écoutés")
    top_artists = calculateTopArtists(df, year_chosen)

    printData(
        type_data = type_data,
        top = top_artists,
        x_col = "Artiste",
        y_col_1 = "Morceaux écoutés",
        y_col_2 = "Minutes écoutées"
    )

    #Calculate and print top 50 of most streamed songs
    st.subheader("🎵 Top 50 des morceaux les plus écoutés")
    top_tracks = calculateTopTracks(df, year_chosen)

    printData(
        type_data = type_data,
        top = top_tracks,
        x_col = "Morceau",
        y_col_1 = "Nombre d'écoutes",
        y_col_2 = "Minutes écoutées"
    )

    #Calculate and print listening time
    st.subheader("Nombre d'heures écoutées")
    totalhour, totaldays, modulototaldays = calculateListeningTime(df, year_chosen)
    st.text(f"Temps d'écoute: {totalhour} heures, soit {totaldays} jours et {modulototaldays} heures.")

    st.markdown("---")
    st.caption("_NB: Les morceaux écoutés pendant moins de 30 secondes ne sont pas comptabilisés, comme dans les statistiques officielles._")
    st.caption("_NB: Les morceaux en featuring, s'ils sont affichés comme tels dans les artistes, sont comptabilisés pour tous les artistes en featuring._")
