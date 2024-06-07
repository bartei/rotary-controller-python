from typing import Optional

from pydantic import BaseModel, Field


class Wireless(BaseModel):
    password: Optional[str]
    ssid: str


class NetworkInterface(BaseModel):
    name: str
    dhcp: bool
    address: Optional[str]
    netmask: Optional[int]
    gateway: Optional[str]
    wireless: Optional[Wireless]


class RfkillStatus(BaseModel):
    id: int
    type: str
    device: str
    soft: str
    hard: str
