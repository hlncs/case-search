"""AI Agent service for autonomous reasoning and tool usage."""

import logging
import json
from typing import List, Dict, Optional, Tuple
from app.services.search_service import SearchService
from app.services.case_service import CaseService
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class Tool:
    """Represents an agent tool."""
    
    def __init__(self, name: str, description: str, func: callable):
        """Initialize tool.
        
        Args:
            name: Tool name
            description: Tool description for agent
            func: Callable function for tool
        """
        self.name = name
        self.description = description
        self.func = func


class AgentService:
    """Service for autonomous AI agent with tool usage."""
    
    def __init__(self, search_service: SearchService = None, 
                 case_service: CaseService = None,
                 llm_service: LLMService = None):
        """Initialize agent service.
        
        Args:
            search_service: Search service for tool use
            case_service: Case service for tool use
            llm_service: LLM service for reasoning
        """
        self.search_service = search_service or SearchService()
        self.case_service = case_service or CaseService()
        self.llm_service = llm_service or LLMService()
        self.max_iterations = 10
        self.search_chunk_limit = 50
        self.max_case_results = 5
        self.reasoning_trace = []
        self.tools = self._define_tools()
    
    def _define_tools(self) -> List[Tool]:
        """Define available tools for agent.
        
        Returns:
            List of available tools
        """
        return [
            Tool(
                name="search_cases",
                description="Search for legal cases using a query",
                func=self._tool_search_cases
            ),
            Tool(
                name="get_case_details",
                description="Get full details of a specific case",
                func=self._tool_get_case_details
            ),
            Tool(
                name="analyze_case",
                description="Analyze a case for specific aspects",
                func=self._tool_analyze_case
            ),
        ]
    
    def run(self, query: str) -> dict:
        """Run agent loop to answer query.
        
        Args:
            query: User query
            
        Returns:
            Agent response with reasoning trace
        """
        try:
            logger.info(f"Starting agent for query: {query}")
            self.reasoning_trace = []
            
            # Initialize agent state
            state = {
                "query": query,
                "step": 0,
                "completed": False,
                "answer": None,
                "sources": []
            }
            
            # Agent loop
            while state["step"] < self.max_iterations and not state["completed"]:
                state["step"] += 1
                logger.info(f"Agent step {state['step']}")
                
                # Ask LLM what to do next
                if self.llm_service.is_model_available():
                    tool_choice = self._decide_next_tool(state)
                else:
                    logger.warning("Configured Ollama model is not available; using search tool directly")
                    tool_choice = {"tool": "search_cases", "input": state["query"]}
                logger.info(f"Agent chose tool: {tool_choice['tool'] if tool_choice else 'FINISH'}")
                
                if not tool_choice:
                    # Agent decided to finish
                    state["completed"] = True
                    break
                
                # Execute chosen tool
                tool_result = self._execute_tool(tool_choice)
                
                # Log action and result
                self.reasoning_trace.append({
                    "step": state["step"],
                    "action": tool_choice["tool"],
                    "input": tool_choice.get("input", ""),
                    "result": tool_result
                })
                
                # Update state based on result
                if tool_choice["tool"] == "search_cases":
                    state["sources"].extend(tool_result.get("cases", []))
                    if tool_result.get("cases"):
                        state["completed"] = True
                
                logger.info(f"Tool result: {tool_result.get('status', 'unknown')}")
            
            # Generate final answer
            final_answer = self._synthesize_answer(state)
            
            return {
                "answer": final_answer,
                "reasoning_trace": self.reasoning_trace,
                "sources": state["sources"],
                "status": "completed" if state["completed"] else "interrupted",
                "steps": state["step"]
            }
        
        except Exception as e:
            logger.error(f"Agent error: {str(e)}")
            return {
                "answer": f"Agent encountered an error: {str(e)}",
                "reasoning_trace": self.reasoning_trace,
                "sources": [],
                "status": "error",
                "error": str(e)
            }
    
    def _decide_next_tool(self, state: dict) -> Optional[dict]:
        """Decide which tool to use next.
        
        Args:
            state: Current agent state
            
        Returns:
            Tool choice dict with tool name and input, or None to finish
        """
        # Create tool descriptions for LLM
        tools_desc = "\n".join([
            f"- {tool.name}: {tool.description}"
            for tool in self.tools
        ])
        
        prompt = f"""You are a legal research agent. Given this query, decide what to do next:

Query: {state['query']}

Available tools:
{tools_desc}

Available actions:
1. search_cases - Search for relevant cases
2. get_case_details - Get details of a specific case (need case_id)
3. analyze_case - Analyze aspects of a case (need case_id and aspect)
4. FINISH - If you have enough information to answer the query

What is your next action? Respond in JSON format:
{{"action": "tool_name", "input": "input_value"}}
Or respond {{"action": "FINISH"}} when done."""
        
        response = self.llm_service.generate(prompt)
        if not response.strip():
            return {
                "tool": "search_cases",
                "input": state["query"]
            }
        
        try:
            # Parse LLM response
            decision = json.loads(response)
            if decision.get("action") == "FINISH":
                return None
            
            return {
                "tool": decision.get("action"),
                "input": decision.get("input", "")
            }
        except:
            # Default to search if parsing fails
            return {
                "tool": "search_cases",
                "input": state["query"]
            }
    
    def _execute_tool(self, tool_choice: dict) -> dict:
        """Execute chosen tool.
        
        Args:
            tool_choice: Tool to execute with input
            
        Returns:
            Tool result
        """
        tool_name = tool_choice.get("tool")
        tool_input = tool_choice.get("input", "")
        
        matching_tool = next((t for t in self.tools if t.name == tool_name), None)
        if matching_tool:
            try:
                return matching_tool.func(tool_input)
            except Exception as e:
                logger.error(f"Tool {tool_name} error: {str(e)}")
                return {"status": "error", "error": str(e)}
        
        return {"status": "error", "error": f"Tool {tool_name} not found"}
    
    def _tool_search_cases(self, query: str) -> dict:
        """Tool: Search for cases."""
        try:
            results, total = self.search_service.search(query, limit=self.search_chunk_limit)

            # Aggregate chunk-level hits into unique document-level results.
            # This avoids repeated entries for the same case when multiple chunks match.
            aggregated: Dict[str, dict] = {}
            for result in results:
                case_id = str(result.case_id)
                if case_id not in aggregated:
                    aggregated[case_id] = {
                        "case_id": case_id,
                        "title": result.title,
                        "year": result.year,
                        "relevance": float(result.relevance_score),
                        "matched_chunks": 1,
                    }
                else:
                    aggregated[case_id]["relevance"] = max(
                        aggregated[case_id]["relevance"],
                        float(result.relevance_score),
                    )
                    aggregated[case_id]["matched_chunks"] += 1

            unique_cases = sorted(
                aggregated.values(),
                key=lambda case: (case["relevance"], case["matched_chunks"]),
                reverse=True,
            )[:self.max_case_results]

            return {
                "status": "success",
                "query": query,
                "cases": unique_cases,
                "total": total,
                "chunks_evaluated": len(results),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _tool_get_case_details(self, case_id: str) -> dict:
        """Tool: Get case details."""
        try:
            case = self.case_service.get_case(case_id)
            if not case:
                return {"status": "not_found", "case_id": case_id}
            return {
                "status": "success",
                "case_id": case_id,
                "title": case.title,
                "year": case.year,
                "decision": case.decision,
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _tool_analyze_case(self, input_str: str) -> dict:
        """Tool: Analyze case for specific aspect."""
        try:
            # Parse input (format: "case_id:aspect")
            parts = input_str.split(":")
            case_id = parts[0] if parts else ""
            aspect = parts[1] if len(parts) > 1 else "summary"
            
            return {
                "status": "success",
                "case_id": case_id,
                "aspect": aspect,
                "analysis": "Analysis would be performed by LLM here"
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _synthesize_answer(self, state: dict) -> str:
        """Synthesize final answer from agent state.
        
        Args:
            state: Final agent state
            
        Returns:
            Synthesized answer
        """
        if not self.reasoning_trace:
            return "No information gathered."
        
        sources = state.get("sources", [])
        if not sources:
            return "No relevant cases were found for this query."

        summary = f"Found {len(sources)} relevant case result(s) for: {state['query']}\n\n"
        for index, source in enumerate(sources[:5], 1):
            relevance = source.get("relevance", 0)
            matched_chunks = source.get("matched_chunks", 1)
            summary += (
                f"{index}. {source.get('title', 'Untitled')} ({source.get('year', 0)}) - "
                f"relevance {relevance:.1%} ({matched_chunks} matching chunk(s))\n"
            )

        llm_summary = self._generate_selected_case_summary(
            query=state.get("query", ""),
            selected_source=sources[0],
        )
        if llm_summary:
            summary += f"\n\nLLM Summary of Selected Case:\n{llm_summary}"

        return summary

    def _generate_selected_case_summary(self, query: str, selected_source: dict) -> str:
        """Generate an LLM summary for the highest-ranked selected case."""
        if not self.llm_service.is_model_available():
            return ""

        case_id = selected_source.get("case_id")
        if not case_id:
            return ""

        try:
            case = self.case_service.get_case(case_id)
        except Exception as exc:
            logger.warning("Could not retrieve selected case details for LLM summary: %s", str(exc))
            return ""

        if not case:
            return ""

        # Keep prompt bounded to avoid large generation latency.
        case_text_excerpt = (case.case_text or "")[:4000]
        prompt = f"""You are a legal analyst. Summarize the selected case for the user's query.

User query:
{query}

Selected case:
Title: {case.title}
Year: {case.year}
Court: {case.court}
Decision excerpt:
{case.decision}

Case text excerpt:
{case_text_excerpt}

Instructions:
- Provide 4-6 concise bullet points.
- Focus on why this case is relevant to the user's query.
- Mention key legal reasoning or outcome.
- Do not invent facts outside the provided text.
"""

        summary = self.llm_service.generate(prompt=prompt, temperature=0.2)
        return summary.strip()
