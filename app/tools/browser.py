import html
import re
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path
from typing import Any

from app.core.enums import ActionStatus, RiskLevel
from app.core.state import ActionResult
from .base import BaseTool


class OpenUrlTool(BaseTool):
    name = "open_url"
    description = "Open a URL in the system web browser."
    risk_level = RiskLevel.LOW
    parameters = {"url": "string"}

    def execute(self, url: str) -> ActionResult:
        try:
            success = webbrowser.open(url)
            return ActionResult(
                status=ActionStatus.SUCCESS if success else ActionStatus.FAILED,
                output={"url": url, "opened": success},
            )
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class BrowserSearchTool(BaseTool):
    name = "browser_search"
    description = "Perform a web search via default query engine."
    risk_level = RiskLevel.LOW
    parameters = {"query": "string"}

    def execute(self, query: str) -> ActionResult:
        try:
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://www.google.com/search?q={encoded_query}"
            webbrowser.open(search_url)
            return ActionResult(
                status=ActionStatus.SUCCESS,
                output={"query": query, "search_url": search_url},
            )
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class BrowserNavigateTool(BaseTool):
    name = "browser_navigate"
    description = "Navigate browser to a target location or URL."
    risk_level = RiskLevel.LOW
    parameters = {"url": "string"}

    def execute(self, url: str) -> ActionResult:
        return OpenUrlTool().execute(url=url)


class ExtractTextTool(BaseTool):
    name = "extract_text"
    description = "Fetch URL HTML content and extract visible text."
    risk_level = RiskLevel.LOW
    parameters = {"url": "string", "timeout": "integer (optional, default 15)"}

    def execute(self, url: str, timeout: int = 15) -> ActionResult:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw_html = resp.read().decode("utf-8", errors="ignore")

            text = re.sub(r"<script.*?>.*?</script>", "", raw_html, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r"<style.*?>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r"<[^>]+>", " ", text)
            clean_text = html.unescape(re.sub(r"\s+", " ", text)).strip()

            return ActionResult(
                status=ActionStatus.SUCCESS,
                output={"url": url, "text_length": len(clean_text), "snippet": clean_text[:1000]},
            )
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class ScreenshotTool(BaseTool):
    name = "take_screenshot"
    description = "Capture screen image (simulated or desktop image capture)."
    risk_level = RiskLevel.LOW
    parameters = {"output_path": "string (optional)"}

    def execute(self, output_path: str = "./workspace/screenshot.png") -> ActionResult:
        try:
            target = Path(output_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            # Dummy screenshot file output for baseline computer OS capability
            target.write_bytes(b"\x89PNG\r\n\x1a\n")
            return ActionResult(
                status=ActionStatus.SUCCESS,
                output={"path": str(target.resolve()), "captured": True},
            )
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class DownloadFileTool(BaseTool):
    name = "download_file"
    description = "Download a file from a URL to a local destination path."
    risk_level = RiskLevel.MEDIUM
    parameters = {"url": "string", "destination": "string"}

    def execute(self, url: str, destination: str) -> ActionResult:
        try:
            target = Path(destination)
            target.parent.mkdir(parents=True, exist_ok=True)
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            )
            with urllib.request.urlopen(req) as resp, open(target, "wb") as out_file:
                out_file.write(resp.read())

            return ActionResult(
                status=ActionStatus.SUCCESS,
                output={"url": url, "path": str(target.resolve()), "size": target.stat().st_size},
            )
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))
