import time
import os
import streamlit as st8
import requests
import pandas as pd8
from horus.utils import pagination

from horus.enums import RISKS, BetTime
from horus.config import logger, TEMP_FOLDER, X8_BASE_URL, JSON_SERVER
import schedule as schedule8


def fetch_emojis():
    resp = requests.get(
        'https://raw.githubusercontent.com/omnidan/node-emoji/master/lib/emoji.json')
    json = resp.json()
    codes, emojis = zip(*json.items())
    return pd8.DataFrame({
        'Emojis': emojis,
        'Shortcodes': [f':{code}:' for code in codes],
    })


# Begin streamlit UI
def page_load():
    st8.set_page_config(
        page_title="Livescore App",
        page_icon=":soccer:",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st8.header("8XBET", divider="rainbow")
# End


# Create the flag file to stop the schedule in x1.py
open("stop_1x.flag", "w").close()
# Remove the flag file to start the schedule in x8.py
if os.path.exists("stop_8x.flag"):
    os.remove("stop_8x.flag")

page_load()
with st8.empty():
    def load_data():
        try:
            url = f"{JSON_SERVER}/8x/"
            response = requests.request("GET", url, headers={}, data={})

            if response.status_code == 200:
                # print(response.text)
                data8 = response.json() or []

                total_data = len(data8)
                count_data = 0
                while total_data > count_data:
                    page = 1  # Page number
                    limit = 30  # Number of items per page
                    paginated_data = pagination(data8, page, limit)
                    count_data += len(paginated_data)

                    if paginated_data:
                        df8 = pd8.DataFrame(
                            data=paginated_data,
                            columns=(
                                "league",
                                "team1",
                                "team2",
                                "score",
                                "time_match",
                                "add_time",
                                "half",
                                "prediction",
                                "h2_prediction",
                                "cur_prediction",
                                "scores",
                                "url")
                        ).sort_values(by='time_match', ascending=False)
                        st8.dataframe(
                            df8,
                            height=(total_data + 1) * 35 + 3,
                            column_config={
                                "league": st8.column_config.Column(
                                    label="League",
                                    width="medium"
                                ),
                                "team1": st8.column_config.Column(
                                    label="T1",
                                    width="small"
                                ),
                                "team2": st8.column_config.Column(
                                    label="T2",
                                    width="small"
                                ),
                                "score": st8.column_config.TextColumn(
                                    label="Score",
                                    width="small"
                                ),
                                "time_match": st8.column_config.Column(
                                    label="Time",
                                    width="small"
                                ),
                                "add_time": st8.column_config.Column(
                                    label="ET",
                                    width="small"
                                ),
                                "half": st8.column_config.Column(
                                    label="Half",
                                    width="small"
                                ),
                                "prediction": st8.column_config.NumberColumn(
                                    label="Pre",
                                    format="%.1f".center(30),
                                    width="small"
                                ),
                                "h2_prediction": st8.column_config.NumberColumn(
                                    label="H2-Pre",
                                    format="%.1f".center(30),
                                    width="small"
                                ),
                                "cur_prediction": st8.column_config.NumberColumn(
                                    label="Cur-Pre",
                                    format="%.1f".center(30),
                                    width="small"
                                ),
                                "scores": st8.column_config.TextColumn(
                                    label="Scores",
                                    width="medium"
                                ),
                                "url": st8.column_config.LinkColumn(
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

    schedule8.every(30).seconds.do(load_data)
    load_data()

    while not os.path.exists("stop_8x.flag"):
        schedule8.run_pending()
        time.sleep(1)

    schedule8.clear()
