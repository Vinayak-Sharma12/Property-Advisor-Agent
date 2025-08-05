import streamlit as st  
from main import workflow
# Title of the app
st.title("Property Agent")

# Input field
user_input = st.text_input("Enter your query:")

# Button to trigger processing
if st.button("Submit"):
    # Simple logic or response
    result=workflow(user_input)
    if result is None or result.empty:
        st.write("Alright! Tell me Your Requirements")
    else:
         st.write(result)


    
    st.success("Processed successfully!")
