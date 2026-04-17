import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

st.set_page_config(
    page_title="Product Discovery Tool",
    page_icon="🚀",
    layout="centered",
)

if not os.environ.get("ANTHROPIC_API_KEY"):
    st.warning(
        "**ANTHROPIC_API_KEY not set.** "
        "Create a `.env` file (see `.env.example`) or set the environment variable before using AI features.",
        icon="⚠️",
    )

st.title("Product Discovery Tool")
st.caption("A research & testing toolkit for neobank product teams.")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("🔍 Painpoints Finder")
    st.markdown(
        "Scrape Google Play reviews of competitor apps, filter by sentiment, "
        "and use AI to extract the top pain point categories with real user quotes."
    )
    st.page_link("pages/1_Painpoints_Finder.py", label="Open Painpoints Finder →")

with col2:
    st.subheader("🧑 Persona Interviews")
    st.markdown(
        "Describe a feature or user flow and simulate feedback from 5 real neobank personas — "
        "impatient users, analytical early adopters, cautious users, and more."
    )
    st.page_link("pages/2_Persona_Interviews.py", label="Open Persona Interviews →")

st.divider()
st.caption("v1 · Built with Streamlit + Claude API")
