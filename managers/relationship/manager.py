

from managers.base import BaseManager, ManagerRequest, ManagerResponse


class RelationshipManager(BaseManager):

    @property
    def name(self) -> str:
        return "relationships"

    def process(self, request: ManagerRequest) -> ManagerResponse:
        return ManagerResponse(
            manager=self.name,
            status="success",
            summary="Relationship Manager stub: no real tools yet",
        )