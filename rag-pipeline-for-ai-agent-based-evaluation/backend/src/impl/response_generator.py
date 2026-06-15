from typing import List
from interface.base_response_generator import BaseResponseGenerator
from util.invoke_ai import invoke_ai

SYSTEM_PROMPT = """
Use the provided context to give a concise, accurate answer to the user's question.
If you cannot find the answer in the context, say so clearly. Do not make up information.
"""


class ResponseGenerator(BaseResponseGenerator):
    def generate_response(self, query: str, context: List[str]) -> str:
        context_text = "\n\n".join(context)
        user_message = (
            f"<context>\n{context_text}\n</context>\n"
            f"<question>\n{query}\n</question>"
        )
        return invoke_ai(system_message=SYSTEM_PROMPT, user_message=user_message)
