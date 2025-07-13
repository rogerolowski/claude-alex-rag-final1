# Streamlit app and main entry point 
import streamlit as st
from ai_layer import AILayer

st.title("LEGO AI Assistant")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize AI layer
ai = AILayer()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if query := st.chat_input("Ask about LEGO sets..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # Process query
    with st.chat_message("assistant"):
        result = ai.process_query(query)
        # Display AI response
        st.markdown(result.ai_response)
        # Display set details
        for lego_set in result.sets:
            st.write(f"**{lego_set.name}** ({lego_set.set_id})")
            st.write(f"Theme: {lego_set.theme}, Pieces: {lego_set.piece_count}, Price: ${lego_set.price or 'N/A'}")
        st.session_state.messages.append({"role": "assistant", "content": result.ai_response})