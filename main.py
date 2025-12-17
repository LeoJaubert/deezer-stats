import pandas as pd
import streamlit as st
from pages_display import afficher_page
from likedArtistsPage import likedArtists
from likedAlbumsPage import likedAlbums
from likedPlaylistsPage import likedPlaylists

#-------------------------Code starts here----------------------------
if __name__ == "__main__":
    #CSS styling
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            background: #A237FF;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    file_path = "stats-deezer-updated-more.xlsx"
    
    #Navigation menu
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Page à afficher",
        ("Détails du compte Deezer", "Profil de l'utilisateur", "Notifications", "Options de paiement", "Misc", "Artistes likés", "Albums likés", "Playlists likées")
    )
    
    #Call to corresponding page function
    if page == "Artistes likés":
        likedArtists(file_path)
    elif page == "Albums likés":
        likedAlbums(file_path)
    elif page == "Playlists likées":
        likedPlaylists(file_path)
    else:
        afficher_page(file_path, page)