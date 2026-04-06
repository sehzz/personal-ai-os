from abc import ABC, abstractmethod
from pydantic import BaseModel


class ManagerRequest(BaseModel):
    task: str
    context: dict


class ManagerResponse(BaseModel):
    manager: str
    status: str
    summary: str
    data: dict = {}
    alerts: list[str] = []

class BaseManager(ABC):
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def process(self, request: ManagerRequest) -> ManagerResponse:
        pass


if __name__ == "__main__":
    try:
        b = BaseManager()
    except TypeError as e:
        print(f"Cannot instantiate BaseManager: {e}")

    class TestManager(BaseManager):
        @property
        def name(self) -> str:
            return "TestManager"

        def process(self, request: ManagerRequest) -> ManagerResponse:
            return ManagerResponse(
                manager=self.name,
                status="success",
                summary=f"Processed task: {request.task}",
                data={"result": "This is a test response."},
                alerts=[]
            )
        

    tm = TestManager()
    result = tm.process(ManagerRequest(task="hello", context={}))
    print(f"Good: {result}")