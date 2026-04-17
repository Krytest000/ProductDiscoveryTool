import json
import streamlit as st
from utils.scraper import run_scrape
from utils.analyzer import analyze_pain_points

st.set_page_config(page_title="Painpoints Finder", page_icon="🔍")
st.title("🔍 Painpoints Finder")
st.caption("Scrape Google Play reviews and extract competitor pain points with AI.")

with st.form("scrape_form"):
    col1, col2 = st.columns(2)
    with col1:
        app_name = st.text_input("App Name", placeholder="e.g. revolut")
    with col2:
        app_id = st.text_input("Google Play App ID", placeholder="e.g. com.revolut.revolut")

    count = st.number_input("Number of reviews to fetch", min_value=10, max_value=1000, value=100, step=10)
    only_negative = st.checkbox("Only negative reviews (≤3★)", value=True)
    run_ai = st.checkbox("Run AI pain point analysis", value=True)
    submitted = st.form_submit_button("Fetch & Analyze", type="primary")

if submitted:
    if not app_name.strip() or not app_id.strip():
        st.error("Please fill in both App Name and App ID.")
        st.stop()

    with st.spinner("Fetching reviews from Google Play..."):
        try:
            processed, raw_path, processed_path = run_scrape(
                app_name.strip(), app_id.strip(), int(count), only_negative
            )
        except Exception as e:
            st.error(f"Failed to fetch reviews: {e}")
            st.stop()

    st.success(f"Fetched {len(processed)} reviews. Saved to `{processed_path}`.")

    if not processed:
        st.warning("No reviews matched the filters. Try increasing the count or unchecking 'Only negative'.")
        st.stop()

    st.subheader("Reviews")
    st.dataframe(
        processed,
        column_config={
            "text": st.column_config.TextColumn("Review", width="large"),
            "rating": st.column_config.NumberColumn("Rating", format="%d ★"),
            "likes": st.column_config.NumberColumn("Likes"),
            "date": "Date",
            "user": "User",
        },
        hide_index=True,
        use_container_width=True,
    )

    st.download_button(
        label="Download as JSON",
        data=json.dumps(processed, ensure_ascii=False, indent=2),
        file_name=f"{app_name}_reviews.json",
        mime="application/json",
    )

    if run_ai:
        st.subheader("AI Pain Point Analysis")
        with st.spinner("Analyzing pain points with Claude..."):
            try:
                pain_points = analyze_pain_points(processed)
            except Exception as e:
                st.error(f"AI analysis failed: {e}")
                st.stop()

        if not pain_points:
            st.info("No pain points returned.")
        else:
            for i, pp in enumerate(pain_points, 1):
                with st.expander(f"{i}. {pp.get('category', 'Unknown')}  —  ~{pp.get('count', '?')} mentions"):
                    st.markdown(f"**{pp.get('description', '')}**")
                    for q in pp.get("quotes", []):
                        st.markdown(f"> {q}")
