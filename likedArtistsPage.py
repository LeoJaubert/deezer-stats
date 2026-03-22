import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
import streamlit as st
import requests

#API call to obtain infos about artist
@st.cache_data(show_spinner = False)
def getArtistInfoFromId(artist_link):
    try:
        artist_id = artist_link.rstrip('/').split('/')[-1]
        url = f"https://api.deezer.com/artist/{artist_id}"
        response = requests.get(url, timeout = 100)
        data = response.json()

        nb_fan = int(data.get("nb_fan", 0))

        return {
            "img_url": data["picture_medium"],
            "nb_album": int(data["nb_album"]),
            "nb_fan_formatted": f"{nb_fan:,}",
            "url": url
        }

    except (requests.exceptions.RequestException, KeyError, ValueError):
        return None

#Do all API requests in bulk
@st.cache_data(show_spinner = False)
def getAllArtistsInfo(artist_links: tuple):
    def fetch(artist_link):
        return artist_link, getArtistInfoFromId(artist_link)

    results = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch, link): link for link in artist_links}
        for future in as_completed(futures):
            link, info = future.result()
            results[link] = info
    return results

#API call to obtain the 5 top songs from tracklist
def getTopSongsFromTracklist(url):
    try:
        url = url + "/top?limit=5"
        response = requests.get(url, timeout = 100)
        data = response.json()

        top_songs_dict = {}

        for track in data.get("data", []):
            track_id = track.get("id")
            title = track.get("title")
            link = track.get("link")

            top_songs_dict[track_id] = {
                "title": title,
                "link": link
            }

        return top_songs_dict

    except requests.exceptions.RequestException:
        return None

#Function needed to use placeholder in HTML
def getBase64Image(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

#Popup appearing when clicking on the button containing infos about artist
@st.dialog("Détails de l'artiste")
def showArtistModal(artist, link, artist_info, top_songs):
    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.markdown(f"""
            # 🧑‍🎤 {artist}
            💿 **Sorties** : {artist_info['nb_album']}  
            🕺 **Fans** : {artist_info['nb_fan_formatted']}  
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
        st.markdown("## 🔥 Top titres")

        #Print the top 5 songs of the artist with a hypertext link
        for _, top_song in top_songs.items():
            st.write(f"🎵 [{top_song['title']}]({top_song['link']})")

#--------------Code starts here--------------#
def likedArtists(sheet):
    df = sheet
    st.title("🧑‍🎤 Artistes likés", anchor = False)
    st.markdown("---")

    artists_dict = {}
    for i in range(len(df)):
        artist = df.iloc[i]["Artist"]
        link = df.iloc[i]["Link"]
        artists_dict[artist] = link

    #Search bar
    search = st.text_input(f"🔎 Rechercher parmi les {len(df)} artistes :")
    if search:
        artists_dict = {k: v for k, v in artists_dict.items() if search.lower() in k.lower()}

    #Sort in alphabetical order
    artists_dict = dict(sorted(artists_dict.items(), key = lambda item: item[0].lower()))

    img_base64 = getBase64Image("pictures/placeholder-picture.jpg")
    placeholder = f"data:image/jpeg;base64,{img_base64}"

    #Print 4 by 4 artists with their picture
    artists = list(artists_dict.items())
    all_links = tuple(link for _, link in artists)
    artists_info = getAllArtistsInfo(all_links)
    row_items = 4
    for i in range(0, len(artists), row_items):
        cols = st.columns(row_items)
        for j, (artist, link) in enumerate(artists[i:i+row_items]):
            with cols[j]:
                artist_info = artists_info.get(link)
                #Correct format of the link
                if not link.startswith("http"):
                    link = "https://" + link.lstrip("/")
                #If artist not found, use a placeholder image and do not display the link
                if artist_info is None:
                    st.markdown(
                        f"""<div style="display: flex; flex-direction: column; align-items: center; margin-top:6px;">
                                <img src="{placeholder}" alt="{artist}" width="70" style="border-radius:8px; box-shadow:0 2px 8px #0001; display:block;"/>
                                <span style="font-size: 0.95em; font-weight: 600; text-align: center; display: block; color: #222; margin-top: 6px;">{artist}</span>
                            </div>""",
                        unsafe_allow_html = True
                    )
                else:
                    url = artist_info["url"]
                    st.markdown(
                        f"""
                        <div style="display:flex; flex-direction:column; align-items:center;">
                            <img src="{artist_info['img_url']}"
                                width="70"
                                style="border-radius:8px; box-shadow:0 2px 8px #0001; margin-bottom:8px">
                        </div>
                        """,
                        unsafe_allow_html = True
                    )

                    #Button with artist name
                    if st.button(
                        artist,
                        use_container_width = True,
                        type = "primary"
                    ):
                        top_songs = getTopSongsFromTracklist(url)
                        showArtistModal(artist, link, artist_info, top_songs)
