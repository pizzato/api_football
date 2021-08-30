from datetime import datetime
from api_football import APIFootballExtended
import os
import json

# Secret and config
KEY = "<API_KEY_API_KEY>"
HOST = "api-football-v1.p.rapidapi.com"  # API URLS
LEAGUE = 39  # This is premier league
SEASON = 2021  # 2021 Season

now = datetime.now().strftime("%Y%m%d-%H%M%S")
FOLDER = 'data/{now}/'.format(now=now)


def fetch_and_dump():
    api = APIFootballExtended(key=KEY, host=HOST, league=LEAGUE, season=SEASON)

    file_append_str = '{league}_{season}_{now}'.format(league=LEAGUE, season=SEASON, now=now)
    os.makedirs(FOLDER)

    print("Getting Teams")
    teams_dict = api.get_map_team_name_id()
    with open(FOLDER + 'teams_' + file_append_str + '.json', 'w', encoding='utf-8') as f:
        json.dump(teams_dict, f, ensure_ascii=False, indent=4)

    print("Getting Squads")
    players_df = api.get_league_players()
    players_df.to_csv(FOLDER + 'players_' + file_append_str + '.csv')
    players_df.to_pickle(FOLDER + 'players_' + file_append_str + '.pkl')

    print("Getting Current Round")
    current_round = api.get_current_round()
    with open(FOLDER + 'current_round_' + file_append_str + '.json', 'w', encoding='utf-8') as f:
        json.dump({'current_round':current_round}, f, ensure_ascii=False, indent=4)

    print("Getting Fixtures")
    round_fixtures_df = api.fixtures(season_round=current_round)
    round_fixtures_df.to_csv(FOLDER + 'round_fixtures_' + file_append_str + '.csv')
    round_fixtures_df.to_pickle(FOLDER + 'round_fixtures_' + file_append_str + '.pkl')

    print("Getting Predictions")
    predictions_df = api.get_fixture_predictions(fixtures=round_fixtures_df.fixture_id)
    predictions_df.to_csv(FOLDER + 'predictions_' + file_append_str + '.csv')
    predictions_df.to_pickle(FOLDER + 'predictions_' + file_append_str + '.pkl')

    print("Getting Odds")
    odds_df = api.odds()
    odds_df.to_csv(FOLDER + 'odds_' + file_append_str + '.csv')
    odds_df.to_pickle(FOLDER + 'odds_' + file_append_str + '.pkl')


if __name__ == "__main__":
    fetch_and_dump()
