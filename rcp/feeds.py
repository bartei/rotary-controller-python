from pydantic import BaseModel
from fractions import Fraction

class FeedConfiguration(BaseModel):
    name: str | None = None
    mode: int | None = None
    ratio: Fraction | None = None

THREAD_MM = [
    FeedConfiguration(name="0.35", ratio=Fraction("0.35"), mode=1),
    FeedConfiguration(name="0.40", ratio=Fraction("0.4"), mode=1),
    FeedConfiguration(name="0.45", ratio=Fraction("0.45"), mode=1),
    FeedConfiguration(name="0.50", ratio=Fraction("0.5"), mode=1),
    FeedConfiguration(name="0.70", ratio=Fraction("0.7"), mode=1),
    FeedConfiguration(name="0.80", ratio=Fraction("0.8"), mode=1),
    FeedConfiguration(name="1.00", ratio=Fraction("1"), mode=1),
    FeedConfiguration(name="1.25", ratio=Fraction("1.25"), mode=1),
    FeedConfiguration(name="1.50", ratio=Fraction("1.5"), mode=1),
    FeedConfiguration(name="1.75", ratio=Fraction("1.75"), mode=1),
    FeedConfiguration(name="2.00", ratio=Fraction("2"), mode=1),
    FeedConfiguration(name="2.50", ratio=Fraction("2.5"), mode=1),
    FeedConfiguration(name="3.00", ratio=Fraction("3"), mode=1),
    FeedConfiguration(name="3.50", ratio=Fraction("3.5"), mode=1),
    FeedConfiguration(name="4.00", ratio=Fraction("4"), mode=1),
]

THREAD_IN = [
    FeedConfiguration(name="64", ratio=Fraction("254/6400"), mode=2),
    FeedConfiguration(name="56", ratio=Fraction("254/5600"), mode=2),
    FeedConfiguration(name="48", ratio=Fraction("254/4800"), mode=2),
    FeedConfiguration(name="40", ratio=Fraction("254/4000"), mode=2),
    FeedConfiguration(name="32", ratio=Fraction("254/3200"), mode=2),
    FeedConfiguration(name="30", ratio=Fraction("254/3000"), mode=2),
    FeedConfiguration(name="24", ratio=Fraction("254/2400"), mode=2),
    FeedConfiguration(name="20", ratio=Fraction("254/2000"), mode=2),
    FeedConfiguration(name="18", ratio=Fraction("254/1800"), mode=2),
    FeedConfiguration(name="16", ratio=Fraction("254/1600"), mode=2),
    FeedConfiguration(name="14", ratio=Fraction("254/1400"), mode=2),
    FeedConfiguration(name="13", ratio=Fraction("254/1300"), mode=2),
    FeedConfiguration(name="12", ratio=Fraction("254/1200"), mode=2),
    FeedConfiguration(name="11", ratio=Fraction("254/1100"), mode=2),
    FeedConfiguration(name="10", ratio=Fraction("254/1000"), mode=2),
    FeedConfiguration(name="9", ratio=Fraction("254/900"), mode=2),
    FeedConfiguration(name="8", ratio=Fraction("254/800"), mode=2),
    FeedConfiguration(name="7", ratio=Fraction("254/700"), mode=2),
    FeedConfiguration(name="6", ratio=Fraction("254/600"), mode=2),
    FeedConfiguration(name="5", ratio=Fraction("254/500"), mode=2),
    FeedConfiguration(name="4", ratio=Fraction("254/400"), mode=2),
]

FEED_IN = [
    FeedConfiguration(name="0.001", ratio=Fraction("254/100") * Fraction("1/1000"), mode=3),
    FeedConfiguration(name="0.002", ratio=Fraction("254/100") * Fraction("2/1000"), mode=3),
    FeedConfiguration(name="0.003", ratio=Fraction("254/100") * Fraction("3/1000"), mode=3),
    FeedConfiguration(name="0.004", ratio=Fraction("254/100") * Fraction("4/1000"), mode=3),
    FeedConfiguration(name="0.005", ratio=Fraction("254/100") * Fraction("5/1000"), mode=3),
    FeedConfiguration(name="0.006", ratio=Fraction("254/100") * Fraction("6/1000"), mode=3),
    FeedConfiguration(name="0.008", ratio=Fraction("254/100") * Fraction("8/1000"), mode=3),
    FeedConfiguration(name="0.010", ratio=Fraction("254/100") * Fraction("10/1000"), mode=3),
    FeedConfiguration(name="0.012", ratio=Fraction("254/100") * Fraction("12/1000"), mode=3),
    FeedConfiguration(name="0.014", ratio=Fraction("254/100") * Fraction("14/1000"), mode=3),
    FeedConfiguration(name="0.016", ratio=Fraction("254/100") * Fraction("16/1000"), mode=3),
    FeedConfiguration(name="0.018", ratio=Fraction("254/100") * Fraction("18/1000"), mode=3),
    FeedConfiguration(name="0.020", ratio=Fraction("254/100") * Fraction("20/1000"), mode=3),
    FeedConfiguration(name="0.022", ratio=Fraction("254/100") * Fraction("22/1000"), mode=3),
    FeedConfiguration(name="0.024", ratio=Fraction("254/100") * Fraction("24/1000"), mode=3),
    FeedConfiguration(name="0.026", ratio=Fraction("254/100") * Fraction("26/1000"), mode=3),
    FeedConfiguration(name="0.028", ratio=Fraction("254/100") * Fraction("28/1000"), mode=3),
    FeedConfiguration(name="0.030", ratio=Fraction("254/100") * Fraction("30/1000"), mode=3),
    FeedConfiguration(name="0.035", ratio=Fraction("254/100") * Fraction("35/1000"), mode=3),
    FeedConfiguration(name="0.040", ratio=Fraction("254/100") * Fraction("40/1000"), mode=3),
]

table = {
    "Thread MM": THREAD_MM,
    "Thread IN": THREAD_IN,
    "Feed IN": FEED_IN,
}