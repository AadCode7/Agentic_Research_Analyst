from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.messages import get_buffer_string
from langgraph.types import Send

from schemas.models import InterviewState, SearchQuery
from prompt_lib.prompt_locator import (
    ANALYST_ASK_QUESTIONS,
    GENERATE_SEARCH_QUERY,
    GENERATE_ANSWERS,
    WRITE_SECTION
)
from logger import GLOBAL_LOGGER
from exception.custom_exception import ResearchAnalystException


class InterviewGraphBuilder:
    """
    A class responsible for constructing and managin the Interview graph workflow
    Handles:
    1.Analyst generating questions.
    2.Performing relevant web search.
    3.Expert generating Answers.
    4.Saving the interview transcript.
    5.Writing a summarized report section.
    """

    def __init__(self, llm, tavily_search):
        self.llm = llm
        self.tavily_search = tavily_search
        self.memory = MemorySaver()
        self.logger = GLOBAL_LOGGER.bind(module="InterviewGraphBuilder")

    def _generate_question(self, state: InterviewState):
        analyst = state["analyst"]
        messages = state["messages"]

        try:
            self.logger.info("Generating questions", analyst=analyst.name)
            system_prompt = ANALYST_ASK_QUESTIONS.render(goals = analyst.persona)
            question = self.llm.invoke([SystemMessage(content=system_prompt)] + messages)
            self.logger.info("Question generated successfully", question_preview = question.content[:200])

            return {"messages": [question]}
        
        except Exception as e:
            self.logger.error("Error generating question", error=str(e))
            raise ResearchAnalystException("Failed to generate question", e)
        
    def _search_web(self, state: InterviewState):
        try:
            self.logger.info("Generating search query from conversation")
            structure_llm = self.llm.with_structured_output(SearchQuery)
            search_prompt = GENERATE_SEARCH_QUERY.render()
            search_query = structure_llm.invoke([SystemMessage(content=search_prompt)] + state["messages"])

            self.logger.info("Performing Tavily Web Search", query = search_query.search_query)
            search_docs = self.tavily_search.invoke(search_query.search_query)

            if not search_docs:
                self.logger.warning("No results found for query", query = search_query.search_query)
                return {"context": ["[No context provided — answer generally using your expertise.]"]}
     
            formatted = "\n\n---\n\n".join(
                [
                    f'<Document href="{doc.get("url", "#")}"/>\n{doc.get("content", "")}\n</Document>'
                    for doc in search_docs
                ]
            )
            self.logger.info("Web search completed successfully", result_count = len(search_docs))
            return {"context": [formatted]}

        except Exception as e:  
            self.logger.error("Error searching web", error=str(e))
            raise ResearchAnalystException("Failed to search web", e)
        
    def _generate_answers(self, state: InterviewState):
        analyst = state["analyst"]
        messages = state["messages"]
        context = state.get("context", ["[No context available]"])

        try:
            self.logger.info("Generating expert answer", analyst=analyst.name)
            system_prompt = GENERATE_ANSWERS.render(goals=analyst.persona, context=context)
            answer = self.llm.invoke([SystemMessage(content=system_prompt)] + messages)
            answer.name = "expert"
            self.logger.info("Expert answer generated successfully", preview=answer.content[:200])
            return {"messages": [answer]}

        except Exception as e:
            self.logger.error("Error generating expert answer", error=str(e))
            raise ResearchAnalystException("Failed to generate expert answer", e)
            
    def _save_interview(self, state: InterviewState):
        try:
            messages = state["messages"]
            interview = get_buffer_string(messages)
            self.logger.info("Saving interview transcript", message_count = len(messages))

            return {"interview": interview}
        
        except Exception as e:
            self.logger.error("Error saving interview transcript", error=str(e))
            raise ResearchAnalystException("Failed to save interview transcript", e)
        

    def _write_section(self, state: InterviewState):
        """
        Write a concise report section based on the interview and gathered context.
        """
        context = state.get("context", ["[No context available.]"])
        analyst = state["analyst"]

        try:
            self.logger.info("Generating report section", analyst=analyst.name)
            system_prompt = WRITE_SECTION.render(focus=analyst.description)
            section = self.llm.invoke(
                [SystemMessage(content=system_prompt)]
                + [HumanMessage(content=f"Use this source to write your section: {context}")]
            )
            self.logger.info("Report section generated successfully", length=len(section.content))
            return {"sections": [section.content]}

        except Exception as e:
            self.logger.error("Error writing report section", error=str(e))
            raise ResearchAnalystException("Failed to generate report section", e)
        
    def build(self):
        try:
            self.logger.info("Building Interview Graph workflow")
            builder = StateGraph(InterviewState)

            builder.add_node("ask_question", self._generate_question)
            builder.add_node("search_web", self._search_web)
            builder.add_node("generate_answers", self._generate_answers)
            builder.add_node("save_interview", self._save_interview)
            builder.add_node("write_section", self._write_section)

            builder.add_edge(START, "ask_question")
            builder.add_edge("ask_question", "search_web")
            builder.add_edge("search_web", "generate_answers")
            builder.add_edge("generate_answers", "save_interview")
            builder.add_edge("save_interview", "write_section")
            builder.add_edge("write_section", END)

            graph = builder.compile(checkpointer=self.memory)
            self.logger.info("Interview Graph compiled successfully")
            return graph

        except Exception as e:
            self.logger.error("Error building interview graph", error=str(e))
            raise ResearchAnalystException("Failed to build interview graph workflow", e)

