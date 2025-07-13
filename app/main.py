# Streamlit app and main entry point 
import streamlit as st
from ai_layer import AILayer  # If you use AI features
from api_layer import LegoAPI

# Initialize API
lego_api = LegoAPI()

st.title("LEGO AI Assistant")

# Search input
query = st.text_input("Search for a LEGO set:")

if query:
    # Fast search (basic info, no price)
    results = lego_api.search_sets(query)
    if results:
        # Show results as a selectable list
        set_names = [f"{s.set_id}: {s.name} ({s.theme})" for s in results]
        selected = st.selectbox("Select a set to view details:", set_names)
        selected_set = results[set_names.index(selected)]

        # Use expander for details
        with st.expander("Show full details and price"):
            if st.button("Fetch details for selected set"):
                with st.spinner("Fetching full details..."):
                    try:
                        full_set = lego_api.fetch_set(selected_set.set_id)
                        st.subheader(full_set.name)
                        st.write(f"**Theme:** {full_set.theme}")
                        st.write(f"**Pieces:** {full_set.piece_count}")
                        st.write(f"**Year:** {full_set.release_year}")
                        st.write(f"**Description:** {full_set.description}")
                        st.write(f"**Price:** {full_set.price if full_set.price else 'N/A'}")
                        # If you have image URLs, you can display them here
                        # st.image(full_set.image_url)
                    except Exception as e:
                        st.error(f"Error fetching set details: {e}")
    else:
        st.info("No sets found for your search.")
else:
    st.info("Enter a search term to find LEGO sets.")