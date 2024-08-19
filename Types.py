from typing import TypedDict
from enum import Enum


class ChatStates(Enum):
    NoWord = 0
    SetWord = 1
    SetLevel = 2
    GenerateList = 3
    SetAudioSettings = 4
    GenerateAudio = 5


class EnglishLevel(Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"


class MyChat(TypedDict):
    status: ChatStates
    last_word: str
    last_list: str
    level: str
    speed: float

