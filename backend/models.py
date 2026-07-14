from typing import Literal, Union

from pydantic import BaseModel, Field


class FieldItem(BaseModel):
    label: str
    value: str | int
    type: Literal["text", "dots", "wait_badge", "number"] = Field(
        description=(
            "text: plain value. dots: a 0-5 rating meter (e.g. thrill level). "
            "number: a prominent stat with its unit inline in value (e.g. "
            "'2,400 guests / hr'). wait_badge: a colored wait-time pill."
        )
    )
    level: Literal["low", "med", "high"] | None = None


class AttractionCard(BaseModel):
    card_type: Literal["attraction"] = "attraction"
    title: str
    area: str
    subtitle: str | None = None
    fields: list[FieldItem]
    badges: list[str] = []
    footer: str | None = None


class LiveOpsRow(BaseModel):
    name: str
    wait_minutes: int
    level: Literal["low", "med", "high"]


class LiveOpsCard(BaseModel):
    card_type: Literal["live_ops"] = "live_ops"
    title: str
    area: str | None = None
    rows: list[LiveOpsRow]


class AccessibilityCard(BaseModel):
    card_type: Literal["accessibility"] = "accessibility"
    title: str
    area: str
    fields: list[FieldItem]
    footer: str | None = None


class EventCard(BaseModel):
    card_type: Literal["event"] = "event"
    title: str
    area: str
    description: str
    footer: str | None = None


class GuideCard(BaseModel):
    card_type: Literal["guide"] = "guide"
    message: str
    example_questions: list[str]


class FallbackCard(BaseModel):
    card_type: Literal["fallback"] = "fallback"
    message: str


Card = Union[AttractionCard, LiveOpsCard, AccessibilityCard, EventCard, GuideCard, FallbackCard]


class ResponsePayload(BaseModel):
    cards: list[Card]
    connector_label: str | None = None
