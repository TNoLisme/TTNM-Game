from abc import ABC, abstractmethod
from typing import Any

class BaseGameService(ABC):
    def __init__(self, repo: Any):
        self.repo = repo

    @abstractmethod
    def create(self, data: Any) -> dict:
        pass

    @abstractmethod
    def get_by_id(self, entity_id: str) -> Any:
        pass

    @abstractmethod
    def update(self, entity_id: str, data: Any) -> dict:
        pass

    @abstractmethod
    def delete(self, entity_id: str) -> dict:
        pass