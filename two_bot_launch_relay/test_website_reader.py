
from src.two_bot_launch_relay.tools.custom_tool import (
    WebsiteReaderTool
)

tool = WebsiteReaderTool()

result = tool._run(
    "https://in.bookmyshow.com/explore/events-today-kolkata"
)

print(result)
