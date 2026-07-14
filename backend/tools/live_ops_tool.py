from fastmcp import FastMCP

from tools.live_ops_mock import get_all_wait_times

mcp = FastMCP("epic-worlds-live-ops")


@mcp.tool()
def get_live_wait_times(area: str | None = None) -> list[dict]:
    """Returns current wait times for Epic Worlds attractions, as a list of
    {attraction, area, wait_minutes} dicts. Use this to answer questions about
    crowding, current wait times, or which attractions are busiest right now.

    Args:
        area: Optional filter. One of: "future_world", "adventure_world",
            "fable_world". Omit to get wait times for all attractions across
            the whole park. Do not use "park_wide" here — that value only
            applies to knowledge-base area guides, not live wait time data.
    """
    all_wait_times = get_all_wait_times()
    if area is None:
        return all_wait_times
    return [row for row in all_wait_times if row["area"] == area]
