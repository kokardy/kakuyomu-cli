"""Request body models for POST or PUT"""

import datetime
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
            use_reservation=status.use_reservation,
        )


class _Input(BaseModel):
    """Input model"""

    episodeId: EpisodeId
    reserveDatetime: str | None


class _Variables(BaseModel):
    """Variables model"""

    input: _Input


class PublishRequest(BaseModel):
    """
    Request model to publish episode

    {
      "operationName": "UpdateEpisodeReservationMutation",
      "variables": {
        "input": {
          "episodeId": "16816927859880026113",
          "reserveDatetime": "2024-06-26T19:00:00.000+09:00"
        }
      },
      "query": "mutation UpdateEpisodeReservationMutation($input: UpdateEpisodeReservationInput!) { updateEpisodeReservation(input: $input) { episode { id title work { id title __typename } __typename } __typename } }"
    }

    """  # noqa: E501

    operationName: str = "UpdateEpisodeReservationMutation"
    variables: _Variables
    query: str = "mutation UpdateEpisodeReservationMutation($input: UpdateEpisodeReservationInput!) { updateEpisodeReservation(input: $input) { episode { id title work { id title __typename } __typename } __typename } }"  # noqa: E501

    @classmethod
    def create(
        cls,
        episode_id: EpisodeId,
        publish_at: datetime.datetime | None,
    ) -> "PublishRequest":
        """Create from episode id and publish at"""
        reserveDatetime = publish_at.strftime("%Y-%m-%dT%H:%M:00.000+09:00") if publish_at else None
        return cls(
            variables=_Variables(
                input=_Input(episodeId=episode_id, reserveDatetime=reserveDatetime),
            ),
        )
