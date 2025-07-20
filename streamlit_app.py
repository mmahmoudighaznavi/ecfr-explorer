import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(page_title="eCFR Explorer", layout="wide")
st.title("📘 eCFR Explorer")
st.markdown("Search and analyze sections of the Electronic Code of Federal Regulations (eCFR).")

# --- Initialize session state ---
for key in ["search_df", "authority_df", "wordcount_df", "available_titles", "available_authorities"]:
    if key not in st.session_state:
        st.session_state[key] = None

# --- Tabs Layout ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔍 Search",
    "📊 Word Count by Authority",
    "📈 Word Count by Title",
    "🔐 Checksum by Authority",
    "📉 Historical Word Count",
    "📚 Readability by Authority"
])

# --- 🔍 Tab 1: Search ---
with tab1:
    st.subheader("Search eCFR Sections")

    # Fetch available titles (only once)
    if st.session_state.available_titles is None:
        try:
            response = requests.get("http://localhost:8000/titles")
            if response.status_code == 200:
                st.session_state.available_titles = response.json()
        except:
            st.warning("Could not load titles.")

    query = st.text_input("Enter keyword (e.g., FDA):")
    selected_title = st.selectbox("Optional: Filter by Title", options=["All"] + st.session_state.available_titles if st.session_state.available_titles else ["All"])

    if st.button("Search"):
        params = {"query": query}
        if selected_title != "All":
            params["title"] = selected_title
        response = requests.get("http://localhost:8000/search", params=params)
        if response.status_code == 200:
            results = response.json()
            if results:
                df = pd.DataFrame(results)
                st.session_state.search_df = df
                st.success(f"Found {len(df)} matching sections.")
            else:
                st.warning("No results found.")
                st.session_state.search_df = None
        else:
            st.error("Search failed.")

    if st.session_state.search_df is not None:
        st.dataframe(st.session_state.search_df[["title", "part_title", "text"]])

# --- 📊 Tab 2: Word Count by Authority ---
with tab2:
    st.subheader("Top Authorities by Word Count")

    if st.button("Load Authority Stats"):
        with st.spinner("Loading data..."):
            response = requests.get("http://localhost:8000/stats/by-authority")
            if response.status_code == 200:
                df = pd.DataFrame(response.json())
                df = df.sort_values(by="word_count", ascending=False)
                st.session_state.authority_df = df
                st.session_state.available_authorities = sorted(df["authority"].dropna().unique().tolist())
            else:
                st.error("Failed to load authority data.")
                st.session_state.authority_df = None

    if st.session_state.authority_df is not None:
        selected_auth = st.selectbox("Filter by Authority (optional)", options=["All"] + st.session_state.available_authorities)

        # Filter and format data
        filtered_df = st.session_state.authority_df
        if selected_auth != "All":
            filtered_df = filtered_df[filtered_df["authority"] == selected_auth]

        # Limit to Top 20 and shorten labels
        filtered_df = filtered_df.head(20).copy()
        filtered_df["label"] = filtered_df["authority"].str.slice(0, 50) + "..."

        fig = px.bar(
            filtered_df,
            x="word_count",
            y="label",
            orientation="h",
            hover_data=["authority"],
            labels={"word_count": "Word Count", "label": "Authority"},
            title="Top 20 Authorities by Word Count"
        )
        st.plotly_chart(fig, use_container_width=True)


# --- 📈 Tab 3: Word Count by Title ---
with tab3:
    st.subheader("Total Word Count by Title")

    if st.button("Load Title Stats"):
        with st.spinner("Loading data..."):
            response = requests.get("http://localhost:8000/stats/wordcount")
            if response.status_code == 200:
                df = pd.DataFrame(response.json())
                st.session_state.wordcount_df = df
            else:
                st.error("Failed to load title stats.")
                st.session_state.wordcount_df = None

    if st.session_state.wordcount_df is not None:
        st.dataframe(st.session_state.wordcount_df)

        fig = px.bar(
            st.session_state.wordcount_df.sort_values(by="title"),
            x="title",
            y="word_count",
            title="Word Count by Title",
            labels={"title": "Title", "word_count": "Word Count"},
            color_discrete_sequence=["royalblue"]
        )
        fig.update_layout(
            xaxis=dict(
                tickmode='linear',
                tick0=1,
                dtick=1,
                tickangle=0
            ),
            yaxis=dict(title="Word Count"),
            margin=dict(l=40, r=20, t=60, b=60),
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)


# --- 🔐 Tab 4: Checksum by Authority ---
with tab4:
    st.subheader("Checksum of Regulation Text by Authority")

    if st.session_state.available_authorities:
        selected_auth = st.selectbox("Select an Authority", st.session_state.available_authorities, key="checksum_selector")
        if st.button("Get Checksum"):
            with st.spinner("Computing checksum..."):
                url = f"http://localhost:8000/checksum/{selected_auth}"
                response = requests.get(url)
                if response.status_code == 200:
                    checksum = response.json().get("checksum")
                    st.code(checksum, language="text")
                else:
                    st.error("Failed to compute checksum.")
    else:
        st.info("Please load authorities from Tab 2 first.")

# --- 📉 Tab 5: Historical Word Count ---
with tab5:
    st.subheader("Simulated Historical Word Count by Title")

    if st.session_state.available_titles:
        selected_title = st.selectbox("Select a Title", st.session_state.available_titles, key="history_selector")
        if st.button("Load History"):
            url = f"http://localhost:8000/history/{selected_title}"
            response = requests.get(url)
            if response.status_code == 200:
                history = response.json().get("history", [])
                df = pd.DataFrame(history)
                fig = px.line(df, x="date", y="word_count", title=f"Historical Word Count for Title {selected_title}")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Failed to load historical data.")
    else:
        st.info("Please load titles from Tab 1 or 3 first.")

# --- 📘 Tab 6: Readability by Authority ---
with tab6:
    st.subheader("Readability Score by Authority (Flesch-Kincaid Grade Level)")

    if st.button("Load Readability Scores"):
        with st.spinner("Loading readability scores..."):
            try:
                response = requests.get("http://localhost:8000/stats/custom-readability")
                if response.status_code == 200:
                    readability_data = response.json()
                    if isinstance(readability_data, list) and len(readability_data) > 0:
                        df = pd.DataFrame(readability_data)
                        st.session_state.readability_df = df
                    else:
                        st.warning("No readability data available.")
                        st.session_state.readability_df = None
                else:
                    st.error(f"Failed to fetch readability scores. Server responded with: {response.status_code}")
                    st.session_state.readability_df = None
            except Exception as e:
                st.error(f"Failed to fetch readability scores: {e}")
                st.session_state.readability_df = None

    if st.session_state.get("readability_df") is not None:
        st.dataframe(st.session_state.readability_df)

        fig = px.bar(
            st.session_state.readability_df,
            x="authority",
            y="readability",
            title="Average Flesch-Kincaid Grade Level by Authority"
        )
        st.plotly_chart(fig, use_container_width=True)
