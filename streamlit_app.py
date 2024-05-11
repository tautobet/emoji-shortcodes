import streamlit as st
import requests
import pandas as pd
import time
import horus.utils as utils

from schedule import every, repeat, run_pending

@st.cache(ttl=60*60*12, allow_output_mutation=True)
def fetch_emojis():
    resp = requests.get(
        'https://raw.githubusercontent.com/omnidan/node-emoji/master/lib/emoji.json')
    json = resp.json()
    codes, emojis = zip(*json.items())
    return pd.DataFrame({
        'Emojis': emojis,
        'Shortcodes': [f':{code}:' for code in codes],
    })


@repeat(every(15).seconds)
def strike_details():
    # live_matches = Utils.sort_json(Utils.get_live_matches_1xbet(), "time_match")
    live_matches = utils.sort_json(
        utils.read_json_w_file_path(f'/Users/trieutruong/repo/autobet/src/report/matches.json'),
        "time_match"
    )
    df = pd.DataFrame(
        data=live_matches,
        columns=("league", "team1", "team2", "team1_score", "team2_score", "time_match", "half", "scores")
    )
    st.table(df)


if __name__ == "__main__":

    # schedule.every(10).seconds.do(strike_details)

    strike_details()
    # schedule with params
    # schedule.every(10).minutes.do(lambda: job('Hello ', 'world!'))

    # # schedule.every(30).seconds.do(job)
    # # schedule.every(10).minutes.do(job)
    # # schedule.every().hour.do(job)
    # # schedule.every().day.at("10:30").do(job)

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

