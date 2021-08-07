from aenum import Constant


class ModerationStatus(Constant):
    """Options for status of changes to moderated model instances."""

    REJECTED = 0
    PENDING = 1
    APPROVED = 2
    MERGED = 3


class DraftState(Constant):
    """Options for draft state of changes to moderated model instances."""

    DRAFT = 0  # not ready for moderation
    READY = 1  # ready for moderation
