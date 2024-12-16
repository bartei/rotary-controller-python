from typing import Optional

from pydantic import BaseModel, Field


class Wireless(BaseModel):
    password: Optional[str]
    ssid: str


class NetworkInterface(BaseModel):
    name: str
    dhcp: bool
    address: str | None = None
    netmask: int | None = None
    gateway: str | None = None
    wireless: Wireless | None = None


class RfkillStatus(BaseModel):
    id: int
    type: str
    device: str
    soft: str
    hard: str
