"""Table of contents action"""
from typing import Iterable

from pydantic import BaseModel

from kakuyomu.types import EpisodeId

type CSRFToken = str  # type: ignore


class DeleteRequestForm(BaseModel):
    """Delete request form"""

    csrf_token: CSRFToken
    bulk_action_name: str
    target_toc_item_id: list[str]


class TOCAction:
    """Table of contents action"""

    @staticmethod
    def delete(csrf_token: CSRFToken, episodes: Iterable[EpisodeId]) -> DeleteRequestForm:
        """
        Delete episodes

        Returns
        -------
        JsonDict
        csrf_token: xxxxxxxxxxxxxxxxxxxx
        bulk_action_name: delete
        target_toc_item_id: episode:00000000000000000001
        target_toc_item_id: episode:00000000000000000002

        """
        target_toc_item_id = [f"episode:{episode}" for episode in episodes]
        result = DeleteRequestForm(
            csrf_token=csrf_token,
            bulk_action_name="delete",
            target_toc_item_id=target_toc_item_id,
        )
        return result
