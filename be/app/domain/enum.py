from enum import Enum

class ReportTypeEnum(str, Enum):
        daily = "daily"
        weekly = "weekly"
        monthly = "monthly"

class GameTypeEnum(str, Enum):
        game_click = "GameClick"
        game_cv = "GameCV"

class SessionStateEnum(str, Enum):
        playing = "playing"
        pause = "pause"
        end = "end"

class RoleEnum(str, Enum):
        child = "child"
        admin = "admin"

class GenderEnum(str, Enum):
    male = "male"
    female = "female"