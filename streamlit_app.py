import os
import time
import streamlit as st
import requests
import pandas as pd
import horus.utils as utils

from schedule import every, repeat, run_pending

CODE_HOME           = os.path.abspath(os.path.dirname(__file__))

with st.empty():

    @repeat(every(15).seconds)
    def strike_details():
        # live_matches = Utils.sort_json(Utils.get_live_matches_1xbet(), "time_match")
        live_matches = utils.sort_json(
            utils.read_json_w_file_path(f'{CODE_HOME}/matches.json'),
            "time_match"
        )
        df = pd.DataFrame(
            data=live_matches,
            columns=("league", "team1", "team2", "team1_score", "team2_score", "time_match", "half", "scores")
        )
        st.table(df)

    while 1:
        run_pending()
        time.sleep(1)



'''
# Streamlit emoji shortcodes

Below are all the emoji shortcodes supported by Streamlit.

Shortcodes are a way to enter emojis using pure ASCII. So you can type this `:smile:` to show this
:smile:.

(Keep in mind you can also enter emojis directly as Unicode in your Python strings too — you don't
*have to* use a shortcode)
'''

# emojis = fetch_emojis()
#
# st.table(emojis)

