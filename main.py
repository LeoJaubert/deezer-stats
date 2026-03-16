import streamlit as st
import pandas as pd
from pages_display import showAllInfoPage
from likedArtistsPage import likedArtists
from likedAlbumsPage import likedAlbums
from likedPlaylistsPage import likedPlaylists
from listeningHistoryPage import listeningHistory

@st.cache_data(show_spinner = False)
def loadFile(file_path):
    file = pd.ExcelFile(file_path)
    return {sheet_name: file.parse(sheet_name) for sheet_name in file.sheet_names}

if __name__ == "__main__":
    col1, col2, col3 = st.sidebar.columns([1, 5, 1])
    with col2:
        st.image("pictures/deezer-logo-coeur.jpg")

    st.sidebar.subheader("The unofficial Deezer stats tracker", divider = "grey")
    page = st.sidebar.selectbox(
        label = "Page à afficher",
        options = ("Informations du compte", "Artistes likés", "Albums likés", "Playlists likées", "Stats approfondies")
    )

    file_path = st.sidebar.file_uploader(
        label = "Choisis ton fichier Deezer (.xlsx)",
        type = ["xlsx"],
        help = "Fichier récupéré via Deezer de la forme 'deezer-data_xxx.xlsx'"
    )

    if file_path is None:
        st.warning("Veuillez charger un fichier Deezer pour utiliser l'application")
        st.stop()

    with st.spinner("Chargement du fichier en cours"):
        all_sheets = loadFile(file_path)

    if page == "Artistes likés":
        likedArtists(all_sheets["4_favoriteArtist"])
    elif page == "Albums likés":
        likedAlbums(all_sheets["5_favoriteAlbum"])
    elif page == "Playlists likées":
        likedPlaylists(all_sheets["7_favoritePlaylist"])
    elif page == "Stats approfondies":
        listeningHistory(all_sheets["10_listeningHistory"])
    else:
        showAllInfoPage(file_path)
