import time
import asyncio
import streamlit as st
import requests
import pandas as pd
from horus.utils import get_live_matches_1xbet, get_live_match_1xbet, read_json_w_file_path, compare_matches, \
                        convert_timematch_to_seconds, sort_json

from horus.config import logger, TEMP_FOLDER, CODE_HOME
from schedule import every, repeat, run_pending
import subprocess

subprocess.run(['bash', f"{CODE_HOME}/devops/deploy.sh"])


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
    def find_max_value(arr):
        max_value = convert_timematch_to_seconds(arr[0])  # Initialize max_value with the first element of the array
        for val in arr:
            if convert_timematch_to_seconds(val) > max_value:
                max_value = convert_timematch_to_seconds(val)
        return max_value

    def color_red_column(col):
        return ['background-color: lightgreen' if len(x) > 0 else None for x in col]

    def make_clickable_both(val):
        return f'<a target="_blank" href="{val}">Link</a>'

    @repeat(every(7).seconds)
    def load_details():
        # live_matches = Utils.sort_json(Utils.get_live_matches_1xbet(), "time_match")

        live_matches = sort_json(
            read_json_w_file_path(f'{TEMP_FOLDER}/matches.json'),
            "time_match"
        )
        df = pd.DataFrame(
            data=live_matches,
            columns=(
                "league",
                "team1",
                "team2",
                "team1_score",
                "team2_score",
                "time_match",
                "add_time",
                "half",
                "prediction",
                "cur_prediction",
                "scores",
                "url")
        )


        # df['scores'] = df.apply(color_red_column, subset=['scores'])
        # df_styled = df.style.apply(color_red_column, subset=['scores'])
        # df_styled = df.style.map(lambda x: f"background-color: {'green' if len(x) > 0 else 'red'}", subset='scores')
        # df.style.format({'url': make_clickable_both})


        # def highlight_market(cell):
        #     return 'background-color: lightgreen;'
        #
        # df['prediction'] = df['prediction'].apply(highlight_market)
        # st.markdown(df.to_html(escape=False), unsafe_allow_html=True)

        # def highlighter(x):
        #     # initialize default colors
        #     color_codes = pd.DataFrame('', index=x.index, columns=x.columns)
        #     # set Check color to red if consumption exceeds threshold green otherwise
        #     color_codes['scores'] = np.where(len(x['scores']) > 0, 'color:red', 'color:green')
        #     return color_codes
        #
        # # apply highlighter to df
        # df_style = df.style.apply(highlighter, axis=None)

        st.dataframe(
            df,
            height=(len(live_matches) + 1) * 35 + 3,
            column_config={
                "league": st.column_config.Column(
                    width="medium"
                ),
                "team1": st.column_config.Column(
                    width="small"
                ),
                "team2": st.column_config.Column(
                    width="small"
                ),
                "team1_score": st.column_config.Column(
                    width="small"
                ),
                "team2_score": st.column_config.Column(
                    width="small"
                ),
                "time_match": st.column_config.Column(
                    width="small"
                ),
                "add_time": st.column_config.Column(
                    width="small"
                ),
                "half": st.column_config.Column(
                    width="small"
                ),
                "prediction": st.column_config.NumberColumn(
                    format="%.1f",
                    width="small"
                ),
                "cur_prediction": st.column_config.NumberColumn(
                    format="%.1f",
                    width="small"
                ),
                "scores": st.column_config.Column(
                    width="medium"
                ),
                "url": st.column_config.LinkColumn(
                    label="Match Link",
                    display_text=f"Link",
                    width="small"
                ),

            }
        )

    # async def delete_matches(matches):
    #     logger.info('run deleting ended matches')
    #     for match in matches:
    #         res_ = get_live_match_1xbet(match.get('match_id'))
    #         if not res_ or not res_.get('Success'):
    #             matches.remove(match)
    #
    # @repeat(every(15).seconds)
    # def fetch_matches_data():
    #     last_matches = read_json_w_file_path(f'{TEMP_FOLDER}/matches.json')
    #     live_matches = get_live_matches_1xbet()
    #     if live_matches:
    #         logger.info(f'Popular live matches: {len(live_matches)}')
    #         asyncio.run(compare_matches(last_matches, live_matches))
    #
    # @repeat(every(5).minutes)
    # def delete_ended_matches():
    #     last_matches = read_json_w_file_path(f'{TEMP_FOLDER}/matches.json')
    #     asyncio.run(delete_matches(last_matches))

    while 1:
        run_pending()
        time.sleep(1)
