

from managers.base import BaseManager, ManagerRequest, ManagerResponse


class FinanceManager(BaseManager):

    @property
    def name(self) -> str:
        return "finance"

    def process(self, request: ManagerRequest) -> ManagerResponse:
        task = request.task

        if task == "ping":
            return ManagerResponse(
                manager=self.name,
                status="success",
                summary="pong"
            )

        return ManagerResponse(
            manager=self.name,
            status="success",
            summary="Finance Manager stub: no real tools yet",
        )