import time
import asyncio
import streamlit as st
import requests
import pandas as pd
import horus.utils as utils
import horus.apis as apis
import numpy as np

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


def check_scores(old_match, new_match):
    team_score = 0
    if old_match['match_id'] == new_match['match_id']:
        if old_match['team1_score'] < new_match['team1_score']:
            team_score = 1
        elif old_match['team1_score'] > new_match['team1_score']:
            team_score = -1
        elif old_match['team2_score'] < new_match['team2_score']:
            team_score = 2
        elif old_match['team2_score'] > new_match['team2_score']:
            team_score = -2
    return team_score


async def check_rules(start_prediction, current_prediction, score_team1, score_team2, half, time_sec):
    # Check risk for betting under
    total_score = score_team1 + score_team2
    diff_score = abs(score_team1 - score_team2)
    if half == 1:
        # TODO:
        #  #1 Add win-lose prediction into total scores prediction
        #  #2 Check red cards into prediction
        #  #3 total scores prediction in 2nd half go to reduced more than 50% from start prediction
        #     Bet over total scores
        # start_prediction < 3: The match is predicted low scores
        if 0 < start_prediction <= 3 or (start_prediction == 0 and total_score*2 < current_prediction):
            # The situation seems going exact start prediction until close to the end of half
            if total_score < start_prediction:
                # The score happens after 36th minute
                if time_sec >= BetTime.MIN36.value:
                    return RISKS.LOW
                # The score happens from 33rd to 36th minute
                # TODO: Add indicators to check
                #   If low scores, skip check odds increased continuously and win team prediction after the score
                elif BetTime.MIN34.value <= time_sec <= BetTime.MIN36.value:
                    return RISKS.MEDIUM
            # The situation seems going wrong start prediction until close to the end of half
            elif total_score >= start_prediction:
                # The score happens after 37th minute
                if time_sec >= BetTime.MIN37.value:
                    return RISKS.MEDIUM
                else:
                    return RISKS.HIGH
        # start_prediction == 3: The match is predicted medium scores
        elif start_prediction == 3.5:
            # The situation seems going exact start prediction until close to the end of half
            if total_score <= 3:
                # The score happens after 37th minute
                if time_sec > BetTime.MIN37.value:
                    return RISKS.LOW
                # The score happens from 34th to 36th minute
                elif BetTime.MIN35.value <= time_sec <= BetTime.MIN37.value:
                    return RISKS.MEDIUM
            elif total_score == 4:
                # The score happens after 39th minute
                if time_sec > BetTime.MIN39.value:
                    return RISKS.MEDIUM
                # The score happens from 36th to 39th minute
                elif BetTime.MIN36.value <= time_sec <= BetTime.MIN39.value:
                    return RISKS.HIGH
            return RISKS.HIGHEST
        return RISKS.HIGHEST
    elif half == 2:
        # start_prediction < 3: The match is predicted low scores
        if total_score <= 4:
            if 0 < start_prediction <= 3.5:
                if diff_score == 1:
                    # The score happens after 86th minute
                    if time_sec > BetTime.MIN85.value:
                        return RISKS.LOW
                    elif BetTime.MIN84.value <= time_sec <= BetTime.MIN85.value:
                        return RISKS.MEDIUM
                    else:
                        return RISKS.HIGH
                elif diff_score == 2:
                    # The score happens after 84th minute
                    if time_sec > BetTime.MIN84.value:
                        return RISKS.LOW
                    # The score happens from 82nd to 84th minute
                    elif BetTime.MIN83.value <= time_sec <= BetTime.MIN84.value:
                        return RISKS.MEDIUM
                    else:
                        return RISKS.HIGH
                elif diff_score == 3:
                    # The score happens after 86th minute
                    if time_sec > BetTime.MIN86.value:
                        return RISKS.LOW
                    elif BetTime.MIN84.value <= time_sec <= BetTime.MIN86.value:
                        return RISKS.MEDIUM
                    else:
                        return RISKS.HIGH
                elif diff_score == 0:
                    # The score happens after 86th minute
                    if time_sec > BetTime.MIN88.value:
                        return RISKS.LOW
                    elif BetTime.MIN86.value <= time_sec <= BetTime.MIN88.value:
                        return RISKS.MEDIUM
                    else:
                        return RISKS.HIGH
                else:
                    return RISKS.HIGHEST
            return RISKS.HIGHEST
        return RISKS.HIGHEST
    else:
        return RISKS.HIGHEST


async def compare_matches(matches, new_matches):

    # TODO: New logic - loop new matches to check current scores with existing matches
    """
    If found any existing match, pop() it out after check score
    New matches will be included new scores, and time that are stored into matches json
    pop() a match from list matches['matches'].pop(matches['matches'].index(m))
    """
    bet_coros = []
    tele_coros = []
    # Loop through each element of 'matches' list
    for match in matches:
        # Loop through each element of 'new_matches' list
        for new_match in new_matches:
            # Check if the 'match_id' keys in both dictionaries have the same value
            if match['match_id'] == new_match['match_id']:
                # Update prediction to new match
                new_match['prediction'] = match['prediction']
                new_match['scores'] = []
                if 'scores' in match:
                    new_match['scores'] = match['scores']
                # Check if is there any score happened
                team_score = check_scores(match, new_match)
                if team_score != 0:
                    # TODO
                    #  1. Create telegram msg here with type to send it to telebot accordingly
                    #  2. If meet matrix rules -> bet
                    match_id        = new_match.get('match_id')
                    league          = new_match.get('league')
                    prediction      = new_match.get('prediction')
                    cur_prediction  = new_match.get('cur_prediction')
                    team1           = new_match.get('team1')
                    team2           = new_match.get('team2')
                    team1_score     = new_match.get('team1_score')
                    team2_score     = new_match.get('team2_score')
                    half            = new_match.get('half')
                    time_second     = new_match.get('time_second')
                    time_match      = new_match.get('time_match')
                    penalties       = new_match.get('penalties')
                    team1_redcard   = new_match.get('team1_redcard')
                    team2_redcard   = new_match.get('team2_redcard')
                    url             = new_match.get('url')
                    scores          = new_match.get('scores')

                    matched_rule = await check_rules(prediction, cur_prediction, team1_score,
                                                     team2_score, half, time_second)

                    # store time of the last score
                    scores.insert(0, time_match)
                    new_match['scores'] = scores

                break
        # If the inner loop completes without the 'break' statement, remove the current 'match' from 'matches' list
        else:
            matches.remove(match)
    # TODO: Start bet with asyncio here, refer /async_sample.py
    await asyncio.gather(*bet_coros, *tele_coros)
    if len(new_matches) > 0:
        utils.write_json(new_matches)
    return new_matches


# Begin streamlit UI
def page_load():
    st.set_page_config(
        page_title="Livescore App",
        page_icon=":soccer:",
        layout="wide",
        initial_sidebar_state="expanded"
    )
# End


import subprocess
from horus.config import CODE_HOME

# Replace 'script.sh' with the name of your Bash script file
subprocess.run(['bash', f"{CODE_HOME}/devops/test.sh"])



page_load()
with st.empty():
    @repeat(every(10).seconds)
    def load_details():
        url = f"{JSON_SERVER}/8x/"
        response = requests.request("GET", url, headers={}, data={})

        # print(response.text)
        data = response.json()

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
                "scores": st.column_config.Column(
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

    while 1:
        run_pending()
        time.sleep(1)