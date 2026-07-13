from __future__ import annotations
from dataclasses import dataclass
from dataclass_csv import DataclassWriter
from datetime import datetime, date, time
from threading import Thread
import time
import os
from pathlib import Path
from tqdm import tqdm

from mtggympy.config.app_config import Setup
from mtggympy.config.decks import DeckName
from mtggympy.config.logging_config import dojo_log as logger
from mtggympy.gameengine.cards.instances.types import CardInstance, LandInstance
from mtggympy.gameengine.constants import DeathDescription
from mtggympy.gameengine.state.core import GameState
from mtggympy.server.agents.base import AgentBase
from mtggympy.server.agents.constants import InternalAgentType
from mtggympy.server.agents.simple import Goldfish, Monkey
from mtggympy.server.agents.rulesbased import RulesBasedAgent
from mtggympy.server.session.multi_client import MultiClientSession as MtgSession
import mtggympy.config.app_config as app_conf

DATE_FORMAT: str = "%Y-%m-%d"

@dataclass
class ExperimentMetadata:
    main_setup: Setup 
    deck_name: DeckName
    with_backup_state: bool
    number_of_episodes: int
    execution_date: date
    execution_start: time

@dataclass
class GameResult:
    winning_seat: int
    loser_death_description: DeathDescription
    halfturns_played: int
    milliseconds_passed: float
    seat_0_lands: int
    seat_0_board_size: int
    seat_0_hand_size: int
    seat_1_lands: int
    seat_1_board_size: int
    seat_1_hand_size: int

def fight_two_player(no_of_episodes: int, agent_types: tuple[InternalAgentType, InternalAgentType]):
    metadata: ExperimentMetadata = ExperimentMetadata(
        app_conf.CURRENT_SETUP,
        app_conf.DEFAULT_DECK,
        app_conf.TRASITION_WITH_STATE_BACKUP,
        no_of_episodes,
        datetime.now().date(),
        datetime.now().time(),
    )
    print (metadata)
    game_results: list[GameResult] = []
    for episode in tqdm(range(no_of_episodes)):
        start_time: float = time.time()
        session: MtgSession = MtgSession() 
        session_thread: Thread = Thread(target=session.tick_session, daemon=False)
        session_thread.start()
        agent_0: AgentBase =  produce_agent(agent_types[0], session, target_seat=0)
        agent_0_thread:  Thread = Thread(target=agent_0.play_game, daemon=True)
        agent_0_thread.start()
        agent_1: AgentBase =  produce_agent(agent_types[1], session, target_seat=1)
        agent_1_thread:  Thread = Thread(target=agent_1.play_game, daemon=True)
        agent_1_thread.start()
        with session.shutting_down_condition:
            session.shutting_down_condition.wait_for(lambda: session.shutting_down)
            end_time: float =  time.time()
            game_results.append(process_game_result(session.game_state, episode, end_time - start_time))
    print("Average lands in play for seat 0: {}".format(
        sum(result.seat_0_lands for result in game_results) / len(game_results)
    ))
    print("Average nonlands in play for seat 0: {}".format(
        sum(result.seat_0_board_size for result in game_results) / len(game_results)
    ))
    print("Average game length in halfturns: {}".format(
        sum(result.halfturns_played for result in game_results) / len(game_results)
    ))
    print("Average game length in ms: {}".format(
        sum(result.milliseconds_passed for result in game_results) / len(game_results)
    ))
    print("Winrate for seat 0: {}".format(
        sum(result.winning_seat == 0 for result in game_results) / len(game_results)
    ))
    save_experiment_result(metadata, game_results)
    return

def save_experiment_result(metadata: ExperimentMetadata, game_results: list[GameResult]) -> None:
    print("SRC-PATH: {}".format(app_conf.SRC_DIR))
    print("RESULT-PATH: {}".format(app_conf.EXPERIMENT_RESULT_DIR))
    date_path: str = os.path.join(app_conf.EXPERIMENT_RESULT_DIR, metadata.execution_date.strftime(DATE_FORMAT))
    Path(date_path).mkdir(parents=True, exist_ok=True)
    prior_folder_names: list[str] = os.listdir(date_path)
    experiment_no : int = 1
    if len(prior_folder_names) > 0:
        experiment_no = max(map(int, prior_folder_names)) + 1
    exp_path: str = os.path.join(date_path, str(experiment_no))
    Path(exp_path).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(exp_path, "game_results.csv"), "w") as csv:
        writer = DataclassWriter(csv, game_results, GameResult)
        writer.write()
    with open(os.path.join(exp_path, "metadata.csv"), "w") as csv:
        writer = DataclassWriter(csv, [metadata], ExperimentMetadata)
        writer.write()
    return
    

def produce_agent(type: InternalAgentType, session: MtgSession, target_seat: int) -> AgentBase:
    match type:
        case InternalAgentType.MONKEY:
            return Monkey(session, str(target_seat) + "-Monkey", target_seat)
        case InternalAgentType.RULESBASED:
            return RulesBasedAgent(session, str(target_seat) + "-RulesBasedAgent", target_seat)
        case InternalAgentType.GOLDFISH:
            return Goldfish(session, str(target_seat) + "-Goldfish", target_seat)

def process_game_result(final_state: GameState, episode: int, seconds_passed: float) -> GameResult:
    winning_seat: int = final_state.winner_positions[0]
    loser_seat: int = (winning_seat + 1) % len(final_state.player_states)
    loser_death_reason: DeathDescription | None = final_state.player_states[loser_seat].death_description
    assert loser_death_reason is not None
    land_count_0, nonland_count_0 = count_lands_and_nonlands(final_state.player_states[0].cards_in_play)
    land_count_1, nonland_count_1 = count_lands_and_nonlands(final_state.player_states[1].cards_in_play)

    result: GameResult = GameResult(
        winning_seat,
        loser_death_reason,
        final_state.halfturns_completed,
        milliseconds_passed=seconds_passed*1000,
        seat_0_lands=land_count_0,
        seat_0_board_size=nonland_count_0,
        seat_0_hand_size=len(final_state.player_states[0].cards_in_hand),
        seat_1_lands=land_count_1,
        seat_1_board_size=nonland_count_1,
        seat_1_hand_size=len(final_state.player_states[1].cards_in_hand),
    )
    
    logger.info("Finished episode {} in {} ms with winner {} by opp death through {}".format(
        episode, result.milliseconds_passed ,result.winning_seat, result.loser_death_description.value)
        )
    return result

def count_lands_and_nonlands(permanents: list[CardInstance]) -> tuple[int, int]:
    land_count: int  = sum(isinstance(card, LandInstance) for card in permanents)
    nonland_count: int  = len(permanents) - land_count
    return (land_count, nonland_count)
        