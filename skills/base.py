from pydantic import BaseModel
from abc import ABC, abstractmethod


class SkillResult(BaseModel):
    success: bool
    data: dict | None = None
    error: str | None = None


class SkillBase(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def execute(self, **kwargs) -> SkillResult:
        pass


if __name__ == "__main__":
    try:
        s = SkillBase()
    except TypeError as e:
        print(f"Cannot instantiate SkillBase: {e}")

    class TestSkill(SkillBase):
        @property
        def name(self) -> str:
            return "TestSkill"

        def execute(self, **kwargs) -> SkillResult:
            return SkillResult(success=True, data={"message": "This is a test skill."})

    ts = TestSkill()
    result = ts.execute()
    print(f"Good: {result}")