
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, task
from crewai.agents.agent_builder.base_agent import BaseAgent


@CrewBase
class TwoBotLaunchRelay:
    """Two specialist bots for the Launch Relay challenge."""

    agents: list[BaseAgent]
    tasks: list[Task]

    def _local_llm(self):
        """Configure the local Qwen model through Ollama."""
        return LLM(
            model="ollama_chat/qwen3.5:2b",
            base_url="http://localhost:11434",
            temperature=0.2,
            max_tokens=2048,
            reasoning_effort="none",
        )

    # -------------------------------
    # AGENTS
    # -------------------------------

    @agent
    def source_editor(self) -> Agent:
        return Agent(
            config=self.agents_config["source_editor"],
            llm=self._local_llm(),
            verbose=True,
        )

    @agent
    def launch_producer(self) -> Agent:
        return Agent(
            config=self.agents_config["launch_producer"],
            llm=self._local_llm(),
            verbose=True,
        )

    # -------------------------------
    # TASKS
    # -------------------------------

    @task
    def source_research_task(self) -> Task:
        return Task(
            config=self.tasks_config["source_research_task"],
        )

    @task
    def launch_production_task(self) -> Task:
        return Task(
            config=self.tasks_config["launch_production_task"],
        )

    @task
    def quality_assurance_task(self) -> Task:
        return Task(
            config=self.tasks_config["quality_assurance_task"],
        )

    # -------------------------------
    # PRODUCER CREW
    # -------------------------------

    def producer_crew(self) -> Crew:
        """Run the Launch Producer after human approval."""
        return Crew(
            agents=[self.launch_producer()],
            tasks=[self.launch_production_task()],
            process=Process.sequential,
            verbose=True,
        )

    # -------------------------------
    # QA CREW
    # -------------------------------

    def qa_crew(self) -> Crew:
        """Return the work to the Source Editor for QA."""
        return Crew(
            agents=[self.source_editor()],
            tasks=[self.quality_assurance_task()],
            process=Process.sequential,
            verbose=True,
        )
