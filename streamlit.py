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

# Add file upload section
st.write("")
st.subheader("Upload a File")

uploaded_file = st.file_uploader("Choose a file", type=['txt', 'csv', 'xlsx', 'pdf', 'png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    # Display file details
    st.success(f"File '{uploaded_file.name}' uploaded successfully!")
    
    # Show file information
    file_details = {
        "Filename": uploaded_file.name,
        "File size": f"{uploaded_file.size} bytes",
        "File type": uploaded_file.type
    }
    
    st.write("**File Details:**")
    for key, value in file_details.items():
        st.write(f"- {key}: {value}")

# Add some information about the app
st.write("")
st.info("Click the button above to see the welcome message, or upload a file to see its details!")
