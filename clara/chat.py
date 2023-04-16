from typing import List, Dict
from dataclasses import dataclass
from typing import Tuple, Iterable, Optional

from langchain.chat_models import ChatOpenAI

# from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.chains.base import Chain
from langchain.schema import BaseRetriever, Document

from .config import config
from .consts import CONDENSE_QUESTION_PROMPT, ANSWER_QUESTION_PROMPT
# from .console import console


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
        # console.log(inputs["chat_history"])
        chat_history = "\n\n".join(
            [
                f"Human: {line[0]}\n\nAssistant: {line[-1]}"
                for line in inputs["chat_history"]
            ]
        )
        condensate_output = self.condense_chain.run(
            {
                "chat_history": chat_history,
                "question": inputs["question"],
            }
        )
        # console.log("Condensated answer:", condensate_output)
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


class ChatHistory:
    def __init__(self, length_limit: int = 3500):
        self.history = []
        self.length_limit = length_limit

    def append(self, messages: Tuple[str, str]):
        def get_total_length(messages: Iterable[str]) -> int:
            return sum(len(message) for message in messages)

        total_length = sum([get_total_length(message) for message in messages])
        new_history = [messages]

        for line in reversed(self.history):
            line_length = get_total_length(line)

            if total_length + line_length < self.length_limit:
                new_history.insert(0, line)
                total_length += line_length

            else:
                break

        self.history = new_history


class Chat:
    def __init__(self, retriever: BaseRetriever):
        self.retriever = retriever
        self.chat_history = ChatHistory()

        self._create_chat()

    def _create_chat(self):
        model = get_model()

        condense_chain = LLMChain(
            llm=model,
            prompt=CONDENSE_QUESTION_PROMPT,
        )
        answer_chain = LLMChain(
            llm=model,
            prompt=ANSWER_QUESTION_PROMPT,
        )

        self.chat = ChatChain(
            condense_chain=condense_chain,
            answer_chain=answer_chain,
            retriever=self.retriever,
        )

    def query(self, query: str) -> QueryResult:
        response = self.chat(
            {"question": query, "chat_history": self.chat_history.history}
            # {"question": query, "chat_history": ""}
        )
        # console.log(response)
        self.chat_history.append((response["question"], response["answer"]))
        return QueryResult(
            question=response["question"],
            answer=response["answer"],
            sources=response["source_documents"],
        )
