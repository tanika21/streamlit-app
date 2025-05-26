import streamlit as st

# Set page title and configuration
st.set_page_config(
    page_title="Welcome App",
    page_icon="👋",
    layout="centered"
)

# Main title
st.title("Simple Streamlit Welcome App")

# Add some spacing
st.write("")

# Create the button
if st.button("Click Me!", type="primary"):
    # Display the welcome message when button is clicked
    st.success("Welcome to Streamlit! 🎉")
    st.balloons()  # Add a fun animation effect
    
if st.button("Hello", type="primary"):
    # Display the welcome message when button is clicked
    st.success("My name is Samantha! 🎉")
    st.balloons()  # Add a fun animation effect

# Add some information about the app
st.write("")
st.info("Click the button above to see the welcome message!")
