import streamlit as st
import sqlite3
from datetime import datetime
import time

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ChatBox",
    page_icon="💬",
    layout="centered"
)

DB_NAME = "chatbox.db"


# ============================================================
# DATABASE
# ============================================================

def get_connection():
    return sqlite3.connect(
        DB_NAME,
        check_same_thread=False
    )


def create_database():

    conn = get_connection()
    cursor = conn.cursor()

    # Messages
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            message TEXT DEFAULT '',
            sticker TEXT DEFAULT '',
            timestamp TEXT NOT NULL
        )
    """)

    # Read receipts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS message_views (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            seen_at TEXT NOT NULL,
            UNIQUE(message_id, username)
        )
    """)

    conn.commit()
    conn.close()


def save_message(username, message="", sticker=""):

    conn = get_connection()
    cursor = conn.cursor()

    timestamp = datetime.now().strftime(
        "%d-%m-%Y %I:%M %p"
    )

    cursor.execute("""
        INSERT INTO messages
        (username, message, sticker, timestamp)
        VALUES (?, ?, ?, ?)
    """, (
        username,
        message,
        sticker,
        timestamp
    ))

    conn.commit()
    conn.close()


def get_messages():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            username,
            message,
            sticker,
            timestamp
        FROM messages
        ORDER BY id ASC
    """)

    data = cursor.fetchall()

    conn.close()

    return data


def mark_seen(username):

    conn = get_connection()
    cursor = conn.cursor()

    messages = get_messages()

    seen_time = datetime.now().strftime(
        "%d-%m-%Y %I:%M %p"
    )

    for message_id, sender, message, sticker, timestamp in messages:

        # Don't mark your own messages
        if sender != username:

            cursor.execute("""
                INSERT OR IGNORE INTO message_views
                (message_id, username, seen_at)
                VALUES (?, ?, ?)
            """, (
                message_id,
                username,
                seen_time
            ))

    conn.commit()
    conn.close()


def get_seen_users(message_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT username
        FROM message_views
        WHERE message_id = ?
        ORDER BY id
    """, (message_id,))

    users = [
        row[0]
        for row in cursor.fetchall()
    ]

    conn.close()

    return users


def get_members():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT username
        FROM messages
        ORDER BY username
    """)

    users = [
        row[0]
        for row in cursor.fetchall()
    ]

    conn.close()

    return users


create_database()


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.stApp {
    background-color: #111827;
}

.main-title {
    text-align: center;
    color: #25D366;
    font-size: 40px;
    font-weight: bold;
}

.subtitle {
    text-align: center;
    color: #9CA3AF;
    margin-bottom: 20px;
}

.user-box {
    background-color: #14532D;
    padding: 12px;
    border-radius: 10px;
    text-align: center;
    color: white;
    margin-bottom: 20px;
}

.time-text {
    color: #6B7280;
    font-size: 11px;
}

.seen-text {
    color: #9CA3AF;
    font-size: 11px;
}

.sticker {
    font-size: 50px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOGIN / USERNAME
# ============================================================

if "username" not in st.session_state:

    st.markdown(
        '<div class="main-title">💬 ChatBox</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Friends Group Chat</div>',
        unsafe_allow_html=True
    )

    st.info(
        "👋 Welcome! Enter your username to join the group."
    )

    username = st.text_input(
        "Username",
        placeholder="Example: Vrishti"
    )

    if st.button(
        "🚀 Join ChatBox",
        use_container_width=True
    ):

        username = username.strip()

        if username:

            st.session_state.username = username

            st.rerun()

        else:

            st.warning(
                "Please enter a username."
            )

    st.stop()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">💬 ChatBox</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">👥 Friends Group</div>',
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div class="user-box">
        👤 You are chatting as <b>{st.session_state.username}</b>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# MARK OTHER PEOPLE'S MESSAGES AS SEEN
# ============================================================

mark_seen(
    st.session_state.username
)


# ============================================================
# DISPLAY MESSAGES
# ============================================================

messages = get_messages()

if not messages:

    st.info(
        "💬 No messages yet. Start the conversation!"
    )

else:

    for (
        message_id,
        username,
        message,
        sticker,
        timestamp
    ) in messages:

        # ----------------------------------------------------
        # YOUR MESSAGE
        # ----------------------------------------------------

        if username == st.session_state.username:

            with st.chat_message(
                "user",
                avatar="🧑"
            ):

                st.markdown(
                    f"**You**"
                )

                if sticker:

                    st.markdown(
                        f'<div class="sticker">{sticker}</div>',
                        unsafe_allow_html=True
                    )

                else:

                    st.write(message)

                st.caption(
                    timestamp
                )

                seen_users = get_seen_users(
                    message_id
                )

                if seen_users:

                    st.caption(
                        "✓ Seen by "
                        + ", ".join(seen_users)
                    )

                else:

                    st.caption(
                        "✓ Sent"
                    )


        # ----------------------------------------------------
        # OTHER USER
        # ----------------------------------------------------

        else:

            with st.chat_message(
                "assistant",
                avatar="👤"
            ):

                st.markdown(
                    f"**{username}**"
                )

                if sticker:

                    st.markdown(
                        f'<div class="sticker">{sticker}</div>',
                        unsafe_allow_html=True
                    )

                else:

                    st.write(message)

                st.caption(
                    timestamp
                )


# ============================================================
# STICKERS
# ============================================================

st.divider()

st.subheader("😄 Stickers")

stickers = [
    "😂",
    "❤️",
    "👍",
    "🎉",
    "🔥",
    "😍",
    "🤣",
    "👏"
]

columns = st.columns(8)

for i, sticker in enumerate(stickers):

    with columns[i]:

        if st.button(
            sticker,
            key=f"sticker_{i}",
            use_container_width=True
        ):

            save_message(
                st.session_state.username,
                sticker=sticker
            )

            st.rerun()


# ============================================================
# GROUP MEMBERS
# ============================================================

with st.expander("👥 Group Members"):

    members = get_members()

    if members:

        for member in members:

            if member == st.session_state.username:

                st.write(
                    f"🟢 {member} **(You)**"
                )

            else:

                st.write(
                    f"⚪ {member}"
                )

    else:

        st.write(
            "No other members yet."
        )


# ============================================================
# MESSAGE INPUT
# ============================================================

message = st.chat_input(
    "Type your message..."
)

if message:

    save_message(
        st.session_state.username,
        message=message
    )

    st.rerun()