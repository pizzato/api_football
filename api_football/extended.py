from api_football.base import APIFootballBase
import pandas as pd

class APIFootballExtended (APIFootballBase):

    def __init__(self, key, host="api-football-v1.p.rapidapi.com", league=None, season=None):
        super().__init__(key, host, convert_to_pandas=True, league=league, season=season)

    def get_map_team_name_id(self, league=None, season=None):
        league = league if league is not None else self.league
        season = season if season is not None else self.season

        res_df = self.teams(league, season)

        return res_df.set_index('team_name')['team_id'].to_dict()

    def get_league_players(self, league=None, season=None, teams=None):
        league = league if league is not None else self.league
        season = season if season is not None else self.season

        assert (league is not None and season is not None) or (teams is not None), "Please use either league and season or teams"
        assert not((league is not None and season is not None) and (teams is not None)), "Please use either league and season or teams"

        if teams is None:
            map_team_name_id = self.get_map_team_name_id(league=league, season=season)
            teams = map_team_name_id.values()

        players_df = pd.concat([self.squads(team=team) for team in teams])
        return players_df

    def get_current_round(self, league=None, season=None):
        league = league if league is not None else self.league
        season = season if season is not None else self.season

        res = self.round(league=league, season=season, current=True)
        return res.loc[0, "rounds"]

    def get_next_n_rounds(self, league=None, season=None, n=2, include_current=True):
        league = league if league is not None else self.league
        season = season if season is not None else self.season

        rounds = self.round(league=league, season=season).rounds.to_list()
        current_round = self.get_current_round(league=league, season=season)

        icr_ = rounds.index(current_round)
        if not include_current:
            icr_ += 1

        if icr_ < len(rounds): # checking it's not the last week
            return rounds[icr_ : icr_ + n]
        else:
            return []

    def get_predictions_for_rounds(self, season_rounds, league=None, season=None):
        league = league if league is not None else self.league
        season = season if season is not None else self.season

        predictions = [self.get_predictions(league=league, season=season, season_round=season_round)
            for season_round in season_rounds
        ]
        res = pd.concat(predictions, axis=0)
        return res

    def get_predictions(self, league=None, season=None, season_round=None):
        """ WARNING: This will create 381 calls for the API if using season_round as None.
            The free quota is 100 calls per day!
        :param league:
        :param season:
        :param season_round:
        :return:
        """
        league = league if league is not None else self.league
        season = season if season is not None else self.season

        fixtures = self.fixtures(league=league, season=season, season_round=season_round)
        return self.get_fixture_predictions(fixtures.fixture_id)

    def get_fixture_predictions(self, fixtures):
        predictions = [self.predictions(fixture=fixture) for fixture in fixtures]
        res = pd.concat(predictions, axis=0).set_index(fixtures)
        return res

