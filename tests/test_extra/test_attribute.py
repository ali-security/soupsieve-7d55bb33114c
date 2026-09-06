"""Test attribute selectors."""
import time
from .. import util
import soupsieve as sv


class TestAttribute(util.TestCase):
    """Test attribute selectors."""

    MARKUP = """
    <div id="div">
    <p id="0">Some text <span id="1"> in a paragraph</span>.</p>
    <a id="2" href="http://google.com">Link</a>
    <span id="3">Direct child</span>
    <pre id="pre">
    <span id="4">Child 1</span>
    <span id="5">Child 2</span>
    <span id="6">Child 3</span>
    </pre>
    </div>
    """

    def test_attribute_not_equal_no_quotes(self):
        """Test attribute with value that does not equal specified value (no quotes)."""

        # No quotes
        self.assert_selector(
            self.MARKUP,
            'body [id!=\\35]',
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_attribute_not_equal_quotes(self):
        """Test attribute with value that does not equal specified value (quotes)."""

        # Quotes
        self.assert_selector(
            self.MARKUP,
            "body [id!='5']",
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_attribute_not_equal_double_quotes(self):
        """Test attribute with value that does not equal specified value (double quotes)."""

        # Double quotes
        self.assert_selector(
            self.MARKUP,
            'body [id!="5"]',
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_bad_attribute_unclused(self):
        """Test bad attribute fails for syntax error, not timeout error."""

        # An unterminated attribute value used to send the value pattern into
        # catastrophic backtracking, so rejecting the selector took exponential
        # time instead of failing immediately. Each of these must raise a syntax
        # error right away. The threshold is deliberately generous so that a slow
        # or loaded CI machine cannot make this flaky, while the exponential
        # behavior (many seconds for a mere 300 characters, and doubling for each
        # additional character) still fails loudly if it ever comes back.
        # `time.perf_counter` is used instead of `signal.alarm` so the test also
        # runs on Windows, where `SIGALRM` does not exist.
        patterns = (
            '[a="' + ('x' * 300),
            "[a='" + ('x' * 300),
            '[a=' + ('x' * 300)
        )

        for pattern in patterns:
            start = time.perf_counter()
            with self.assertRaises(sv.SelectorSyntaxError):
                sv.compile(pattern)
            elapsed = time.perf_counter() - start
            self.assertLess(
                elapsed,
                5,
                'Compiling {!r} took {} seconds, expected an immediate syntax error'.format(pattern, elapsed)
            )
