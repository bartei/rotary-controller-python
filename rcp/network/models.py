from typing import Optional

from pydantic import BaseModel, Field


class Wireless(BaseModel):
    password: Optional[str]
    ssid: str


class NetworkInterface(BaseModel):
    name: str
    dhcp: bool
    address: Optional[str] = None
    netmask: Optional[int] = None
    gateway: Optional[str] = None
    wireless: Optional[Wireless] = None


class RfkillStatus(BaseModel):
    id: int
    type: str
    device: str
    soft: str
    hard: str
