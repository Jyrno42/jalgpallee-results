import datetime
import os

import pytest
import pytz
import responses

from jalgpall import get_game_info, GoalEventData, CardEventData, Player

expected_events = [
    {
        "event_data": GoalEventData(penalty=False),
        "event_type": "goal",
        "overtime_offset": None,
        "player_nr": 27,
        "team": "home",
        "time": 7,
    },
    {
        "event_data": CardEventData(
            is_yellow=True,
            is_red=False,
            reason="Ebasportlik käitumine - lubava rünnaku peatamine",
        ),
        "event_type": "card",
        "overtime_offset": None,
        "player_nr": 28,
        "team": "home",
        "time": 18,
    },
    {
        "event_data": CardEventData(
            is_yellow=True,
            is_red=False,
            reason="Ebasportlik käitumine - ilmse väravavõimaluse ärahoidmine üritusega palli mängida",
        ),
        "event_type": "card",
        "overtime_offset": None,
        "player_nr": 31,
        "team": "home",
        "time": 34,
    },
    {
        "event_data": GoalEventData(penalty=False),
        "event_type": "goal",
        "overtime_offset": None,
        "player_nr": 34,
        "team": "home",
        "time": 70,
    },
    {
        "event_data": CardEventData(
            is_yellow=True,
            is_red=False,
            reason="Ebasportlik käitumine - lubava rünnaku peatamine",
        ),
        "event_type": "card",
        "overtime_offset": 1,
        "player_nr": 11,
        "team": "away",
        "time": 70,
    },
    {
        "event_data": CardEventData(
            is_yellow=True,
            is_red=False,
            reason="Rahulolematuse näitamine sõnas või teos",
        ),
        "event_type": "card",
        "overtime_offset": 1,
        "player_nr": 27,
        "team": "home",
        "time": 70,
    },
]


@pytest.fixture
def basic_xml():
    base_path = os.path.dirname(__file__)

    with open(os.path.join(base_path, "fixtures", "basic.html")) as h:
        return h.read()


@pytest.fixture
def basic_response(basic_xml):
    responses.add(
        method=responses.GET,
        url="http://jalgpall.ee/voistlused/protocol/12345",
        status=200,
        body=basic_xml,
    )


@responses.activate
def test_fetch_basic(basic_response):
    info = get_game_info(12345)

    assert info.official is True
    assert info.home_score == 2
    assert info.away_score == 0
    assert info.home_halftime_score == 1
    assert info.away_halftime_score == 0
    assert info.location == "Venue name"
    assert info.attendance == 29

    assert info.kick_off == datetime.datetime(
        2020, 7, 10, 20, 30, tzinfo=pytz.timezone("Europe/Tallinn")
    )

    assert info.home_team.name == "RL. Home team"
    assert info.home_team.team_id == "5678"

    assert info.away_team.name == "RL. Away team"
    assert info.away_team.team_id == "1234"

    assert info.referee == "Prashant Leopold"


@responses.activate
def test_fetch_basic_events(basic_response):
    info = get_game_info(12345)

    assert [x._asdict() for x in info.events] == expected_events


def test_fetch_basic_real_api():
    info = get_game_info(89842)

    assert info.official is True
    assert info.home_score == 2
    assert info.away_score == 0
    assert info.home_halftime_score == 1
    assert info.away_halftime_score == 0
    assert info.location == "Männiku kunstmuruväljak"
    assert info.attendance == 15

    assert [x._asdict() for x in info.events] == expected_events

    assert info.home_team.name == "RL. JK Metsis"
    assert info.away_team.name == "RL. Error United"


@responses.activate
def test_fetch_basic_players(basic_response):
    info = get_game_info(12345)

    assert info.home_team.lineup == [
        Player(32, "Chi Shulammite", is_keeper=True, is_captain=False),
        Player(3, "Demetrios Willoughby", is_keeper=False, is_captain=False),
        Player(6, "Gwenaël Saoul", is_keeper=False, is_captain=False),
        Player(8, "Pankaj Kris", is_keeper=False, is_captain=False),
        Player(13, "Ramsay Erebos", is_keeper=False, is_captain=False),
        Player(19, "Zhivko Sebastian", is_keeper=False, is_captain=False),
        Player(21, "Notah Hans", is_keeper=False, is_captain=False),
        Player(22, "Heimir Blagoje", is_keeper=False, is_captain=False),
        Player(24, "Dax Octavian", is_keeper=False, is_captain=False),
        Player(25, "Voldemārs Rok", is_keeper=False, is_captain=False),
        Player(27, "Bagrat Garth", is_keeper=False, is_captain=False),
        Player(28, "Hariwald Rafaël", is_keeper=False, is_captain=False),
        Player(31, "Onesimos Shantanu", is_keeper=False, is_captain=True),
        Player(34, "Demeter Najm", is_keeper=False, is_captain=False),
        Player(35, "Toni Efraim", is_keeper=False, is_captain=False),
        Player(92, "Thiemo Vlastimir", is_keeper=False, is_captain=False),
    ]

    assert info.away_team.lineup == [
        Player(1, "Marián Borivoje", is_keeper=True, is_captain=False),
        Player(3, "Osmund Hardwin", is_keeper=False, is_captain=False),
        Player(5, "Culhwch Naranbaatar", is_keeper=False, is_captain=False),
        Player(7, "Shakti Chaza'el", is_keeper=False, is_captain=False),
        Player(8, "Hesiodos Lovrenco", is_keeper=False, is_captain=False),
        Player(9, "Kristo Flanagan", is_keeper=False, is_captain=False),
        Player(10, "Klim Freyr", is_keeper=False, is_captain=False),
        Player(11, "Radoslav Artur", is_keeper=False, is_captain=False),
        Player(18, "Zachary Sumeet", is_keeper=False, is_captain=True),
        Player(26, "Fedlimid Abhishek", is_keeper=False, is_captain=False),
        Player(38, "Abel Finnur", is_keeper=False, is_captain=False),
        Player(69, "Jēkabs Jae", is_keeper=False, is_captain=False),
    ]
