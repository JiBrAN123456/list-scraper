class Match:
    def __init__(self, match_id, date, teams, score, result):
        self.match_id = match_id
        self.date = date
        self.teams = teams
        self.score = score
        self.result = result

class Player:
    def __init__(self, player_id, name, team, role):
        self.player_id = player_id
        self.name = name
        self.team = team
        self.role = role

class Team:
    def __init__(self, team_id, name, players):
        self.team_id = team_id
        self.name = name
        self.players = players

class Tournament:
    def __init__(self, tournament_id, name, matches):
        self.tournament_id = tournament_id
        self.name = name
        self.matches = matches