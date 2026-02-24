import streamlit as st

from playlist_logic import (
    DEFAULT_PROFILE,
    Song,
    build_playlists,
    compute_playlist_stats,
    genre_distribution,
    history_summary,
    lucky_pick,
    merge_playlists,
    normalize_song,
    search_songs_multi,
)


def init_state():
    """Initialize Streamlit session state."""
    if "songs" not in st.session_state:
        st.session_state.songs = default_songs()
    if "profile" not in st.session_state:
        st.session_state.profile = dict(DEFAULT_PROFILE)
    if "history" not in st.session_state:
        st.session_state.history = []
    if "recent_songs" not in st.session_state:
        st.session_state.recent_songs = []


def default_songs():
    """Return a default list of songs."""
    return [
        {
            "title": "Thunderstruck",
            "artist": "AC/DC",
            "genre": "rock",
            "energy": 9,
            "tags": ["classic", "guitar"],
        },
        {
            "title": "Lo-fi Rain",
            "artist": "DJ Calm",
            "genre": "lofi",
            "energy": 2,
            "tags": ["study"],
        },
        {
            "title": "Night Drive",
            "artist": "Neon Echo",
            "genre": "electronic",
            "energy": 6,
            "tags": ["synth"],
        },
        {
            "title": "Soft Piano",
            "artist": "Sleep Sound",
            "genre": "ambient",
            "energy": 1,
            "tags": ["sleep"],
        },
        {
            "title": "Bohemian Rhapsody",
            "artist": "Queen",
            "genre": "rock",
            "energy": 8,
            "tags": ["classic", "opera"],
        },
        {
            "title": "Blinding Lights",
            "artist": "The Weeknd",
            "genre": "pop",
            "energy": 8,
            "tags": ["synth", "dance"],
        },
        {
            "title": "Take Five",
            "artist": "Dave Brubeck",
            "genre": "jazz",
            "energy": 4,
            "tags": ["classic", "instrumental"],
        },
        {
            "title": "Strobe",
            "artist": "Deadmau5",
            "genre": "electronic",
            "energy": 7,
            "tags": ["progressive", "long"],
        },
        {
            "title": "Weightless",
            "artist": "Marconi Union",
            "genre": "ambient",
            "energy": 1,
            "tags": ["relax", "sleep"],
        },
        {
            "title": "Smells Like Teen Spirit",
            "artist": "Nirvana",
            "genre": "rock",
            "energy": 9,
            "tags": ["grunge", "90s"],
        },
        {
            "title": "Levitating",
            "artist": "Dua Lipa",
            "genre": "pop",
            "energy": 8,
            "tags": ["dance", "party"],
        },
        {
            "title": "So What",
            "artist": "Miles Davis",
            "genre": "jazz",
            "energy": 3,
            "tags": ["trumpet", "cool"],
        },
        {
            "title": "Midnight City",
            "artist": "M83",
            "genre": "electronic",
            "energy": 7,
            "tags": ["indie", "dream"],
        },
        {
            "title": "Gymnopedie No.1",
            "artist": "Erik Satie",
            "genre": "ambient",
            "energy": 1,
            "tags": ["piano", "calm"],
        },
        {
            "title": "Sweet Child O' Mine",
            "artist": "Guns N' Roses",
            "genre": "rock",
            "energy": 8,
            "tags": ["guitar", "80s"],
        },
        {
            "title": "Bad Guy",
            "artist": "Billie Eilish",
            "genre": "pop",
            "energy": 6,
            "tags": ["bass", "dark"],
        },
        {
            "title": "Fly Me to the Moon",
            "artist": "Frank Sinatra",
            "genre": "jazz",
            "energy": 5,
            "tags": ["vocal", "swing"],
        },
        {
            "title": "Sandstorm",
            "artist": "Darude",
            "genre": "electronic",
            "energy": 10,
            "tags": ["trance", "meme"],
        },
        {
            "title": "Clair de Lune",
            "artist": "Claude Debussy",
            "genre": "ambient",
            "energy": 2,
            "tags": ["piano", "classical"],
        },
        {
            "title": "Hotel California",
            "artist": "Eagles",
            "genre": "rock",
            "energy": 6,
            "tags": ["classic", "guitar"],
        },
        {
            "title": "Uptown Funk",
            "artist": "Mark Ronson ft. Bruno Mars",
            "genre": "pop",
            "energy": 9,
            "tags": ["funk", "dance"],
        },
        {
            "title": "Feeling Good",
            "artist": "Nina Simone",
            "genre": "jazz",
            "energy": 6,
            "tags": ["soul", "vocal"],
        },
    ]


def profile_sidebar():
    """Render and update the user profile."""
    st.sidebar.header("Mood profile")

    profile = st.session_state.profile

    profile["name"] = st.sidebar.text_input(
        "Profile name",
        value=str(profile.get("name", "")),
    )

    col1, col2 = st.sidebar.columns(2)
    with col1:
        # Fix: was st.sidebar.slider inside a column context, which bypasses the
        # column layout; use st.slider so it renders inside the column
        profile["hype_min_energy"] = st.slider(
            "Hype min energy",
            min_value=1,
            max_value=10,
            value=int(profile.get("hype_min_energy", 7)),
        )
    with col2:
        profile["chill_max_energy"] = st.slider(
            "Chill max energy",
            min_value=1,
            max_value=10,
            value=int(profile.get("chill_max_energy", 3)),
        )

    genres = ["rock", "lofi", "pop", "jazz", "electronic", "ambient", "other"]
    current_genre = profile.get("favorite_genre", "rock")
    # Fix: was always index=0 (rock), ignoring the previously saved genre preference
    current_index = genres.index(current_genre) if current_genre in genres else 0
    profile["favorite_genre"] = st.sidebar.selectbox(
        "Favorite genre",
        options=genres,
        index=current_index,
    )

    profile["include_mixed"] = st.sidebar.checkbox(
        "Include Mixed playlist in views",
        value=bool(profile.get("include_mixed", True)),
    )

    st.sidebar.write("Current profile:", profile["name"])


def add_song_sidebar():
    """Render the Add Song controls in the sidebar."""
    st.sidebar.header("Add a song")

    title = st.sidebar.text_input("Title")
    artist = st.sidebar.text_input("Artist")
    genre = st.sidebar.selectbox(
        "Genre",
        options=["rock", "lofi", "pop", "jazz", "electronic", "ambient", "other"],
    )
    energy = st.sidebar.slider("Energy", min_value=1, max_value=10, value=5)
    tags_text = st.sidebar.text_input("Tags (comma separated)")

    if st.sidebar.button("Add to playlist"):
        if not title or not artist:
            st.sidebar.warning("Title and artist are required.")
        else:
            raw_tags = [t.strip() for t in tags_text.split(",")]
            tags = [t for t in raw_tags if t]

            song: Song = {
                "title": title,
                "artist": artist,
                "genre": genre,
                "energy": energy,
                "tags": tags,
            }
            normalized = normalize_song(song)
            st.session_state.songs.append(normalized)
            st.session_state.recent_songs.append(normalized)
            st.sidebar.success(f'Added "{title}"')


def playlist_tabs(playlists):
    """Render playlists in tabs."""
    include_mixed = st.session_state.profile.get("include_mixed", True)

    tab_labels = ["Hype", "Chill"]
    if include_mixed:
        tab_labels.append("Mixed")

    tabs = st.tabs(tab_labels)

    for label, tab in zip(tab_labels, tabs):
        with tab:
            render_playlist(label, playlists.get(label, []))


def render_playlist(label, songs):
    st.subheader(f"{label} playlist")
    if not songs:
        st.write("No songs in this playlist.")
        return

    col_search, col_sort = st.columns([3, 2])
    with col_search:
        query = st.text_input(
            "Search",
            key=f"search_{label}",
            placeholder="Title, artist, genre, or tag...",
        )
    with col_sort:
        sort_by = st.selectbox(
            "Sort by",
            options=["Default", "Title", "Artist", "Energy ↑", "Energy ↓"],
            key=f"sort_{label}",
        )

    filtered = search_songs_multi(songs, query)

    if sort_by == "Title":
        filtered = sorted(filtered, key=lambda s: str(s.get("title", "")).lower())
    elif sort_by == "Artist":
        filtered = sorted(filtered, key=lambda s: str(s.get("artist", "")).lower())
    elif sort_by == "Energy ↑":
        filtered = sorted(filtered, key=lambda s: s.get("energy", 0))
    elif sort_by == "Energy ↓":
        filtered = sorted(filtered, key=lambda s: s.get("energy", 0), reverse=True)

    if not filtered:
        st.write("No matching songs.")
        return

    for song in filtered:
        mood = song.get("mood", "?")
        tags = ", ".join(song.get("tags", []))
        st.write(
            f"- **{song['title']}** by {song['artist']} "
            f"(genre: {song['genre']}, energy: {song['energy']}, mood: {mood}) "
            f"[{tags}]"
        )


def lucky_section(playlists):
    """Render the lucky pick controls and result."""
    st.header("Lucky pick")

    mode = st.selectbox(
        "Pick from",
        options=["any", "hype", "chill"],
        index=0,
    )

    if st.button("Feeling lucky"):
        pick = lucky_pick(playlists, mode=mode)
        if pick is None:
            st.warning("No songs available for this mode.")
            return

        st.success(
            f"Lucky song: {pick['title']} by {pick['artist']} "
            f"(mood {pick.get('mood', '?')})"
        )

        history = st.session_state.history
        history.append(pick)
        st.session_state.history = history


def stats_section(playlists):
    """Render statistics based on the playlists."""
    st.header("Playlist stats")

    stats = compute_playlist_stats(playlists)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total songs", stats["total_songs"])
    col2.metric("Hype songs", stats["hype_count"])
    col3.metric("Chill songs", stats["chill_count"])

    col4, col5, col6 = st.columns(3)
    col4.metric("Mixed songs", stats["mixed_count"])
    col5.metric("Hype ratio", f"{stats['hype_ratio']:.2f}")
    col6.metric("Average energy", f"{stats['avg_energy']:.2f}")

    top_artist = stats["top_artist"]
    if top_artist:
        st.write(
            f"Most common artist: **{top_artist}** "
            f"({stats['top_artist_count']} songs)"
        )
    else:
        st.write("No top artist yet.")

    all_songs = [s for songs in playlists.values() for s in songs]
    if all_songs:
        st.subheader("Genre distribution")
        dist = genre_distribution(all_songs)
        for g, count in dist.items():
            bar = "█" * count
            st.write(f"**{g}**: {bar} ({count})")


def history_section():
    """Render the pick history overview."""
    st.header("History")

    history = st.session_state.history
    if not history:
        st.write("No history yet.")
        return

    summary = history_summary(history)
    st.write("Recent picks by mood:", summary)

    show_details = st.checkbox("Show full history")
    if show_details:
        for song in history:
            st.write(
                f"{song.get('mood', '?')}: {song['title']} by {song['artist']}"
            )


def recently_added_section():
    """Show songs added during this session, most recent first."""
    recent = st.session_state.recent_songs
    if not recent:
        return

    st.header("Recently added")
    st.caption(f"{len(recent)} song(s) added this session")
    for song in reversed(recent[-10:]):
        tags = ", ".join(song.get("tags", []))
        st.write(
            f"- **{song['title']}** by {song['artist']} "
            f"(genre: {song['genre']}, energy: {song['energy']}) [{tags}]"
        )


def delete_songs_sidebar():
    """Render controls to remove songs from the library."""
    all_songs = st.session_state.songs
    if not all_songs:
        return

    st.sidebar.header("Delete songs")
    to_delete = st.sidebar.multiselect(
        "Select songs to remove",
        options=list(range(len(all_songs))),
        format_func=lambda i: f"{all_songs[i]['title']} — {all_songs[i]['artist']}",
    )

    if st.sidebar.button("Remove selected") and to_delete:
        deleted_keys = {(all_songs[i]["title"], all_songs[i]["artist"]) for i in to_delete}
        st.session_state.songs = [
            s for i, s in enumerate(all_songs) if i not in to_delete
        ]
        st.session_state.recent_songs = [
            s for s in st.session_state.recent_songs
            if (s["title"], s["artist"]) not in deleted_keys
        ]


def clear_controls():
    """Render a small section for clearing data."""
    st.sidebar.header("Manage data")
    if st.sidebar.button("Reset songs to default"):
        st.session_state.songs = default_songs()
        st.session_state.recent_songs = []
    if st.sidebar.button("Clear history"):
        st.session_state.history = []


def main():
    st.set_page_config(page_title="Playlist Chaos", layout="wide")
    st.title("Playlist Chaos")

    st.write(
        "An AI assistant tried to build a smart playlist engine. "
        "The code runs, but the behavior is a bit unpredictable."
    )

    init_state()
    profile_sidebar()
    add_song_sidebar()
    delete_songs_sidebar()
    clear_controls()

    profile = st.session_state.profile
    songs = st.session_state.songs

    base_playlists = build_playlists(songs, profile)
    merged_playlists = merge_playlists(base_playlists, {})

    playlist_tabs(merged_playlists)
    if st.session_state.recent_songs:
        st.divider()
        recently_added_section()
    st.divider()
    lucky_section(merged_playlists)
    st.divider()
    stats_section(merged_playlists)
    st.divider()
    history_section()


if __name__ == "__main__":
    main()
