from abc import ABC, abstractmethod

class ModelManagerABC(ABC):
    @abstractmethod
    async def get_available_models(self, db):
        pass

    @abstractmethod
    async def download_models(self, db):
        pass

    @abstractmethod
    async def predict(self, model_id, data):
        pass