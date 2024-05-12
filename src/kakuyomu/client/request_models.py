"""Request body models for POST or PUT"""

from typing import Iterable

from pydantic import BaseModel

from kakuyomu.types.work import EpisodeId, EpisodeStatus


class NoCsrfToken(BaseModel):
    """Request model without CSRF token"""

    pass


class WithCsrfToken(BaseModel):
    """Request model with CSRF token"""

    csrf_token: str


class DeleteEpisodesRequest(WithCsrfToken):
    """
    Request model to delete episodes

    csrf_token: xxxxxxxxxxxxxxxxxxxx
    bulk_action_name: delete
    target_toc_item_id: episode:00000000000000000001
    target_toc_item_id: episode:00000000000000000002

    """

    bulk_action_name: str
    target_toc_item_id: list[str]

    @classmethod
    def create_from_episode_ids(cls, csrf_token: str, episode_ids: Iterable[EpisodeId]) -> "DeleteEpisodesRequest":
        """Create from episode ids"""
        target_toc_item_id = [f"episode:{episode_id}" for episode_id in episode_ids]
        return cls(
            csrf_token=csrf_token,
            bulk_action_name="delete",
            target_toc_item_id=target_toc_item_id,
        )


class CreateEpisodeRequest(NoCsrfToken):
    """Request model to create episode"""

    title: str
    status: str = "draft"
    edit_reservation: int = 0
    keep_editing: int = 0
    body: str


class UpdateEpisodeRequest(EpisodeStatus, WithCsrfToken):
    """Request model to update episode"""

    title: str
    body: str

    @classmethod
    def create_from_status(
        cls,
        status: EpisodeStatus,
        csrf_token: str,
        title: str,
        body: str,
    ) -> "UpdateEpisodeRequest":
        """Create from status"""
        return cls(
            csrf_token=csrf_token,
            title=title,
            body=body,
            status=status.status,
            edit_reservation=status.edit_reservation,
            keep_editing=status.keep_editing,
            reservation=status.reservation,
            reservation_date=status.reservation_date,
            reservation_time=status.reservation_time,
        )
