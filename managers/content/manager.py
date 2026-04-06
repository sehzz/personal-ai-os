

from managers.base import BaseManager, ManagerRequest, ManagerResponse


class ContentManager(BaseManager):

    @property
    def name(self) -> str:
        return "content"

    def process(self, request: ManagerRequest) -> ManagerResponse:
        return ManagerResponse(
            manager=self.name,
            status="success",
            summary="Content Manager stub: no real tools yet",
        )