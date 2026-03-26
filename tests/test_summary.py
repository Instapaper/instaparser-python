"""
Tests for Summary class.
"""

from instaparser.summary import Summary


class TestSummary:
    """Tests for Summary class."""

    def test_summary_initialization(self):
        """Test Summary initialization with key_sentences and overview."""
        key_sentences = [
            "First key sentence.",
            "Second key sentence.",
            "Third key sentence.",
        ]
        overview = "This is a comprehensive overview of the article."

        summary = Summary(key_sentences=key_sentences, overview=overview)

        assert summary.key_sentences == key_sentences
        assert summary.overview == overview

    def test_summary_with_empty_key_sentences(self):
        """Test Summary with empty key_sentences list."""
        summary = Summary(key_sentences=[], overview="Overview text")

        assert summary.key_sentences == []
        assert summary.overview == "Overview text"

    def test_summary_with_empty_overview(self):
        """Test Summary with empty overview."""
        summary = Summary(key_sentences=["Key sentence"], overview="")

        assert summary.key_sentences == ["Key sentence"]
        assert summary.overview == ""

    def test_summary_repr(self):
        """Test Summary __repr__ method."""
        summary = Summary(
            key_sentences=["Sentence 1", "Sentence 2"],
            overview="This is a test overview that is longer than 50 characters",
        )

        repr_str = repr(summary)
        assert "Summary" in repr_str
        assert "key_sentences=2" in repr_str
        # Should truncate overview to 50 chars
        assert len(repr_str) > 0

    def test_summary_str(self):
        """Test Summary __str__ method returns overview."""
        overview = "This is the overview text"
        summary = Summary(key_sentences=["Key sentence"], overview=overview)

        assert str(summary) == overview

    def test_summary_with_single_key_sentence(self):
        """Test Summary with a single key sentence."""
        summary = Summary(key_sentences=["Only one sentence"], overview="Overview")

        assert len(summary.key_sentences) == 1
        assert summary.key_sentences[0] == "Only one sentence"

    def test_summary_with_many_key_sentences(self):
        """Test Summary with many key sentences."""
        key_sentences = [f"Sentence {i}" for i in range(10)]
        summary = Summary(key_sentences=key_sentences, overview="Overview")

        assert len(summary.key_sentences) == 10
        assert summary.key_sentences[0] == "Sentence 0"
        assert summary.key_sentences[9] == "Sentence 9"

    def test_summary_with_very_long_overview(self):
        """Test Summary with very long overview."""
        long_overview = "This is a very long overview. " * 1000
        summary = Summary(key_sentences=["Key sentence"], overview=long_overview)

        assert len(summary.overview) > 10000
        assert summary.overview == long_overview

    def test_summary_with_very_long_key_sentences(self):
        """Test Summary with very long key sentences."""
        long_sentences = ["This is a very long key sentence. " * 100 for _ in range(5)]
        summary = Summary(key_sentences=long_sentences, overview="Overview")

        assert len(summary.key_sentences) == 5
        assert len(summary.key_sentences[0]) > 1000

    def test_summary_with_unicode_content(self):
        """Test Summary with Unicode content."""
        key_sentences = ["这是关键句子。", "これは重要な文です。", "이것은 중요한 문장입니다."]
        overview = "这是概述。これは概要です。이것은 개요입니다."

        summary = Summary(key_sentences=key_sentences, overview=overview)

        assert "关键句子" in summary.key_sentences[0]
        assert "重要な文" in summary.key_sentences[1]
        assert "중요한 문장" in summary.key_sentences[2]
        assert "概述" in summary.overview

    def test_summary_with_special_characters(self):
        """Test Summary with special characters."""
        key_sentences = ["Sentence with 'quotes' & \"double quotes\"", "Sentence with\nnewlines"]
        overview = "Overview with <tags> & special chars: @#$%"

        summary = Summary(key_sentences=key_sentences, overview=overview)

        assert "'quotes'" in summary.key_sentences[0]
        assert "\n" in summary.key_sentences[1]
        assert "<tags>" in summary.overview
        assert "@#$%" in summary.overview

    def test_summary_repr_with_short_overview(self):
        """Test Summary __repr__ with short overview."""
        summary = Summary(key_sentences=["Sentence 1"], overview="Short")

        repr_str = repr(summary)
        assert "Summary" in repr_str
        assert "key_sentences=1" in repr_str

    def test_summary_repr_with_exactly_50_char_overview(self):
        """Test Summary __repr__ with exactly 50 character overview."""
        overview = "A" * 50
        summary = Summary(key_sentences=["Sentence"], overview=overview)

        repr_str = repr(summary)
        assert "Summary" in repr_str

    def test_summary_with_whitespace_only_overview(self):
        """Test Summary with whitespace-only overview."""
        summary = Summary(key_sentences=["Sentence"], overview="   \n\t  ")

        assert summary.overview == "   \n\t  "
        assert str(summary) == "   \n\t  "

    def test_summary_with_whitespace_only_key_sentences(self):
        """Test Summary with whitespace-only key sentences."""
        key_sentences = ["   ", "\n", "\t"]
        summary = Summary(key_sentences=key_sentences, overview="Overview")

        assert len(summary.key_sentences) == 3
        assert summary.key_sentences[0] == "   "
