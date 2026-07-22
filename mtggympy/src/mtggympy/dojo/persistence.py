from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Protocol, Sequence
from dataclass_csv import DataclassWriter
import os
from pathlib import Path
from datetime import date, time, datetime

from mtggympy.config.app_config import Setup
from mtggympy.config.decks import DeckName
from mtggympy.config import app_config as app_conf



DATE_FORMAT: str = "%Y-%m-%d"


@dataclass
class ExperimentMetadata:
    main_setup: Setup 
    deck_name: DeckName
    with_backup_state: bool
    number_of_episodes: int
    execution_date: date
    execution_start: time

class IsDataclass(Protocol):
    # as already noted in comments, checking for this attribute is currently
    # the most reliable way to ascertain that something is a dataclass
    __dataclass_fields__: ClassVar[Dict[str, Any]] 

def produce_metadata(number_of_episodes: int, start_datetime: datetime) -> ExperimentMetadata:
    return ExperimentMetadata(
        app_conf.CURRENT_SETUP,
        app_conf.DEFAULT_DECK,
        app_conf.TRASITION_WITH_STATE_BACKUP,
        number_of_episodes,
        start_datetime.date(),
        start_datetime.time(),
    )

def save_experiment_result(start_datetime: datetime, results: Sequence[IsDataclass], dataclass: type[IsDataclass]) -> None:
    metadata: ExperimentMetadata =  produce_metadata(len(results), start_datetime)
    date_path: str = os.path.join(app_conf.EXPERIMENT_RESULT_DIR, metadata.execution_date.strftime(DATE_FORMAT))
    Path(date_path).mkdir(parents=True, exist_ok=True)
    prior_folder_names: list[str] = os.listdir(date_path)
    experiment_no : int = 1
    if len(prior_folder_names) > 0:
        experiment_no = max(map(int, prior_folder_names)) + 1
    exp_path: str = os.path.join(date_path, str(experiment_no))
    Path(exp_path).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(exp_path, "results.csv"), "w") as csv:
        writer = DataclassWriter(csv, results, dataclass)
        writer.write()
    with open(os.path.join(exp_path, "metadata.csv"), "w") as csv:
        writer = DataclassWriter(csv, [metadata], ExperimentMetadata)
        writer.write()
    return