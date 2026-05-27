from collections import Counter

from tuitris.bag import SevenBag
from tuitris.tetromino import PIECE_TYPES


def test_bag_returns_all_seven_pieces_in_one_cycle():
    bag = SevenBag(seed=42)
    drawn = [bag.next() for _ in range(7)]
    assert Counter(drawn) == Counter(PIECE_TYPES)


def test_bag_refills_after_exhaustion():
    bag = SevenBag(seed=42)
    drawn = [bag.next() for _ in range(14)]
    assert Counter(drawn[:7]) == Counter(PIECE_TYPES)
    assert Counter(drawn[7:]) == Counter(PIECE_TYPES)


def test_bag_peek_does_not_consume():
    bag = SevenBag(seed=42)
    peeked = bag.peek()
    assert bag.next() == peeked


def test_bag_is_deterministic_with_seed():
    bag1 = SevenBag(seed=7)
    bag2 = SevenBag(seed=7)
    seq1 = [bag1.next() for _ in range(14)]
    seq2 = [bag2.next() for _ in range(14)]
    assert seq1 == seq2
