

from managers.base import BaseManager, ManagerRequest, ManagerResponse


class LifeAdminManager(BaseManager):

    @property
    def name(self) -> str:
        return "life_admin"

    def process(self, request: ManagerRequest) -> ManagerResponse:
        return ManagerResponse(
            manager=self.name,
            status="success",
            summary="Life Admin Manager stub: no real tools yet",
        )