import streamlit as st


st.title("suryaleads marketing ")

Name = st.text_input(" your name")

if st.button("sumit"):
   if Name:
      st.success(f" Hi {Name}, welcome to suryaleads marketing")
   else:
      st.warning("please enter your name for your business future")
      