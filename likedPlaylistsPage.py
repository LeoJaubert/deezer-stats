import pandas as pd
import streamlit as st
import requests
import base64

@st.cache_data(show_spinner=False)
def get_playlist_info_from_id(playlist_link):
    # Extrait l'ID de la playlist depuis le lien
    try:
        playlist_id = playlist_link.rstrip('/').split('/')[-1]
        url = f"https://api.deezer.com/playlist/{playlist_id}"
        response = requests.get(url)
        data = response.json()
        return {
            "img_url": data.get("picture_medium", "N/A"),
            "nb_tracks": data.get("nb_tracks", "N/A"),
            "fans": data.get("fans", "N/A"),
            "duration": data.get("duration", "N/A"),
            "description": data.get("description", "N/A")
        }
    except Exception:
        pass
    return None

#Function needed to use placeholder in HTML
def get_base64_image(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def likedPlaylists(file_path):
    df = pd.read_excel(file_path, sheet_name="7_favoritePlaylist")
    st.title("🎶 Playlists likées")
    st.markdown("---")

    playlistsDict = {}
    for i in range(len(df)):
        playlist = df.iloc[i]["Playlist Title"]
        link = df.iloc[i]["Link"]
        playlistsDict[playlist] = link

    # Barre de recherche
    search = st.text_input("🔎 Rechercher une playlist")
    if search:
        playlistsDict = {k: v for k, v in playlistsDict.items() if search.lower() in k.lower()}
    #Sort in alphabetical order
    playlistsDict = dict(sorted(playlistsDict.items(), key=lambda item: item[0].lower()))

    img_base64 = get_base64_image("placeholder_pics/placeholder-picture.jpg")
    placeholder = f"data:image/jpeg;base64,{img_base64}"

    #Print 4 by 4 playlists with their picture and link to their Deezer page
    playlists = list(playlistsDict.items())
    row_items = 4
    for i in range(0, len(playlists), row_items):
        cols = st.columns(row_items)
        for j, (playlist, link) in enumerate(playlists[i:i+row_items]):
            with cols[j]:
                playlist_info = get_playlist_info_from_id(link)
                #Correct format of the link
                if not link.startswith("http"):
                    link = "https://" + link.lstrip("/")
                #If playlist not found, use a placeholder image and do not display the link
                if playlist_info == {'img_url': 'N/A', 'nb_tracks': 'N/A', 'fans': 'N/A', 'duration': 'N/A', 'description': 'N/A'}:
                    st.markdown(
                        f"""<div style="display: flex; flex-direction: column; align-items: center; margin-top:6px;">
                                <img src="{placeholder}" alt="{playlist}" width="70" style="border-radius:8px; box-shadow:0 2px 8px #0001; display:block;"/>
                                <span style="font-size: 0.95em; font-weight: 600; text-align: center; display: block; color: #222; margin-top: 6px;">{playlist}</span>
                            </div>""",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"""<div style="display: flex; flex-direction: column; align-items: center; margin-top:6px;">
                                <a href="{link}" target="_blank" style="text-decoration: none;">
                                    <img src="{playlist_info['img_url']}" alt="{playlist}" width="70" style="border-radius:8px; box-shadow:0 2px 8px #0001; display:block;"/>
                                </a>
                                <span style="font-size: 0.95em; font-weight: 600; text-align: center; display: block; color: #222; margin-top: 6px;">{playlist}</span>
                            </div>""",
                        unsafe_allow_html=True
                    )