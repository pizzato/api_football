import requests
import requests_cache
import pandas as pd
import numpy as np
from api_football.helper import flatten

_EP_SQUADS = "v3/players/squads"
_EP_TEAMS = "v3/teams"
_EP_ROUNDS = "v3/fixtures/rounds"
_EP_FIXTURES = "v3/fixtures"
_EP_PREDICTIONS = "v3/predictions"
_EP_ODDS = "v3/odds"


class APIFootballBase:

    def __init__(self, key, host="api-football-v1.p.rapidapi.com", convert_to_pandas=True, league=None, season=None):
        requests_cache.install_cache("APIFootball", backend='sqlite', expire_after=-1,
                                     urls_expire_after={
                                         "*/" + _EP_SQUADS: -1
                                         , "*/" + _EP_TEAMS: -1
                                         , "*/" + _EP_ROUNDS: 86400  # 1 day
                                         , "*/" + _EP_FIXTURES: 86400  # 1 day
                                         , "*/" + _EP_PREDICTIONS: 3600  # 1 hour
                                         , "*/" + _EP_ODDS: 3600  # 1 hour
                                     }
                                     )

        self.host = "https://{host}/".format(host=host)
        self.headers = {
            'x-rapidapi-key': key,
            'x-rapidapi-host': host
        }

        self.convert_to_pandas = convert_to_pandas
        self.league = league
        self.season = season


    def _api_call(self, params, url, just_response=False):
        response = []
        while True:
            json_response = requests.request("GET", url=url, headers=self.headers, params=params).json()

            if not json_response['results']:
                print("Warning: ", json_response['errors'])
                return None

            response += json_response['response']

            pages = json_response.get('paging', {'current': 1, 'total': 1})

            if pages['current'] == pages['total']:
                break
            params.update({'page':pages['current']+1})

        if just_response:
            return response

        result = [flatten(r_) for r_ in response]
        if self.convert_to_pandas:
            result = pd.DataFrame(result)

        return result

    def teams(self, league=None, season=None):
        league = league if league is not None else self.league
        season = season if season is not None else self.season

        params = dict(league=league, season=season)
        url = self.host + _EP_TEAMS
        return self._api_call(params=params, url=url)

    def squads(self, team):
        params = dict(team=team)
        url = self.host + _EP_SQUADS
        response = self._api_call(params=params, url=url, just_response=True)

        if len(response) > 1:
            print("Warning: More than one team for squad id {} using first one".format(team))

        response = response[0]

        team = {"team_" + k: v for k, v in response['team'].items()}
        players = [{**team, **player} for player in response['players']]
        if self.convert_to_pandas:
            players = pd.DataFrame(players)

        return players

    def round(self, league=None, season=None, current="false"):
        league = league if league is not None else self.league
        season = season if season is not None else self.season

        current = "true" if current is True else "false"

        params = dict(league=league, season=season, current=current)
        url = self.host + _EP_ROUNDS
        response = self._api_call(params=params, url=url, just_response=True)

        rounds = response
        if self.convert_to_pandas:
            rounds = pd.DataFrame({'rounds': rounds})
        return rounds

    def fixtures(self, league=None, season=None, season_round=None):
        league = league if league is not None else self.league
        season = season if season is not None else self.season
        params = dict(league=league, season=season)
        if season_round is not None:
            params.update(dict(round = season_round))

        url = self.host + _EP_FIXTURES
        return self._api_call(params=params, url=url)

    def predictions(self, fixture):
        params = dict(fixture=fixture)
        url = self.host + _EP_PREDICTIONS
        return self._api_call(params=params, url=url)

    def odds(self, league=None, season=None, fixture=None, bookmaker=None, bet=None):
        league = league if league is not None else self.league
        season = season if season is not None else self.season
        params = dict(league=league, season=season)

        if fixture is not None:
            params.update(dict(fixture=fixture))
        if bookmaker is not None:
            params.update(dict(bookmaker=bookmaker))
        if bet is not None:
            params.update(dict(bet=bet))

        url = self.host + _EP_ODDS

        response = self._api_call(params=params, url=url, just_response=True)
        if response is None:
            return None

        results = []
        for fixture_odds in response:
            fixture_id = fixture_odds['fixture']['id']

            d_bid_value = {}
            for bookmaker in fixture_odds['bookmakers']:
                for bets in bookmaker['bets']:
                    # bid = bets['id'], bets['name']
                    bid = bets['name']
                    if bid not in d_bid_value:
                        d_bid_value[bid] = {}

                    for ov in bets['values']:
                        value, odd = ov['value'], ov['odd']
                        if value not in d_bid_value[bid]:
                            d_bid_value[bid][value] = []

                        d_bid_value[bid][value] += [1. / float(odd)]

            result = dict(fixture_id=fixture_id)
            result.update({b: {v: np.mean(lo) for v, lo in dv.items()} for b, dv in d_bid_value.items()})
            results.append(result)

        if self.convert_to_pandas:
            results = pd.DataFrame([flatten(r) for r in results])
        return results

