import time
import asyncio
import streamlit as st
import requests
import pandas as pd
import horus.utils as utils

from horus.enums import RISKS, BetTime
from horus.config import logger, TEMP_FOLDER, X8_BASE_URL, JSON_SERVER
from schedule import every, repeat, run_pending


def fetch_emojis():
    resp = requests.get(
        'https://raw.githubusercontent.com/omnidan/node-emoji/master/lib/emoji.json')
    json = resp.json()
    codes, emojis = zip(*json.items())
    return pd.DataFrame({
        'Emojis': emojis,
        'Shortcodes': [f':{code}:' for code in codes],
    })


# Begin streamlit UI
def page_load():
    st.set_page_config(
        page_title="Livescore App",
        page_icon=":soccer:",
        layout="wide",
        initial_sidebar_state="expanded"
    )
# End


page_load()
with st.empty():
    @repeat(every(15).seconds)
    def load_details():
        try:
            url = f"{JSON_SERVER}/1x/"
            response = requests.request("GET", url, headers={}, data={})

            if response.status_code == 200:
                # print(response.text)
                data = response.json()

                if data:
                    df = pd.DataFrame(
                        data=data,
                        columns=(
                            "league",
                            "team1",
                            "team2",
                            "score",
                            "time_match",
                            "add_time",
                            "half",
                            "prediction",
                            "cur_prediction",
                            "scores",
                            "url")
                    ).sort_values(by='time_match', ascending=False)
                    st.dataframe(
                        df,
                        height=(len(data) + 1) * 35 + 3,
                        column_config={
                            "league": st.column_config.Column(
                                label="League",
                                width="medium"
                            ),
                            "team1": st.column_config.Column(
                                label="T1",
                                width="small"
                            ),
                            "team2": st.column_config.Column(
                                label="T2",
                                width="small"
                            ),
                            "score": st.column_config.TextColumn(
                                label="Score",
                                width="small"
                            ),
                            "time_match": st.column_config.Column(
                                label="Time",
                                width="small"
                            ),
                            "add_time": st.column_config.Column(
                                label="ET",
                                width="small"
                            ),
                            "half": st.column_config.Column(
                                label="Half",
                                width="small"
                            ),
                            "prediction": st.column_config.NumberColumn(
                                label="Pre",
                                format="%.1f".center(30),
                                width="small"
                            ),
                            "cur_prediction": st.column_config.NumberColumn(
                                label="Cur-Pre",
                                format="%.1f".center(30),
                                width="small"
                            ),
                            "url": st.column_config.LinkColumn(
                                label="Link",
                                display_text=f"Link",
                                width="small"
                            ),

                        }
                    )
        except requests.exceptions.RequestException as e:
            logger.error(f'RequestException: {e}')
        except ConnectionResetError:
            logger.error('ConnectionResetError')
        return None
    while 1:
        run_pending()
        time.sleep(1)
