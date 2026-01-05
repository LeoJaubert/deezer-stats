import base64
from datetime import datetime
import pandas as pd
import streamlit as st
import requests

def format_duration(seconds):
    minutes = seconds // 60
    hours = minutes // 60
    minutes = minutes % 60

    if hours > 0:
        if minutes == 0:
            return f"{hours} heure" if hours == 1 else f"{hours} heures"
        return f"{hours} heure {minutes} minutes" if hours == 1 else f"{hours} heures {minutes} minutes"
    else:
        return f"{minutes} minute" if minutes == 1 else f"{minutes} minutes"

#API call to obtain infos about album
@st.cache_data(show_spinner=False)
def get_album_info_from_id(album_link):
    try:
        album_id = album_link.rstrip('/').split('/')[-1]
        url = f"https://api.deezer.com/album/{album_id}"
        response = requests.get(url)
        data = response.json()
        
        main_artists = []

        for contributor in data["contributors"]:
            if contributor.get("role") == "Main":
                main_artists.append(contributor.get("name"))

        artists_str = ", ".join(main_artists)

        fans = int(data.get("fans", 0))
        duration = int(data.get("duration", 0))
        release_date = data.get("release_date", 0)

        return {
            "img_url": data["cover_medium"],
            "nb_tracks": int(data["nb_tracks"]),
            "fans_formatted": f"{fans:,}",
            "duration_formatted": format_duration(duration),
            "release_date_formatted": datetime.strptime(release_date, "%Y-%m-%d").strftime("%d/%m/%Y"),
            "artists": artists_str,
            "url": url
        }

    except Exception:
        return None

#Function needed to use placeholder in HTML
def get_base64_image(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

#API call to obtain the tracklist from album
def get_tracklist_from_album(url):
    try:
        response = requests.get(url)
        data = response.json()

        tracklist_dict = {}

        for track in data["tracks"]["data"]:
            track_id = track.get("id")
            title = track.get("title")
            link = track.get("link")

            tracklist_dict[track_id] = {
                "title": title,
                "link": link
            }

        return tracklist_dict

    except:
        return None

#Popup appearing when clicking on the button containing infos about artist
@st.dialog("Détails de l'album")
def show_album_modal(album, link, album_info, tracklist):

    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.markdown(f"""
            # 💿 {album}
            🧑‍🎤 **Artiste** : {album_info['artists']}\n
            🔢 **Morceaux** : {album_info['nb_tracks']}\n
            🕺 **Fans** : {album_info['fans_formatted']}\n
            ⏱  **Durée** : {album_info['duration_formatted']}\n
            📅 **Sortie** : {album_info['release_date_formatted']}  
        """, unsafe_allow_html = True)

        st.markdown(
            f"""
            <a href="{link}" target="_blank"
            style="
                display:inline-block;
                padding:10px 16px;
                background:#A237FF;
                color:white;
                text-decoration:none;
                border-radius:6px;
                font-weight:600;
            ">
                Ouvrir sur Deezer
            </a>
            """,
            unsafe_allow_html = True
        )

    with right_col:
        st.markdown("## ⏯ Tracklist")

        #Print the full tracklist of the album with a hypertext link
        for track_id, track in tracklist.items():
            st.write(f"🎵 [{track['title']}]({track['link']})")

#--------------Code starts here--------------#
def likedAlbums(file_path):
    df = pd.read_excel(file_path, sheet_name="5_favoriteAlbum")
    st.title("💿 Albums likés")
    st.markdown("---")

    albumsDict = {}
    for i in range(len(df)):
        album = df.iloc[i]["Album Title"]
        link = df.iloc[i]["Link"]
        albumsDict[album] = link

    # Barre de recherche
    search = st.text_input("🔎 Rechercher un album")
    if search:
        albumsDict = {k: v for k, v in albumsDict.items() if search.lower() in k.lower()}

    #Sort in alphabetical order
    albumsDict = dict(sorted(albumsDict.items(), key=lambda item: item[0].lower()))

    img_base64 = get_base64_image("placeholder_pics/placeholder-picture.jpg")
    placeholder = f"data:image/jpeg;base64,{img_base64}"

    #Print 4 by 4 albums with their picture and link to their Deezer page
    albums = list(albumsDict.items())
    row_items = 4
    for i in range(0, len(albums), row_items):
        cols = st.columns(row_items)
        for j, (album, link) in enumerate(albums[i:i+row_items]):
            with cols[j]:
                album_info = get_album_info_from_id(link)
                #Correct format of the link
                if not link.startswith("http"):
                    link = "https://" + link.lstrip("/")
                #If album not found, use a placeholder image and do not display the link
                if album_info is None:
                    st.markdown(
                        f"""<div style="display: flex; flex-direction: column; align-items: center; margin-top:6px;">
                                <img src="{placeholder}" alt="{album}" width="70" style="border-radius:8px; box-shadow:0 2px 8px #0001; display:block;"/>
                                <span style="font-size: 0.95em; font-weight: 600; text-align: center; display: block; color: #222; margin-top: 6px;">{album}</span>
                            </div>""",
                        unsafe_allow_html=True
                    )
                else:
                    url = album_info["url"]
                    st.markdown(
                        f"""
                        <div style="display:flex; flex-direction:column; align-items:center;">
                            <img src="{album_info['img_url']}"
                                width="70"
                                style="border-radius:8px; box-shadow:0 2px 8px #0001; margin-bottom:8px">
                        </div>
                        """,
                        unsafe_allow_html = True
                    )

                    #Button with album name
                    if st.button(
                        album,
                        key = f"btn_{album}_{i}_{j}",
                        use_container_width = True,
                        type = "primary"
                    ):
                        tracklist = get_tracklist_from_album(url)
                        show_album_modal(album, link, album_info, tracklist)
