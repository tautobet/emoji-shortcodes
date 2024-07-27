import streamlit as st
from horus.config import CODE_HOME

st.page_link("streamlit_app.py", label="LiveScores")
st.page_link(f"{CODE_HOME}/pages/x1.py", label="1xBet")
st.page_link(f"{CODE_HOME}/pages/x8.py", label="8xBet")
open("stop_1x.flag", "w").close()
open("stop_8x.flag", "w").close()
