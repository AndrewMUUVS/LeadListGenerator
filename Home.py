import streamlit as st

st.title("Home")

"Hey there!"
"You can use the following three applications to make your life easier when handling lead lists from Phantombuster, Zoominfo, and Cognism."

"#### List Merger"
"Here, you can upload three CSV files obtained from Phantombuster, Zoominfo, or Cognism. The program will generate a merged file combining all the information from the three tables."

"#### AI Email Generator"
"Upload the merged list you created earlier here. The program will generate a personalized message for each lead in the MESSAGE column using OpenAI. OpenAI will extract the two most relevant skills from the lead's skillset and include them in the message. In case OpenAI is unavailable, an Email Generator application is provided as an alternative."

"#### Email Generator"
"Upload the merged list you created earlier here. The program will generate a personalized message for each lead in the MESSAGE column."