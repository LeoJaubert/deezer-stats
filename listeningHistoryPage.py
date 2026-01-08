import pandas as pd
import streamlit as st
import numpy as np

def filterNonListenedSongs(df):
    #Clear all songs not listened more than 29 seconds to be counted
    df = df[df["Listening Time"] > 29]
    
    #Clear every "hole" in the index
    df = df.reset_index(drop = True)
    
    #Start index at 1 instead of 0
    df.index = df.index + 1
    
    return df

def calculateTopArtists(df):
    #Duplicate every song in featuring to count it for each artist of the song
    df_with_duplicated_featuring_songs = df.copy()
    df_with_duplicated_featuring_songs["Artist"] =    df_with_duplicated_featuring_songs["Artist"].str.split(",")
    df_with_duplicated_featuring_songs =  df_with_duplicated_featuring_songs.explode("Artist")
    df_with_duplicated_featuring_songs["Artist"] =    df_with_duplicated_featuring_songs["Artist"].str.strip()

    #Create table with artists, songs listened and minutes listened (rounded to superior)
    top_artists = (
        df_with_duplicated_featuring_songs.groupby("Artist")
        .agg(
            Morceaux_ecoutes = ("Artist", "count"),
            Minutes_ecoutees = ("Listening Time", lambda x: int(np.ceil(x.sum() / 60)))
        )
        .sort_values(by = "Morceaux_ecoutes", ascending = False)
        .head(100)
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

def calculateTopSongs(df):
    top_tracks = (
        df.groupby(["Song Title", "Artist"])
        .agg(
            Fois_ecoute=("Song Title", "count"),
            Minutes_ecoutees=("Listening Time", lambda x: int(np.ceil(x.sum() / 60)))
        )
        .sort_values(by="Fois_ecoute", ascending=False)
        .head(100)
        .reset_index()
    )

    # Renommage des colonnes
    top_tracks = top_tracks.rename(
        columns={
            "Track": "Son",
            "Artist": "Artiste",
            "Fois_ecoute": "Nombre d'écoutes",
            "Minutes_ecoutees": "Minutes écoutées"
        }
    )

    return top_tracks

#--------------Code starts here--------------#
def listeningHistory(file_path):
    df = pd.read_excel(file_path, sheet_name="10_listeningHistory")

    df = filterNonListenedSongs(df)

    st.title("📊 Stats approfondies")
    st.markdown("---")

    #Calculate and print top 100 of most streamed artists
    st.subheader("Top 100 des artistes les plus écoutés")
    top_artists = calculateTopArtists(df)
    st.dataframe(top_artists, hide_index = True)

    #Calculate and print top 100 of most streamed songs
    st.subheader("Top 100 des morceaux les plus écoutés")
    top_songs = calculateTopSongs(df)
    styled_df = (
        top_songs.style
        .bar(subset=["Nombre d'écoutes"], color="#1DB954")
        .background_gradient(subset=["Minutes écoutées"], cmap="Greens")
    )
    st.dataframe(top_songs, hide_index = True)

    st.markdown("---")
    st.caption("_NB: Les morceaux écoutés pendant moins de 30 secondes ne sont pas comptabilisés, comme dans les statistiques officielles._")
    st.caption("_NB: Les morceaux en featuring, s'ils sont affichés comme tels dans les artistes, sont comptabilisés pour tous les artistes en featuring._")




