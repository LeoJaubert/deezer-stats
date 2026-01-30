import streamlit as st
import pandas as pd
from pages_display import showPage
from likedArtistsPage import likedArtists
from likedAlbumsPage import likedAlbums
from likedPlaylistsPage import likedPlaylists
from listeningHistoryPage import listeningHistory

@st.cache_data
def loadFile(file_path):
    file = pd.ExcelFile(file_path)
    return {sheet_name: file.parse(sheet_name) for sheet_name in file.sheet_names}

if __name__ == "__main__":
    st.sidebar.image("placeholder_pics/deezer-logo-coeur.jpg")
    st.sidebar.markdown(
    """
    <div style = "position: sticky; top: 0; z-index: 10; padding: 5px 0;">
        <h3 style = "color: black; text-align: center; margin: 0;">
            The unofficial Deezer stats tracker
        </h3>
    </div>
    """,
    unsafe_allow_html = True)

    #Navigation menu
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Page à afficher",
        ("Détails du compte Deezer", "Profil de l'utilisateur", "Notifications", "Options de paiement", "Misc", "Artistes likés", "Albums likés", "Playlists likées", "Stats approfondies")
    )

    file_path = "deezer-data_5567445704.xlsx"
    all_sheets = loadFile(file_path)

    #Call to corresponding page function
    if page == "Artistes likés":
        likedArtists(all_sheets["4_favoriteArtist"])
    elif page == "Albums likés":
        likedAlbums(all_sheets["5_favoriteAlbum"])
    elif page == "Playlists likées":
        likedPlaylists(all_sheets["7_favoritePlaylist"])
    elif page == "Stats approfondies":
        listeningHistory(all_sheets["10_listeningHistory"])
    else:
        showPage(file_path, page)
