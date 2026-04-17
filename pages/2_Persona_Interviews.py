import streamlit as st
from utils.personas import PERSONAS, simulate_persona, generate_summary

st.set_page_config(page_title="Persona Interviews", page_icon="🧑")
st.title("🧑 Persona Interviews")
st.caption("Test a feature or flow through the eyes of 5 real neobank users from Poland.")

st.info(
    "Describe a feature, user flow, or prototype you want to test. "
    "Claude will simulate each selected persona walking through it."
)

feature_description = st.text_area(
    "Feature / flow description",
    height=150,
    placeholder=(
        "e.g. The user opens the app and wants to send money to a friend by phone number. "
        "They tap 'Send', type the amount, enter the recipient's phone number, "
        "add an optional note, and confirm with biometrics."
    ),
)

persona_options = [f"{p['name']} ({p['age']}, {p['city']}) — {p['archetype']}" for p in PERSONAS]
selected_labels = st.multiselect(
    "Select personas",
    options=persona_options,
    default=persona_options,
)

selected_personas = [
    p for p, label in zip(PERSONAS, persona_options) if label in selected_labels
]

run_summary = st.checkbox("Generate cross-persona summary after interviews", value=True)

if st.button("Run Persona Interviews", type="primary", disabled=not feature_description.strip() or not selected_personas):
    if not feature_description.strip():
        st.error("Please describe the feature or flow.")
        st.stop()

    all_feedback = []
    progress = st.progress(0, text="Starting interviews...")

    for i, persona in enumerate(selected_personas):
        progress.progress(i / len(selected_personas), text=f"Interviewing {persona['name']}...")
        with st.spinner(f"Simulating {persona['name']}..."):
            try:
                response = simulate_persona(persona, feature_description.strip())
            except Exception as e:
                st.error(f"Error simulating {persona['name']}: {e}")
                continue

        all_feedback.append({"name": persona["name"], "response": response})

        with st.expander(f"{persona['name']} — {persona['archetype']}", expanded=(i == 0)):
            st.markdown(response)

    progress.progress(1.0, text="Done!")

    if run_summary and len(all_feedback) > 1:
        st.subheader("Cross-Persona Summary")
        with st.spinner("Generating summary..."):
            try:
                summary = generate_summary(all_feedback)
                st.markdown(summary)
            except Exception as e:
                st.error(f"Summary generation failed: {e}")
