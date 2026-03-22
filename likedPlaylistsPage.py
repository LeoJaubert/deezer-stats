import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
import streamlit as st
import requests

def formatDuration(seconds):
    minutes = seconds // 60
    hours = minutes // 60
    minutes = minutes % 60

    if hours > 0:
        if minutes == 0:
            return f"{hours} heure" if hours == 1 else f"{hours} heures"
        return f"{hours} heure {minutes} minutes" if hours == 1 else f"{hours} heures {minutes} minutes"
    return f"{minutes} minute" if minutes == 1 else f"{minutes} minutes"

#API call to obtain infos about playlist
@st.cache_data(show_spinner = False)
def getPlaylistInfoFromId(playlist_link):
    try:
        playlist_id = playlist_link.rstrip('/').split('/')[-1]
        url = f"https://api.deezer.com/playlist/{playlist_id}"
        response = requests.get(url, timeout = 10)
        data = response.json()

        fans = int(data.get("fans", 0))
        duration = int(data.get("duration", 0))

        return {
            "img_url": data["picture_medium"],
            "nb_tracks": data["nb_tracks"],
            "fans_formatted": f"{fans:,}",
            "duration_formatted": formatDuration(duration),
            "description": data["description"],
            "url": url
        }

    except (requests.exceptions.RequestException, KeyError, ValueError):
        return None

#Do all API requests in bulk
@st.cache_data(show_spinner = False)
def getAllPlaylistsInfo(playlist_links: tuple):
    def fetch(playlist_link):
        return playlist_link, getPlaylistInfoFromId(playlist_link)

    results = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch, link): link for link in playlist_links}
        for future in as_completed(futures):
            link, info = future.result()
            results[link] = info
    return results

#Function needed to use placeholder in HTML
def getBase64Image(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

#API call to obtain the first 5 songs of playlist
def getFirstSongsOfPlaylist(url):
    try:
        response = requests.get(url, timeout = 10)
        data = response.json()

        first_songs_dict = {}

        for track in data["tracks"]["data"][:5]:
            track_id = track.get("id")
            title = track.get("title")
            link = track.get("link")

            first_songs_dict[track_id] = {
                "title": title,
                "link": link
            }

        return first_songs_dict

    except requests.exceptions.RequestException:
        return None

#Popup appearing when clicking on the button containing infos about playlist
@st.dialog("Détails de la playlist")
def showPlaylistModal(playlist, link, playlist_info, first_songs):

    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.markdown(f"""
            # 🔀 {playlist}
            🔢 **Morceaux** : {playlist_info['nb_tracks']}\n
            🕺 **Fans** : {playlist_info['fans_formatted']}\n
            ⏱  **Durée** : {playlist_info['duration_formatted']}\n
            🔠 **Description** : {playlist_info['description']} 
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
        st.markdown("## 🔥 Derniers titres")

        #Print the last 5 songs of the playlist with a hypertext link
        for _, song in first_songs.items():
            st.write(f"🎵 [{song['title']}]({song['link']})")

#--------------Code starts here--------------#
def likedPlaylists(sheet):
    df = sheet
    st.title("🎶 Playlists likées", anchor = False)
    st.markdown("---")

    playlists_dict = {}
    for i in range(len(df)):
        playlist = df.iloc[i]["Playlist Title"]
        link = df.iloc[i]["Link"]
        playlists_dict[playlist] = link

    #Search bar
    search = st.text_input(f"🔎 Rechercher parmi les {len(df)} playlists :")
    if search:
        playlists_dict = {k: v for k, v in playlists_dict.items() if search.lower() in k.lower()}
    #Sort in alphabetical order
    playlists_dict = dict(sorted(playlists_dict.items(), key=lambda item: item[0].lower()))

    img_base64 = getBase64Image("pictures/placeholder-picture.jpg")
    placeholder = f"data:image/jpeg;base64,{img_base64}"

    #Print 4 by 4 playlists with their picture and link to their Deezer page
    playlists = list(playlists_dict.items())
    all_links = tuple(link for _, link in playlists)
    playlists_info = getAllPlaylistsInfo(all_links)
    row_items = 4
    for i in range(0, len(playlists), row_items):
        cols = st.columns(row_items)
        for j, (playlist, link) in enumerate(playlists[i:i+row_items]):
            with cols[j]:
                playlist_info = playlists_info.get(link)
                #Correct format of the link
                if not link.startswith("http"):
                    link = "https://" + link.lstrip("/")
                #If playlist not found, use a placeholder image and do not display the link
                if playlist_info is None:
                    st.markdown(
                        f"""<div style="display: flex; flex-direction: column; align-items: center; margin-top:6px;">
                                <img src="{placeholder}" alt="{playlist}" width="70" style="border-radius:8px; box-shadow:0 2px 8px #0001; display:block;"/>
                                <span style="font-size: 0.95em; font-weight: 600; text-align: center; display: block; color: #222; margin-top: 6px;">{playlist}</span>
                            </div>""",
                        unsafe_allow_html = True
                    )
                else:
                    url = playlist_info["url"]
                    st.markdown(
                        f"""
                        <div style="display:flex; flex-direction:column; align-items:center;">
                            <img src="{playlist_info['img_url']}"
                                width="70"
                                style="border-radius:8px; box-shadow:0 2px 8px #0001; margin-bottom:8px">
                        </div>
                        """,
                        unsafe_allow_html = True
                    )

                    #Button with playlist name
                    if st.button(
                        playlist,
                        use_container_width = True,
                        type = "primary"
                    ):
                        top_songs = getFirstSongsOfPlaylist(url)
                        showPlaylistModal(playlist, link, playlist_info, top_songs)
