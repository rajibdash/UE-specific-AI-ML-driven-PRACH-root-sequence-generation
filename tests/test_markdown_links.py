from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
import unittest


ROOT = Path(__file__).resolve().parents[1]
LINK_PATTERN = re.compile(r"(?<!)\[[^\]]*\]\(([^)]+)\)")


class MarkdownLinkTests(unittest.TestCase):
    def test_local_markdown_links_resolve(self):
        missing = []
        for markdown in ROOT.rglob("*.md"):
            if ".git" in markdown.parts:
                continue
            for target in LINK_PATTERN.findall(markdown.read_text(encoding="utf-8")):
                parsed = urlsplit(target.strip())
                if parsed.scheme or parsed.netloc:
                    continue
                relative_path = unquote(parsed.path)
                destination = (
                    markdown.parent / relative_path if relative_path else markdown
                )
                if not destination.exists():
                    missing.append(f"{markdown.relative_to(ROOT)} -> {target}")

        self.assertEqual(missing, [], "\n".join(missing))


if __name__ == "__main__":
    unittest.main()
