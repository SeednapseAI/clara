from typing import List, Dict

from langchain.chat_models import ChatOpenAI

# from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.chains.base import Chain
from langchain.schema import BaseRetriever

from .config import config
from .consts import CONDENSE_QUESTION_PROMPT, ANSWER_QUESTION_PROMPT
# from .console import console


def get_model():
    return ChatOpenAI(
        model=config["llm"]["name"], temperature=config["llm"]["temperature"]
    )


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
        context = "---\n".join([
            f"{document.page_content}\nSOURCE: {document.metadata['source']}\n"
            for document in documents])
        answer_output = self.answer_chain.run(
            {
                "context": context,
                "question": condensate_output,
                # "question": inputs["question"],
            }
        )
        return {
            "answer": answer_output,
            "question": inputs["question"],
            "source_documents": documents,
        }


def create_chat(retriever: BaseRetriever):
    model = get_model()

    condense_chain = LLMChain(
        llm=model,
        prompt=CONDENSE_QUESTION_PROMPT,
    )
    answer_chain = LLMChain(
        llm=model,
        prompt=ANSWER_QUESTION_PROMPT,
    )

    return ChatChain(
        condense_chain=condense_chain, answer_chain=answer_chain, retriever=retriever
    )
