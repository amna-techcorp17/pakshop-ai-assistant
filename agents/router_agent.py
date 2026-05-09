from agents.base_agent import BaseAgent
from langchain_core.messages import HumanMessage
import concurrent.futures


class RouterAgent(BaseAgent):

    def __init__(self):
        super().__init__()
        self.agent_name = "RouterAgent"

    def process(self, state: dict) -> dict:

        self.log(f"Routing query: {state['query']}")

        prompt = f"""You are a router.

Classify query:
- search
- general

Query: {state['query']}

Return only one word."""

        def call_llm():
            return self.llm.invoke(
                [HumanMessage(content=prompt)]
            )

        route = "search"  # default fallback

        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(call_llm)
                response = future.result(timeout=5)   # hard timeout

            route = response.content.strip().lower()

        except concurrent.futures.TimeoutError:
            self.log("Router timeout → fallback search")
            route = "search"

        except Exception as e:
            self.log(f"Router error: {str(e)}")
            route = "search"

        if route not in ["search", "general"]:
            route = "search"

        return {
            **state,
            "route": route
        }