
from typing import Type

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class WebsiteReaderInput(BaseModel):
    """Input schema for the website reader."""

    url: str = Field(
        description="The public webpage URL to retrieve."
    )


class WebsiteReaderTool(BaseTool):
    name: str = "Public Website Reader"
    description: str = (
        "Fetches a public webpage and extracts its readable text. "
        "Use this to inspect source material and verify claims. "
        "It does not bypass logins or access restrictions."
    )
    args_schema: Type[BaseModel] = WebsiteReaderInput

    def _run(self, url: str) -> str:
        try:
            response = requests.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0"
                },
                timeout=25
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            for element in soup(
                ["script", "style", "noscript", "svg"]
            ):
                element.decompose()

            text = soup.get_text(
                separator=" ",
                strip=True
            )

            if not text:
                return (
                    "No readable page content was extracted. "
                    "Do not invent information."
                )

            return (
                f"Source URL: {url}\n\n"
                f"Extracted page content:\n{text[:15000]}"
            )

        except requests.RequestException as error:
            return (
                f"Website retrieval failed: {error}. "
                "Mark unavailable information as Unknown."
            )

