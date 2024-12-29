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
    FeedConfiguration(name="64", ratio=Fraction("254/640"), mode=2),
    FeedConfiguration(name="56", ratio=Fraction("254/560"), mode=2),
    FeedConfiguration(name="48", ratio=Fraction("254/480"), mode=2),
    FeedConfiguration(name="40", ratio=Fraction("254/400"), mode=2),
    FeedConfiguration(name="32", ratio=Fraction("254/320"), mode=2),
    FeedConfiguration(name="30", ratio=Fraction("254/300"), mode=2),
    FeedConfiguration(name="24", ratio=Fraction("254/240"), mode=2),
    FeedConfiguration(name="20", ratio=Fraction("254/200"), mode=2),
    FeedConfiguration(name="18", ratio=Fraction("254/180"), mode=2),
    FeedConfiguration(name="16", ratio=Fraction("254/160"), mode=2),
    FeedConfiguration(name="14", ratio=Fraction("254/140"), mode=2),
    FeedConfiguration(name="13", ratio=Fraction("254/130"), mode=2),
    FeedConfiguration(name="12", ratio=Fraction("254/120"), mode=2),
    FeedConfiguration(name="11", ratio=Fraction("254/110"), mode=2),
    FeedConfiguration(name="10", ratio=Fraction("254/100"), mode=2),
    FeedConfiguration(name="9", ratio=Fraction("254/90"), mode=2),
    FeedConfiguration(name="8", ratio=Fraction("254/80"), mode=2),
    FeedConfiguration(name="7", ratio=Fraction("254/70"), mode=2),
    FeedConfiguration(name="6", ratio=Fraction("254/60"), mode=2),
    FeedConfiguration(name="5", ratio=Fraction("254/50"), mode=2),
    FeedConfiguration(name="4", ratio=Fraction("254/40"), mode=2),
]

FEED_IN = [
    FeedConfiguration(name="0.001", ratio=Fraction("254/10") * Fraction("1/1000"), mode=3),
    FeedConfiguration(name="0.002", ratio=Fraction("254/10") * Fraction("2/1000"), mode=3),
    FeedConfiguration(name="0.003", ratio=Fraction("254/10") * Fraction("3/1000"), mode=3),
    FeedConfiguration(name="0.004", ratio=Fraction("254/10") * Fraction("4/1000"), mode=3),
    FeedConfiguration(name="0.005", ratio=Fraction("254/10") * Fraction("5/1000"), mode=3),
    FeedConfiguration(name="0.006", ratio=Fraction("254/10") * Fraction("6/1000"), mode=3),
    FeedConfiguration(name="0.008", ratio=Fraction("254/10") * Fraction("8/1000"), mode=3),
    FeedConfiguration(name="0.010", ratio=Fraction("254/10") * Fraction("10/1000"), mode=3),
    FeedConfiguration(name="0.012", ratio=Fraction("254/10") * Fraction("12/1000"), mode=3),
    FeedConfiguration(name="0.014", ratio=Fraction("254/10") * Fraction("14/1000"), mode=3),
    FeedConfiguration(name="0.016", ratio=Fraction("254/10") * Fraction("16/1000"), mode=3),
    FeedConfiguration(name="0.018", ratio=Fraction("254/10") * Fraction("18/1000"), mode=3),
    FeedConfiguration(name="0.020", ratio=Fraction("254/10") * Fraction("20/1000"), mode=3),
    FeedConfiguration(name="0.022", ratio=Fraction("254/10") * Fraction("22/1000"), mode=3),
    FeedConfiguration(name="0.024", ratio=Fraction("254/10") * Fraction("24/1000"), mode=3),
    FeedConfiguration(name="0.026", ratio=Fraction("254/10") * Fraction("26/1000"), mode=3),
    FeedConfiguration(name="0.028", ratio=Fraction("254/10") * Fraction("28/1000"), mode=3),
    FeedConfiguration(name="0.030", ratio=Fraction("254/10") * Fraction("30/1000"), mode=3),
    FeedConfiguration(name="0.035", ratio=Fraction("254/10") * Fraction("35/1000"), mode=3),
    FeedConfiguration(name="0.040", ratio=Fraction("254/10") * Fraction("40/1000"), mode=3),
]

FEED_MM = [
    FeedConfiguration(name="0.01", ratio=Fraction("1/100"), mode=4),
    FeedConfiguration(name="0.02", ratio=Fraction("2/100"), mode=4),
    FeedConfiguration(name="0.03", ratio=Fraction("3/100"), mode=4),
    FeedConfiguration(name="0.04", ratio=Fraction("4/100"), mode=4),
    FeedConfiguration(name="0.05", ratio=Fraction("5/100"), mode=4),
    FeedConfiguration(name="0.06", ratio=Fraction("6/100"), mode=4),
    FeedConfiguration(name="0.07", ratio=Fraction("7/100"), mode=4),
    FeedConfiguration(name="0.08", ratio=Fraction("8/100"), mode=4),
    FeedConfiguration(name="0.09", ratio=Fraction("9/100"), mode=4),
    FeedConfiguration(name="0.10", ratio=Fraction("10/100"), mode=4),
    FeedConfiguration(name="0.12", ratio=Fraction("12/100"), mode=4),
    FeedConfiguration(name="0.14", ratio=Fraction("14/100"), mode=4),
    FeedConfiguration(name="0.16", ratio=Fraction("16/100"), mode=4),
    FeedConfiguration(name="0.18", ratio=Fraction("18/100"), mode=4),
    FeedConfiguration(name="0.20", ratio=Fraction("20/100"), mode=4),
    FeedConfiguration(name="0.22", ratio=Fraction("22/100"), mode=4),
    FeedConfiguration(name="0.24", ratio=Fraction("24/100"), mode=4),
    FeedConfiguration(name="0.26", ratio=Fraction("26/100"), mode=4),
    FeedConfiguration(name="0.28", ratio=Fraction("28/100"), mode=4),
    FeedConfiguration(name="0.30", ratio=Fraction("30/100"), mode=4),
]

table = {
    "Thread MM": THREAD_MM,
    "Thread IN": THREAD_IN,
    "Feed IN": FEED_IN,
    "Feed MM": FEED_MM,
}