from agents.base_agent import BaseAgent
from langchain_core.messages import HumanMessage
import re


class SearchAgent(BaseAgent):

    def __init__(self):
        super().__init__()
        self.agent_name = "SearchAgent"

        # 🌍 PLATFORMS
        self.platforms = {
            "daraz.pk": "https://www.daraz.pk/",
            "telemart.pk": "https://telemart.pk/",
            "homeshopping.pk": "https://www.homeshopping.pk/"
        }

    # 🔥 CLEAN PRODUCT QUERY (ONLY PRODUCT NAME)
    def clean_query(self, query: str) -> str:

        query = query.lower()

        stop_words = [
            "i want", "please", "show me", "i need", "can you find",
            "for me", "looking for", "buy", "get", "give me",
            "find", "search", "cheap", "price", "prices",
            "under", "best", "top", "affordable", "budget",
            "cost", "rs", "rupees", "in pakistan", "pakistan", "online"
        ]

        for word in stop_words:
            query = query.replace(word, "")

        # remove numbers
        query = re.sub(r"\d+", "", query)

        # remove special chars
        query = re.sub(r"[^\w\s]", "", query)

        # clean spaces
        query = " ".join(query.split())

        return query.strip()

    def process(self, state):

        self.log("Searching: " + state["query"])

        # 🔥 CLEAN PRODUCT ONLY
        cleaned_query = self.clean_query(state["query"])

        if not cleaned_query:
            cleaned_query = state["query"]

        keywords = cleaned_query.split()

        product_name = "+".join(keywords)

        # 🌍 ONLY OPEN WEBSITE (NO SEARCH PREFILL)
        platform_links = {
            platform: base_url
            for platform, base_url in self.platforms.items()
        }

        prompt = f"""
Search product: {cleaned_query}

Check availability on:
- Daraz
- Telemart
- HomeShopping

Return:
- product info
- availability
- delivery time
- estimated price (PKR)
"""

        response = self.llm.invoke(
            [HumanMessage(content=prompt)]
        )

        return {
            **state,
            "search_results": response.content,
            "cleaned_query": cleaned_query,
            "platforms_searched": list(self.platforms.keys()),
            "platform_links": platform_links
        }