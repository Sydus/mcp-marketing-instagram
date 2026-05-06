"""mcp-marketing-instagram  — server Agent24 pattern."""
from __future__ import annotations
import os
import sys
from pathlib import Path
from typing import Optional

from mcp_common import create_mcp_app, get_creds, tool

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

mcp, app, main = create_mcp_app(
    name="mcp-marketing-instagram",
    instructions=(
        "Instagram Business: pubblicazione di media (immagini, reel, "
        "carosello), gestione profilo, insights di account e media, "
        "rate limit di publishing, validazione access token. Tutti i "
        "tool richiedono identity: l'access_token e l'instagram_account_id "
        "vengono risolti dall'api-key del cliente."
    ),
    port=int(os.environ.get("PORT", "8127")),
)


_MCP_NAME = "mcp-marketing-instagram"


def _get_client():
    """Crea InstagramClient con credenziali per-request dal broker."""
    from instagram_client import InstagramClient
    creds = get_creds().get("instagram", {})
    os.environ["INSTAGRAM_ACCESS_TOKEN"] = creds.get("access_token", os.environ.get("INSTAGRAM_ACCESS_TOKEN", ""))
    os.environ["INSTAGRAM_BUSINESS_ACCOUNT_ID"] = creds.get("account_id", os.environ.get("INSTAGRAM_BUSINESS_ACCOUNT_ID", ""))
    os.environ["FACEBOOK_APP_ID"] = creds.get("facebook_app_id", os.environ.get("FACEBOOK_APP_ID", "placeholder"))
    os.environ["FACEBOOK_APP_SECRET"] = creds.get("facebook_app_secret", os.environ.get("FACEBOOK_APP_SECRET", "placeholder"))
    # Forza reload settings con nuove credenziali
    import src.config as _cfg
    _cfg._settings = None
    return InstagramClient()


# ── Profile & Media ──────────────────────────────────────────────────────────

@tool(mcp, mcp_name=_MCP_NAME)
async def get_profile_info(account_id: Optional[str] = None) -> dict:
    """Get Instagram business profile information including followers, bio, and account details."""
    client = _get_client()
    try:
        result = await client.get_profile_info(account_id=account_id)
        return result.model_dump() if hasattr(result, "model_dump") else result.__dict__
    finally:
        await client.close()


@tool(mcp, mcp_name=_MCP_NAME)
async def get_media_posts(limit: int = 25, after: Optional[str] = None) -> list:
    """Get recent media posts from Instagram account with engagement metrics."""
    client = _get_client()
    try:
        result = await client.get_media_posts(limit=limit, after=after)
        return [r.model_dump() if hasattr(r, "model_dump") else r.__dict__ for r in result]
    finally:
        await client.close()


@tool(mcp, mcp_name=_MCP_NAME)
async def get_media_insights(media_id: str) -> list:
    """Get detailed insights and analytics for a specific Instagram post (likes, comments, reach, shares, saved)."""
    client = _get_client()
    try:
        result = await client.get_media_insights(media_id=media_id)
        return [r.model_dump() if hasattr(r, "model_dump") else r.__dict__ for r in result]
    finally:
        await client.close()


@tool(mcp, mcp_name=_MCP_NAME)
async def publish_media(
    image_url: Optional[str] = None,
    video_url: Optional[str] = None,
    caption: str = "",
    location_id: Optional[str] = None,
) -> dict:
    """Upload and publish an image or video to Instagram with caption and optional location. Provide either image_url or video_url."""
    from src.models.instagram_models import PublishMediaRequest
    client = _get_client()
    try:
        request = PublishMediaRequest(
            image_url=image_url,
            video_url=video_url,
            caption=caption,
            location_id=location_id,
        )
        result = await client.publish_media(request)
        return result.model_dump() if hasattr(result, "model_dump") else result.__dict__
    finally:
        await client.close()


@tool(mcp, mcp_name=_MCP_NAME)
async def publish_reel(video_url: str, caption: str = "", share_to_feed: bool = True) -> dict:
    """Publish a Reel to Instagram."""
    client = _get_client()
    try:
        result = await client.publish_reel(video_url=video_url, caption=caption, share_to_feed=share_to_feed)
        return result.model_dump() if hasattr(result, "model_dump") else result.__dict__
    finally:
        await client.close()


@tool(mcp, mcp_name=_MCP_NAME)
async def publish_carousel(image_urls: list[str], caption: str = "") -> dict:
    """Publish a carousel (multiple images, 2-10) to Instagram."""
    client = _get_client()
    try:
        result = await client.publish_carousel(image_urls=image_urls, caption=caption)
        return result.model_dump() if hasattr(result, "model_dump") else result.__dict__
    finally:
        await client.close()


# ── Insights ─────────────────────────────────────────────────────────────────

@tool(mcp, mcp_name=_MCP_NAME)
async def get_account_insights(
    metrics: Optional[list[str]] = None,
    period: str = "day",
) -> list:
    """Get account-level insights (reach, profile_views, website_clicks). Period: 'day' or 'lifetime'."""
    from src.models.instagram_models import InsightPeriod
    client = _get_client()
    try:
        period_enum = InsightPeriod(period) if period else InsightPeriod.DAY
        result = await client.get_account_insights(metrics=metrics, period=period_enum)
        return [r.model_dump() if hasattr(r, "model_dump") else r.__dict__ for r in result]
    finally:
        await client.close()


@tool(mcp, mcp_name=_MCP_NAME)
async def get_content_publishing_limit() -> dict:
    """Check how many more posts you can publish today (quota usage and config)."""
    client = _get_client()
    try:
        result = await client.get_content_publishing_limit()
        return result.model_dump() if hasattr(result, "model_dump") else result.__dict__
    finally:
        await client.close()


# ── Pages & Token ─────────────────────────────────────────────────────────────

@tool(mcp, mcp_name=_MCP_NAME)
async def get_account_pages() -> list:
    """Get Facebook pages connected to the account and their Instagram business accounts."""
    client = _get_client()
    try:
        result = await client.get_account_pages()
        return [r.model_dump() if hasattr(r, "model_dump") else r.__dict__ for r in result]
    finally:
        await client.close()


@tool(mcp, mcp_name=_MCP_NAME)
async def validate_access_token() -> dict:
    """Validate the Instagram API access token and check permissions."""
    client = _get_client()
    try:
        valid = await client.validate_access_token()
        return {"valid": valid}
    finally:
        await client.close()


# ── Comments ──────────────────────────────────────────────────────────────────

@tool(mcp, mcp_name=_MCP_NAME)
async def get_comments(media_id: str, limit: int = 25) -> list:
    """Get comments on a media post."""
    client = _get_client()
    try:
        result = await client.get_comments(media_id=media_id, limit=limit)
        return [r.model_dump() if hasattr(r, "model_dump") else r.__dict__ for r in result]
    finally:
        await client.close()


@tool(mcp, mcp_name=_MCP_NAME)
async def post_comment(media_id: str, message: str) -> dict:
    """Post a top-level comment on a media post."""
    client = _get_client()
    try:
        result = await client.post_comment(media_id=media_id, message=message)
        return result.model_dump() if hasattr(result, "model_dump") else result.__dict__
    finally:
        await client.close()


@tool(mcp, mcp_name=_MCP_NAME)
async def reply_to_comment(comment_id: str, message: str) -> dict:
    """Reply to a specific comment."""
    client = _get_client()
    try:
        result = await client.reply_to_comment(comment_id=comment_id, message=message)
        return result.model_dump() if hasattr(result, "model_dump") else result.__dict__
    finally:
        await client.close()


@tool(mcp, mcp_name=_MCP_NAME)
async def delete_comment(comment_id: str) -> dict:
    """Delete a comment."""
    client = _get_client()
    try:
        result = await client.delete_comment(comment_id=comment_id)
        return {"success": result}
    finally:
        await client.close()


@tool(mcp, mcp_name=_MCP_NAME)
async def hide_comment(comment_id: str, hide: bool = True) -> dict:
    """Hide or unhide a comment."""
    client = _get_client()
    try:
        result = await client.hide_comment(comment_id=comment_id, hide=hide)
        return {"success": result}
    finally:
        await client.close()


# ── Hashtags ──────────────────────────────────────────────────────────────────

@tool(mcp, mcp_name=_MCP_NAME)
async def search_hashtag(hashtag: str) -> dict:
    """Search for a hashtag ID by name on Instagram."""
    client = _get_client()
    try:
        result = await client.search_hashtag(hashtag_name=hashtag)
        return result.model_dump() if hasattr(result, "model_dump") else result.__dict__
    finally:
        await client.close()


@tool(mcp, mcp_name=_MCP_NAME)
async def get_hashtag_media(hashtag_id: str, media_type: str = "top", limit: int = 25) -> list:
    """Get top or recent media for a hashtag. media_type: 'top' or 'recent'."""
    client = _get_client()
    try:
        result = await client.get_hashtag_media(hashtag_id=hashtag_id, media_type=media_type, limit=limit)
        return [r.model_dump() if hasattr(r, "model_dump") else r.__dict__ for r in result]
    finally:
        await client.close()


# ── Stories & Mentions ────────────────────────────────────────────────────────

@tool(mcp, mcp_name=_MCP_NAME)
async def get_stories() -> list:
    """Get current active stories for the Instagram account."""
    client = _get_client()
    try:
        result = await client.get_stories()
        return [r.model_dump() if hasattr(r, "model_dump") else r.__dict__ for r in result]
    finally:
        await client.close()


@tool(mcp, mcp_name=_MCP_NAME)
async def get_mentions(limit: int = 25) -> list:
    """Get recent posts and comments that mention the account (@mention)."""
    client = _get_client()
    try:
        result = await client.get_mentions(limit=limit)
        return [r.model_dump() if hasattr(r, "model_dump") else r.__dict__ for r in result]
    finally:
        await client.close()


# ── Business Discovery ────────────────────────────────────────────────────────

@tool(mcp, mcp_name=_MCP_NAME)
async def business_discovery(username: str) -> dict:
    """Get public profile info for another Instagram business/creator account."""
    client = _get_client()
    try:
        result = await client.business_discovery(target_username=username)
        return result.model_dump() if hasattr(result, "model_dump") else result.__dict__
    finally:
        await client.close()


# ── Direct Messages ────────────────────────────────────────────────────────────

@tool(mcp, mcp_name=_MCP_NAME)
async def get_conversations(page_id: Optional[str] = None, limit: int = 25) -> list:
    """Get Instagram DM conversations. Requires instagram_manage_messages permission (Advanced Access)."""
    client = _get_client()
    try:
        result = await client.get_conversations(page_id=page_id, limit=limit)
        return [r.model_dump() if hasattr(r, "model_dump") else r.__dict__ for r in result]
    finally:
        await client.close()


@tool(mcp, mcp_name=_MCP_NAME)
async def get_conversation_messages(conversation_id: str, limit: int = 25) -> list:
    """Get messages from a specific Instagram DM conversation. Requires instagram_manage_messages permission."""
    client = _get_client()
    try:
        result = await client.get_conversation_messages(conversation_id=conversation_id, limit=limit)
        return [r.model_dump() if hasattr(r, "model_dump") else r.__dict__ for r in result]
    finally:
        await client.close()


@tool(mcp, mcp_name=_MCP_NAME)
async def send_dm(recipient_id: str, message: str) -> dict:
    """Send Instagram direct message. Requires Advanced Access. Can only reply within 24h of user's last message."""
    from src.models.instagram_models import SendDMRequest
    client = _get_client()
    try:
        request = SendDMRequest(recipient_id=recipient_id, message=message)
        result = await client.send_dm(request)
        return result.model_dump() if hasattr(result, "model_dump") else result.__dict__
    finally:
        await client.close()


if __name__ == "__main__":
    main()
