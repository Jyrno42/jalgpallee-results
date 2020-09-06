#!/usr/bin/env python3
import requests
import typing

from bs4 import BeautifulSoup


class GoalEventData(typing.NamedTuple):
    penalty: bool


class SwitchEventData(typing.NamedTuple):
    off_player_nr: bool


class CardEventData(typing.NamedTuple):
    is_yellow: bool
    is_red: bool
    reason: str


class Event(typing.NamedTuple):
    time: int
    overtime_offset: typing.Optional[int]
    event_type: str  # goal | own_goal | penalty_miss | switch | card
    team: str  # home | away
    player_nr: int

    event_data: typing.Optional[
        typing.Union[
            GoalEventData,
            SwitchEventData,
            CardEventData,
        ]
    ]


class Player(typing.NamedTuple):
    number: int
    name: str

    is_keeper: bool
    is_captain: bool


class Team(typing.NamedTuple):
    name: str
    team_id: str

    lineup: typing.List[Player]
    substitutes: typing.List[Player]


class GameInfo(typing.NamedTuple):
    home_team: str
    away_team: str

    official: bool

    home_score: typing.Union[int, str]
    away_score: typing.Union[int, str]

    home_halftime_score: typing.Optional[typing.Union[int, str]]
    away_halftime_score: typing.Optional[typing.Union[int, str]]

    location: str

    attendance: typing.Optional[int]

    events: typing.List[Event]


special_scores = ["+", "-", ""]


def get_score(score_node, allow_none=False):
    home_score = None
    away_score = None

    score_node = score_node[0] if score_node and isinstance(score_node, list) else None
    score_node = score_node.parent if score_node else None

    if score_node is None:
        if allow_none:
            return None, None

        raise Exception("Score node not found")

    score = (
        score_node.get_text().replace("Lõppseis", "").replace("Vaheajaseis", "").strip()
    )

    if ":" in score:
        score_parts = [x.strip() for x in score.split(":")]

    else:
        score_parts = [x.strip() for x in score.split("-")]

    if len(score_parts) != 2:
        raise Exception(f"Final format is bad {score}")

    home_score = (
        int(score_parts[0]) if score_parts[0] not in special_scores else score_parts[0]
    )
    away_score = (
        int(score_parts[1]) if score_parts[1] not in special_scores else score_parts[1]
    )

    return home_score, away_score


def get_attendance(soup: BeautifulSoup) -> typing.Optional[int]:
    attendance_node = soup.find("li", class_="group")

    if not attendance_node:
        return None

    attendance = attendance_node.get_text().replace("Pealtvaatajaid", "").strip()

    try:
        return int(attendance)

    except (TypeError, ValueError):
        return None


def get_players(node) -> typing.List[Player]:
    players = []

    nodes = node.find_all("li") if node else []

    for player_node in nodes:
        classes = player_node.get("class") or []
        if "title" in classes or "large" in classes:
            continue

        nr_node = player_node.find(class_="count")

        if nr_node is None:
            continue

        player_nr = nr_node.get_text().replace(".", "").strip()

        name_node = player_node.find("p")
        name = name_node.get_text()

        is_keeper = False
        is_captain = False

        for role_node in name_node.find_all("small"):
            role_txt = role_node.get_text().strip()

            if role_txt:
                if role_txt == "(VV)":
                    is_keeper = True
                elif role_txt == "(K)":
                    is_captain = True

                name = name.replace(role_txt, "").strip()

        player_nr = player_nr.strip()
        name = name.strip()

        players.append(
            Player(
                number=int(player_nr),
                name=name,
                is_keeper=is_keeper,
                is_captain=is_captain,
            )
        )

    return players


def get_events(
    soup, *, home_name, away_name, home_lineup, away_lineup, home_subs, away_subs
):
    events = []

    events_node = soup.find(text="Mängu sündmused")
    events_node = events_node.parent if events_node else None
    events_node = events_node.parent if events_node else None
    events_node = events_node.parent if events_node else None
    events_node = events_node.find(class_="timeline") if events_node else None
    nodes = events_node.find_all("li") if events_node else []

    for node in nodes:
        # Get event time
        time_node = node.find(class_="order")
        time_txt = time_node.get_text().replace("′", "").strip()

        if "+" in time_txt:
            time, overtime_offset = [int(x.strip()) for x in time_txt.split("+")]
        else:
            time = int(time_txt)
            overtime_offset = None

        # Get event type
        status_node = node.find(class_="status")
        goal_node = status_node.find("span", class_="football")
        switch_node = status_node.find("span", class_="switch")
        card_node = status_node.find("span", class_="card")

        is_goal = goal_node is not None and "red" not in (goal_node.get("class") or [])
        is_own_goal = goal_node is not None and "red" in (goal_node.get("class") or [])
        is_success_penalty = goal_node is not None and "penalty" in (
            goal_node.get("class") or []
        )
        is_failed_penalty = (
            is_goal is False
            and is_own_goal is False
            and is_success_penalty is False
            and status_node.find(class_="penalty") is not None
        )

        is_substitution = switch_node is not None

        is_card = card_node is not None
        is_yellow = is_card and "yellow" in (card_node.get("class") or [])
        is_red = is_card and "red" in (card_node.get("class") or [])
        card_reason = (card_node.get("title").strip() or "") if card_node else ""

        # Get player nr
        player_node = node.find(class_="player")
        nr_node = player_node.find("span")
        player_nr = int(nr_node.get_text().replace(".", "").strip())
        off_player_nr = None

        # In case of a sub we also need to get the other players nr
        if is_substitution:
            off_nr_node = player_node.find_all("span")[-1]
            off_player_nr = int(off_nr_node.get_text().replace(".", "").strip())

        team = (
            "home"
            if node.find(class_="country").get_text().strip() == home_name
            else "away"
        )

        event_type = ""
        event_data = None

        if is_goal:
            event_type = "goal"
            event_data = GoalEventData(penalty=is_success_penalty)
        elif is_own_goal:
            event_type = "own_goal"
        elif is_failed_penalty:
            event_type = "penalty_miss"
        elif is_substitution:
            event_type = "switch"
            event_data = SwitchEventData(off_player_nr=off_player_nr)
        elif is_card:
            event_type = "card"
            event_data = CardEventData(
                is_yellow=is_yellow, is_red=is_red, reason=card_reason
            )

        events.append(
            Event(
                time=time,
                overtime_offset=overtime_offset,
                player_nr=player_nr,
                team=team,
                event_type=event_type,
                event_data=event_data,
            )
        )

    return events


def get_game_info(game_id: int):
    game_url = f"http://jalgpall.ee/voistlused/protocol/{game_id}"

    response = requests.get(game_url)

    if response.status_code == 500:
        raise Exception("Game does not exist")

    response.raise_for_status()

    soup = BeautifulSoup(response.content, features="html.parser")

    final_score_node = soup.find_all("small", string="Lõppseis")
    final_score = get_score(final_score_node)

    halftime_score_node = soup.find_all("small", string="Vaheajaseis")
    halftime_score = get_score(halftime_score_node, allow_none=True)

    location_node = soup.find("li", class_="location")
    location = location_node.get_text() if location_node else ""

    lineup_node = soup.find("div", class_="lineup") or None
    home_lineup_node = lineup_node.find("ul", class_="left") if lineup_node else None
    away_lineup_node = lineup_node.find("ul", class_="right") if lineup_node else None

    home_lineup = get_players(home_lineup_node)
    away_lineup = get_players(away_lineup_node)

    home_subs = []
    away_subs = []

    subs_node = soup.find(text="Vahetusmängijad")
    if (
        subs_node
        and subs_node.parent
        and subs_node.parent.parent
        and subs_node.parent.parent.parent
    ):
        home_subs = get_players(
            subs_node.parent.parent.parent.find("ul", class_="left")
        )
        away_subs = get_players(
            subs_node.parent.parent.parent.find("ul", class_="right")
        )

    home_team = None
    away_team = None

    for i, node in enumerate(soup.find_all(class_="team")):
        team_name = node.get_text().strip()
        team_id = node.find("a").get("href").split("/")[-1]

        if i == 0:
            home_team = Team(
                name=team_name,
                team_id=team_id,
                lineup=home_lineup,
                substitutes=home_subs,
            )
        elif i == 1:
            away_team = Team(
                name=team_name,
                team_id=team_id,
                lineup=away_lineup,
                substitutes=away_subs,
            )
        else:
            raise Exception("More than two teams found")

    events = get_events(
        soup,
        home_name=home_team.name,
        away_name=away_team.name,
        home_lineup=home_lineup,
        away_lineup=away_lineup,
        home_subs=home_subs,
        away_subs=away_subs,
    )

    # FIXME: Does not handle case where extra time or penalties are used to determine the winner.

    return GameInfo(
        home_score=final_score[0],
        away_score=final_score[1],
        home_halftime_score=halftime_score[0],
        away_halftime_score=halftime_score[1],
        home_team=home_team,
        away_team=away_team,
        location=location,
        attendance=get_attendance(soup),
        official=soup.find(text="Mitteametlik") is None,
        events=events,
    )
