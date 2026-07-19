"""
Answer Generator.

Connects RAG context with
local Ollama models.


Responsibilities:

- Build final prompt
- Call Qwen3-VL
- Control hallucination
- Return grounded answers


Model:

qwen3-vl:4b


Author:
    Your Name
"""

from __future__ import annotations


from dataclasses import dataclass


import requests


from core.logger import logger



@dataclass(slots=True)
class GeneratedAnswer:
    """
    Final AI response.
    """

    answer: str

    model: str

    grounded: bool



class AnswerGenerator:
    """
    RAG answer generation engine.
    """

    def __init__(
        self,

        model_name: str =
        "qwen3-vl:4b",

        ollama_url: str =
        "http://localhost:11434/api/generate",

    ):

        self.model_name = model_name


        self.ollama_url = ollama_url


        logger.info(

            "Answer generator initialized"

        )



    def build_prompt(
        self,

        question: str,

        context: str,

    ) -> str:
        """
        Create grounded prompt.
        """


        prompt = f"""

You are an enterprise document intelligence assistant.


Your task:

Answer the user's question using ONLY
the provided document evidence.


Rules:

- Never invent information.
- If evidence is insufficient,
  say "Information not found in document."
- Always mention page/document sources
  when available.
- Keep technical values exact.


DOCUMENT EVIDENCE:

{context}


USER QUESTION:

{question}


ANSWER:

"""


        return prompt



    def generate(
        self,

        question: str,

        context: str,

    ) -> GeneratedAnswer:
        """
        Generate final answer.
        """

        prompt = self.build_prompt(

            question,

            context

        )


        payload = {

            "model":
            self.model_name,


            "prompt":
            prompt,


            "stream":
            False,


            "options":

            {

                "temperature":
                0.1

            }

        }



        response = requests.post(

            self.ollama_url,

            json=payload,

            timeout=300

        )



        response.raise_for_status()



        result = response.json()



        return GeneratedAnswer(

            answer=
            result["response"],


            model=
            self.model_name,


            grounded=True

        )