from fractions import Fraction

import pytest

from rcp.feeds import FeedConfiguration, THREAD_MM, THREAD_IN, FEED_IN, FEED_MM, table


class TestFeedConfiguration:
    def test_has_required_fields(self):
        fc = FeedConfiguration(name="1.00", ratio=Fraction(1), mode=1)
        assert fc.name == "1.00"
        assert fc.ratio == Fraction(1)
        assert fc.mode == 1

    def test_optional_fields_default_none(self):
        fc = FeedConfiguration()
        assert fc.name is None
        assert fc.ratio is None
        assert fc.mode is None


class TestThreadMM:
    def test_not_empty(self):
        assert len(THREAD_MM) > 0

    def test_all_have_ratios(self):
        for fc in THREAD_MM:
            assert fc.ratio is not None
            assert isinstance(fc.ratio, Fraction)

    def test_all_mode_1(self):
        for fc in THREAD_MM:
            assert fc.mode == 1

    def test_ratios_are_positive(self):
        for fc in THREAD_MM:
            assert fc.ratio > 0

    def test_sorted_ascending(self):
        ratios = [fc.ratio for fc in THREAD_MM]
        assert ratios == sorted(ratios)

    def test_known_values(self):
        names = [fc.name for fc in THREAD_MM]
        assert "1.00" in names
        assert "0.50" in names
        assert "2.00" in names


class TestThreadIN:
    def test_not_empty(self):
        assert len(THREAD_IN) > 0

    def test_all_have_ratios(self):
        for fc in THREAD_IN:
            assert fc.ratio is not None
            assert isinstance(fc.ratio, Fraction)

    def test_all_mode_2(self):
        for fc in THREAD_IN:
            assert fc.mode == 2

    def test_ratios_are_positive(self):
        for fc in THREAD_IN:
            assert fc.ratio > 0

    def test_ratio_formula_correct(self):
        """Imperial threads use 254/(TPI*10) formula."""
        # 20 TPI: ratio = 254/200 = 127/100
        fc_20 = [fc for fc in THREAD_IN if fc.name == "20"][0]
        assert fc_20.ratio == Fraction(254, 200)

    def test_higher_tpi_has_smaller_ratio(self):
        """Higher TPI = finer thread = smaller pitch ratio."""
        fc_20 = [fc for fc in THREAD_IN if fc.name == "20"][0]
        fc_10 = [fc for fc in THREAD_IN if fc.name == "10"][0]
        assert fc_20.ratio < fc_10.ratio


class TestFeedIN:
    def test_not_empty(self):
        assert len(FEED_IN) > 0

    def test_all_mode_3(self):
        for fc in FEED_IN:
            assert fc.mode == 3

    def test_ratios_are_positive(self):
        for fc in FEED_IN:
            assert fc.ratio > 0

    def test_sorted_ascending(self):
        ratios = [fc.ratio for fc in FEED_IN]
        assert ratios == sorted(ratios)


class TestFeedMM:
    def test_not_empty(self):
        assert len(FEED_MM) > 0

    def test_all_mode_4(self):
        for fc in FEED_MM:
            assert fc.mode == 4

    def test_ratios_are_positive(self):
        for fc in FEED_MM:
            assert fc.ratio > 0

    def test_sorted_ascending(self):
        ratios = [fc.ratio for fc in FEED_MM]
        assert ratios == sorted(ratios)

    def test_ratio_matches_name(self):
        """MM feed ratios should equal the name as a fraction."""
        for fc in FEED_MM:
            assert fc.ratio == Fraction(fc.name)


class TestTable:
    def test_has_four_entries(self):
        assert len(table) == 4

    def test_expected_keys(self):
        assert set(table.keys()) == {"Thread MM", "Thread IN", "Feed IN", "Feed MM"}

    def test_values_are_lists(self):
        for key, value in table.items():
            assert isinstance(value, list)
            assert len(value) > 0

    def test_all_entries_are_feed_configurations(self):
        for key, entries in table.items():
            for fc in entries:
                assert isinstance(fc, FeedConfiguration)
