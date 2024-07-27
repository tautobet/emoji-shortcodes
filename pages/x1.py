import time
import os
import streamlit as st
import requests
import pandas as pd
from horus.utils import pagination
from horus.config import logger, JSON_SERVER
import schedule as schedule1


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
    st.header("1XBET", divider="rainbow")
# End


# Create the flag file to stop the schedule in x8.py
open("stop_8x.flag", "w").close()
# Remove the flag file to start the schedule in x1.py
if os.path.exists("stop_1x.flag"):
    os.remove("stop_1x.flag")


page_load()
with st.empty():
    def load_data():
        try:
            url = f"{JSON_SERVER}/1x/"
            response = requests.request("GET", url, headers={}, data={})

            if response.status_code == 200:
                # print(response.text)
                data = response.json()

                total_data = len(data)
                count_data = 0
                while total_data > count_data:
                    page = 1  # Page number
                    limit = 30  # Number of items per page
                    paginated_data = pagination(data, page, limit)
                    count_data += len(paginated_data)

                    if paginated_data:
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
                                "h2_prediction",
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
                                "h2_prediction": st.column_config.NumberColumn(
                                    label="H2-Pre",
                                    format="%.1f".center(30),
                                    width="small"
                                ),
                                "cur_prediction": st.column_config.NumberColumn(
                                    label="Cur-Pre",
                                    format="%.1f".center(30),
                                    width="small"
                                ),
                                "scores": st.column_config.TextColumn(
                                    label="Scores",
                                    width="medium"
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

    schedule1.every(30).seconds.do(load_data)
    load_data()

    while not os.path.exists("stop_1x.flag"):
        schedule1.run_pending()
        time.sleep(1)

    schedule1.clear()
