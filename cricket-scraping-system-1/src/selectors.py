class Selectors:
    MATCH_LIST = "div.match-list"  # Selector for the list of matches
    MATCH_ITEM = "div.match-item"    # Selector for individual match items
    TEAM_A = "span.team-a"           # Selector for Team A name
    TEAM_B = "span.team-b"           # Selector for Team B name
    SCORE = "span.score"             # Selector for match score
    DATE = "span.date"               # Selector for match date
    TIME = "span.time"               # Selector for match time
    MATCH_LINK = "a.match-link"      # Selector for match detail link

    @staticmethod
    def get_match_list_selector():
        return Selectors.MATCH_LIST

    @staticmethod
    def get_match_item_selector():
        return Selectors.MATCH_ITEM

    @staticmethod
    def get_team_a_selector():
        return Selectors.TEAM_A

    @staticmethod
    def get_team_b_selector():
        return Selectors.TEAM_B

    @staticmethod
    def get_score_selector():
        return Selectors.SCORE

    @staticmethod
    def get_date_selector():
        return Selectors.DATE

    @staticmethod
    def get_time_selector():
        return Selectors.TIME

    @staticmethod
    def get_match_link_selector():
        return Selectors.MATCH_LINK