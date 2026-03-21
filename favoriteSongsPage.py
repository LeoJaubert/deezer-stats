import pandas as pd
import streamlit as st
import numpy as np
import altair as alt

def calculateLikedTracksStats(df):
    #Calculate number of favorite tracks
    nb_morceaux = len(df)
    
    #Calculate number of different artists in all favorite tracks
    df_artists = df.copy()
    df_artists["Artists"] = df_artists["Artists"].str.split(",")
    df_artists = df_artists.explode("Artists")
    df_artists["Artists"] = (
        df_artists["Artists"]
        .str.strip()
        .str.replace(r'\s+', ' ', regex=True)
        .str.strip()
    )
    nb_artistes = df_artists["Artists"].nunique()
    
    #Calculate number of different albums in favorite tracks
    nb_albums = df["Album Title"].nunique()
    
    return nb_morceaux, nb_artistes, nb_albums

def calculateTopArtists(df):
    #Duplicate every song in featuring to count it for each artist of the song
    df_with_duplicated_featuring_songs = df.copy()
    df_with_duplicated_featuring_songs["Artists"] = df_with_duplicated_featuring_songs["Artists"].str.split(",")
    df_with_duplicated_featuring_songs = df_with_duplicated_featuring_songs.explode("Artists")
    df_with_duplicated_featuring_songs["Artists"] = df_with_duplicated_featuring_songs["Artists"].str.strip()

    #Create table with artists, songs listened and minutes listened (rounded to superior)
    top_artists = (
        df_with_duplicated_featuring_songs.groupby("Artists")
        .agg(
            Morceaux_favoris = ("Artists", "count"),
        )
        .sort_values(by = "Morceaux_favoris", ascending = False)
        .head(50)
        .reset_index()
    )

    #Rename columns
    top_artists = top_artists.rename(
        columns = {
            "Artists": "Artiste",
            "Morceaux_favoris": "Morceaux favoris"
        }
    )

    return top_artists

def calculateTopAlbums(df):
    top_albums = (
        df.groupby(["Album Title", "Artists"])
        .agg(
            Morceaux_favoris = ("Album Title", "count")
        )
        .sort_values(by = "Morceaux_favoris", ascending=False)
        .head(50)
        .reset_index()
    )

    top_albums = top_albums.rename(
        columns = {
            "Album Title": "Album",
            "Artists": "Artiste",
            "Morceaux_favoris": "Morceaux favoris",
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

def printData(type_data, top, x_col, y_col):
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
                value_vars = y_col,
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

def calculateDiversity(df):
    df = df.copy()

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
def favoriteSongs(sheet):
    df = sheet
    st.title("📊 Stats des morceaux likés", anchor = False)
    st.markdown("---")

    type_data = st.radio(
        label = "Affichage des top 50",
        options = ["Tableau", "Graphique"],
        horizontal = True,
    )

    #Calculate all infos that will be displayed in stat cards
    nb_morceaux, nb_artistes, nb_albums = calculateLikedTracksStats(df)
    ratio_div = round(nb_artistes / nb_morceaux * 100, 2)

    k1, k2 = st.columns(2, gap = "medium")
    with k1:
        stat_card(
            title = "Titres likés",
            value = f"{nb_morceaux:,}", 
            description = "morceaux favoris"
        )
    with k2:
        stat_card(
            title = "Artistes",
            value = f"{nb_artistes:,}",
            description = "artistes différents"
        )

    k1, k2 = st.columns(2, gap = "medium")
    with k1:
        stat_card(
            title = "Albums",
            value = f"{nb_albums:,}",
            description = "albums différents"
        )
    with k2:
        stat_card(
            title = "Diversité des artistes",
            value = ratio_div,
            description = "% d'artistes différents"
        )

    #Calculate and display top 50 of artists with most favorite tracks
    st.subheader("🧑‍🎤 Top 50 — Artistes", anchor = False)
    top_artists = calculateTopArtists(df)
    printData(
        type_data = type_data,
        top = top_artists,
        x_col = "Artiste",
        y_col = "Morceaux favoris"
    )

    #Calculate and display top 50 of albums with most favorite tracks
    st.subheader("💿 Top 50 — Albums", anchor = False)
    top_albums = calculateTopAlbums(df)
    printData(
        type_data = type_data,
        top = top_albums,
        x_col = "Album",
        y_col = "Morceaux favoris"
    )

    st.markdown("---")
    st.caption("_Les morceaux en featuring sont comptabilisés pour tous les artistes en featuring._")