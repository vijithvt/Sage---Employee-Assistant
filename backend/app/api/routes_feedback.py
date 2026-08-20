"""API route: POST /feedback — record a thumbs up/down rating for an answer."""

from pathlib import Path

from fastapi import APIRouter

from app.core.config import settings
from app.models.schemas import FeedbackRequest
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

FEEDBACK_LOG_PATH = Path(settings.CHROMA_PERSIST_DIR).parent / "feedback.log"


@router.post("/feedback")
def submit_feedback(feedback: FeedbackRequest) -> dict:
    FEEDBACK_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with FEEDBACK_LOG_PATH.open("a", encoding="utf-8") as log_file:
        log_file.write(feedback.model_dump_json() + "\n")

    logger.info("Feedback recorded: rating=%s", feedback.rating)
    return {"detail": "Feedback recorded."}
