from typing import List, Dict
from dataclasses import dataclass
from typing import Tuple

from langchain.chat_models import ChatOpenAI

# from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.chains.base import Chain
from langchain.memory import ConversationTokenBufferMemory
from langchain.schema import BaseRetriever, Document, get_buffer_string

from .config import config
from .consts import CONDENSE_QUESTION_PROMPT, ANSWER_QUESTION_PROMPT, DEBUG
from .utils import log


def get_model():
    return ChatOpenAI(
        model=config["llm"]["name"], temperature=config["llm"]["temperature"]
    )


@dataclass
class QueryResult:
    question: str
    answer: str
    sources: List[Document]


class ChatChain(Chain):
    condense_chain: LLMChain
    answer_chain: LLMChain
    retriever: BaseRetriever

    @property
    def input_keys(self) -> List[str]:
        return ["chat_history", "question"]

    @property
    def output_keys(self) -> List[str]:
        return ["answer", "question", "source_documents"]

    def _call(self, inputs: Dict[str, str]) -> Dict[str, str]:
        chat_history = get_buffer_string(
            inputs["chat_history"], human_prefix="Human", ai_prefix="Assistant"
        )
        condensate_output = self.condense_chain.run(
            {
                "chat_history": chat_history,
                "question": inputs["question"],
            }
        )
        log("Condensated answer:", condensate_output)
        documents = self.retriever.get_relevant_documents(condensate_output)
        context = "---\n".join(
            [
                f"{document.page_content}\nSOURCE: {document.metadata['source']}\n"
                for document in documents
            ]
        )
        answer_output = self.answer_chain.run(
            {
                "context": context,
                "question": condensate_output,
            }
        )
        return {
            "answer": answer_output,
            "question": inputs["question"],
            "source_documents": documents,
        }


class Chat:
    def __init__(self, retriever: BaseRetriever):
        self.retriever = retriever
        self._create_chat()

    def _create_chat(self):
        model = get_model()

        self.chat_history = ConversationTokenBufferMemory(
            llm=model,
            max_token_limit=config["llm"]["chat_history"]["token_limit"],
            return_messages=True,
        )

        condense_chain = LLMChain(
            llm=model,
            prompt=CONDENSE_QUESTION_PROMPT,
            verbose=DEBUG,
        )
        answer_chain = LLMChain(
            llm=model,
            prompt=ANSWER_QUESTION_PROMPT,
            verbose=DEBUG,
        )

        self.chat = ChatChain(
            condense_chain=condense_chain,
            answer_chain=answer_chain,
            retriever=self.retriever,
        )

    def query(self, query: str) -> QueryResult:
        response = self.chat(
            {
                "question": query,
                "chat_history": self.chat_history.load_memory_variables({})["history"],
            }
            # {"question": query, "chat_history": ""}
        )
        self.chat_history.save_context(
            {"input": response["question"]}, {"output": response["answer"]}
        )
        return QueryResult(
            question=response["question"],
            answer=response["answer"],
            sources=response["source_documents"],
        )
