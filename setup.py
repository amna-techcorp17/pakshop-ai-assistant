def w(path, content):
    with open(path, 'wb') as f:
        f.write(content.encode('utf-8'))
    print(f"Fixed: {path}")

w("agents/search_agent.py", """from agents.base_agent import BaseAgent
from langchain_core.messages import HumanMessage

class SearchAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "SearchAgent"
        self.platforms = {
            "daraz.pk": "https://www.daraz.pk/catalog/?q=",
            "telemart.pk": "https://telemart.pk/search?q=",
            "homeshopping.pk": "https://www.homeshopping.pk/search?q=",
            "ishopping.pk": "https://www.ishopping.pk/search?q=",
            "symbios.pk": "https://www.symbios.pk/search?q="
        }

    def extract_product_name(self, query: str) -> str:
        prompt = f\\\"\\\"\\\"Extract ONLY the product name from this query.
Return just 2-4 words maximum, nothing else.
Examples:
- iPhone 13 ki price kya hai? -> iPhone 13
- Headphones compare karo platforms pe -> headphones
Query: {query}
Product name:\\\"\\\"\\\"
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip().replace(' ', '+')

    def process(self, state: dict) -> dict:
        self.log(f"Searching for: {state['query']}")
        product_name = self.extract_product_name(state['query'])
        platform_links = {
            platform: base_url + product_name
            for platform, base_url in self.platforms.items()
        }
        platforms_str = ", ".join(self.platforms.keys())
        prompt = f\\\"\\\"\\\"You are a real-time shopping search agent for Pakistani e-commerce platforms.
Search for this query on these platforms: {platforms_str}
User Query: {state['query']}
Find prices in PKR, availability, delivery info.
Format for each platform:
PLATFORM: [name]
PRODUCT: [name]
PRICE: Rs. [price]
AVAILABILITY: [In Stock/Out of Stock]
DELIVERY: [info]
---
Only report real prices. Skip platforms where not found.\\\"\\\"\\\"
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return {
            **state,
            "search_results": response.content,
            "platforms_searched": list(self.platforms.keys()),
            "platform_links": platform_links
        }
""")
print("Done!")