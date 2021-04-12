from .sanitize_html import (
    default_tag_acl,
    default_cleaner,
    clean_raw_html,
)

import unittest

RAW_HTML = """
<html>
<head></head>
<body>
  This is a test.
  <script type="not-a-hacker">alert("This javascript tag/type was allowed.");</script>
  <script type="also-not-a-hacker">alert("This javascript tag/type was allowed.");</script>
  <script type="a-hacker">alert("This javascript tag/type should not appear in cleaned output.");</script>
  <script type="unknown-hacker">alert("This javascript tag/type should not appear in cleaned output.");</script>
</body>
</html>
"""


class SanitizeHtml(unittest.TestCase, object):
    def test_default_tag_acl(self):
        tag_acl = default_tag_acl()
        self.assertFalse(tag_acl)
        self.assertEquals(len(tag_acl.keys()), 0)

    def test_complex_cleaner_tag_acl(self):
        tag_acl = {
            "script": [
                ("type", "not-a-hacker", "allow"),
                ("type", "also-not-a-hacker", "allow"),
                ("type", "a-hacker", "deny"),
            ],
        }
        cleaner = default_cleaner(tag_acl)
        clean_html = clean_raw_html(RAW_HTML, cleaner)

        self.assertIn("This is a test.", clean_html)
        self.assertIn(
            '<script type="not-a-hacker">alert("This javascript tag/type was allowed.");</script>',
            clean_html,
        )
        self.assertIn(
            '<script type="also-not-a-hacker">alert("This javascript tag/type was allowed.");</script>',
            clean_html,
        )
        self.assertNotIn(
            '<script type="a-hacker">alert("This javascript tag/type was allowed.");</script>',
            clean_html,
        )
        self.assertNotIn(
            '<script type="unknown-hacker">alert("This javascript tag/type was allowed.");</script>',
            clean_html,
        )
