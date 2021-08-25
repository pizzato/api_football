from api_football.base import APIFootballBase
import pandas as pd

class APIFootballExtended (APIFootballBase):

    def __init__(self, key, host="api-football-v1.p.rapidapi.com"):
        super().__init__(key, host, convert_to_pandas=True)

    def get_map_team_name_id(self, league, season):
        res_df = self.teams(league, season)

        return res_df.set_index('team_name')['team_id'].to_dict()

    def get_league_players(self, league=None, season=None, teams=None):
        assert (league is not None and season is not None) or (teams is not None), "Please use either league and season or teams"
        assert not((league is not None and season is not None) and (teams is not None)), "Please use either league and season or teams"

        if teams is None:
            map_team_name_id = self.get_map_team_name_id(league=league, season=season)
            teams = map_team_name_id.values()

        players_df = pd.concat([self.squads(team=team) for team in teams])
        return players_df

    def get_current_round(self, league, season):
        res = self.round(league=league, season=season, current=True)
        return res.loc[0, "rounds"]

    def get_round_predictions(self, league, season, round):
        round_fixtures = self.fixtures(league=league, season=season, round=round)
        return self.get_fixture_predictions(round_fixtures.fixture_id)

    def get_fixture_predictions(self, fixtures):
        predictions = [self.predictions(fixture=fixture) for fixture in fixtures]
        res = pd.concat(predictions, axis=0).set_index(fixtures)
        return res