from agents.base_agent import BaseAgent
from langchain_core.messages import HumanMessage

class SearchAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "SearchAgent"
        self.platforms = {
            "daraz.pk": "https://www.daraz.pk/catalog/?q=",
            "telemart.pk": "https://telemart.pk/search?q=",
            "homeshopping.pk": "https://www.homeshopping.pk/search?q="
        }

    def process(self, state):
        self.log("Searching: " + state["query"])
        product = state["query"].split()[:3]
        product_name = "+".join(product)
        platform_links = {p: u + product_name for p, u in self.platforms.items()}
        platforms_str = ", ".join(self.platforms.keys())
        prompt = "Search for " + state["query"] + " on " + platforms_str + ". Find prices in PKR, availability, delivery. Format: PLATFORM: name\nPRODUCT: name\nPRICE: Rs. X\nAVAILABILITY: status\nDELIVERY: info\n---\nOnly real prices."
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return {
            **state,
            "search_results": response.content,
            "platforms_searched": list(self.platforms.keys()),
            "platform_links": platform_links
        }