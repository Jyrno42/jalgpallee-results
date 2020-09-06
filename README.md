# Jalgpall.ee game result parser

A small script to fetch games from jalgpall.ee and parse them to a structured format.

Usage:

```python
from jalgpall import get_game_info

get_game_info(89842)

GameInfo(
    home_team=Team(
        name="RL. JK Metsis",
        team_id="4762",
        lineup=[
            # Player(number=1, name="John Smith", is_keeper=True, is_captain=False),
            # more players...,
        ],
        substitutes=[],
    ),
    away_team=Team(
        name="RL. Error United",
        team_id="4273",
        lineup=[
            # Player(number=1, name="John Smith", is_keeper=True, is_captain=False),
            # more players...,
        ],
        substitutes=[],
    ),
    official=True,
    home_score=2,
    away_score=0,
    home_halftime_score=1,
    away_halftime_score=0,
    location="Männiku kunstmuruväljak",
    attendance=15,
    events=[
        Event(
            time=7,
            overtime_offset=None,
            event_type="goal",
            team="home",
            player_nr=27,
            event_data=GoalEventData(penalty=False),
        ),
        Event(
            time=18,
            overtime_offset=None,
            event_type="card",
            team="home",
            player_nr=28,
            event_data=CardEventData(
                is_yellow=True,
                is_red=False,
                reason="Ebasportlik käitumine - lubava rünnaku peatamine",
            ),
        ),
        Event(
            time=34,
            overtime_offset=None,
            event_type="card",
            team="home",
            player_nr=31,
            event_data=CardEventData(
                is_yellow=True,
                is_red=False,
                reason="Ebasportlik käitumine - ilmse väravavõimaluse ärahoidmine üritusega palli mängida",
            ),
        ),
        Event(
            time=70,
            overtime_offset=None,
            event_type="goal",
            team="home",
            player_nr=34,
            event_data=GoalEventData(penalty=False),
        ),
        Event(
            time=70,
            overtime_offset=1,
            event_type="card",
            team="away",
            player_nr=11,
            event_data=CardEventData(
                is_yellow=True,
                is_red=False,
                reason="Ebasportlik käitumine - lubava rünnaku peatamine",
            ),
        ),
        Event(
            time=70,
            overtime_offset=1,
            event_type="card",
            team="home",
            player_nr=27,
            event_data=CardEventData(
                is_yellow=True,
                is_red=False,
                reason="Rahulolematuse näitamine sõnas või teos",
            ),
        ),
    ],
)
```

