from pathlib import Path
import logging

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "emails"


def build_congrats_email_html(
    username: str,
    email: str,
    total_votes: int,
) -> str:

    template_path = TEMPLATES_DIR / "top_vote_getter_congrats.html"

    try:
        html_template = template_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.error(f"❌ Email template not found at: {template_path}")
        raise

    html_content = (
        html_template
        .replace("{{USERNAME}}", username)
        .replace("{{EMAIL}}", email)
        .replace("{{TOTAL_VOTES}}", str(total_votes))
    )

    return html_content