from typing import Any
from .models import AgentRole, AgentStatus, WorkerAgentInfo


class AgentRegistry:
    """Manages worker agent registration, discovery, capabilities, and availability."""

    def __init__(self):
        self._agents: dict[str, WorkerAgentInfo] = {}
        self._register_default_agents()

    def register(self, agent: WorkerAgentInfo) -> None:
        self._agents[agent.id] = agent

    def get(self, agent_id: str) -> WorkerAgentInfo:
        if agent_id not in self._agents:
            raise KeyError(f"Worker Agent '{agent_id}' not found in registry.")
        return self._agents[agent_id]

    def list_agents(self) -> list[dict[str, Any]]:
        return [agent.model_dump() for agent in self._agents.values()]

    def find_agent_by_role(self, role: AgentRole) -> WorkerAgentInfo | None:
        for agent in self._agents.values():
            if agent.role == role:
                return agent
        return None

    def find_best_agent(self, required_capabilities: list[str], role_hint: AgentRole | None = None) -> WorkerAgentInfo | None:
        if role_hint:
            agent = self.find_agent_by_role(role_hint)
            if agent:
                return agent

        # Match by capabilities
        best_match = None
        highest_score = -1
        for agent in self._agents.values():
            score = sum(1 for cap in required_capabilities if cap in agent.capabilities)
            if score > highest_score:
                highest_score = score
                best_match = agent

        return best_match

    def _register_default_agents(self) -> None:
        default_workers = [
            WorkerAgentInfo(
                id="agent-research-01",
                name="ResearchAgent",
                role=AgentRole.RESEARCH,
                capabilities=["research", "web_search", "document_analysis", "read_file"],
                supported_tasks=["research_topics", "summarize_documents"],
                required_permissions=["filesystem.read", "browser.control"],
            ),
            WorkerAgentInfo(
                id="agent-coding-01",
                name="CodingAgent",
                role=AgentRole.CODING,
                capabilities=["python", "javascript", "create_directory", "write_file", "create_file", "execute_command"],
                supported_tasks=["generate_code", "create_project", "run_tests"],
                required_permissions=["filesystem.read", "filesystem.write", "terminal.execute"],
            ),
            WorkerAgentInfo(
                id="agent-computer-01",
                name="ComputerAgent",
                role=AgentRole.COMPUTER,
                capabilities=["mouse_click", "mouse_move", "keyboard_type", "screen_capture", "inspect_ui_tree", "window_action"],
                supported_tasks=["gui_automation", "desktop_interaction"],
                required_permissions=["screen.capture", "filesystem.read"],
            ),
            WorkerAgentInfo(
                id="agent-browser-01",
                name="BrowserAgent",
                role=AgentRole.BROWSER,
                capabilities=["open_url", "browser_search", "browser_navigate", "extract_text", "download_file"],
                supported_tasks=["web_navigation", "page_scraping"],
                required_permissions=["browser.control", "filesystem.write"],
            ),
            WorkerAgentInfo(
                id="agent-verification-01",
                name="VerificationAgent",
                role=AgentRole.VERIFICATION,
                capabilities=["verify_state", "get_metadata", "check_artifact"],
                supported_tasks=["verify_output", "validate_file"],
                required_permissions=["filesystem.read"],
            ),
        ]
        for worker in default_workers:
            self.register(worker)
