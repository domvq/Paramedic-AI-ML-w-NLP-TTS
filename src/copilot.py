import os

import ollama


OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "paramedic-ai:latest",
)


SYSTEM_PROMPT = """
You are Paramedic AI, an EMS education and
decision-support assistant.

Use the retrieved reference material when relevant.

Important rules:

1. Do not invent EMS protocol information.
2. Do not invent medication doses.
3. Do not present educational references as current
   local EMS protocols.
4. Clearly identify uncertainty when the source
   material is incomplete or has unknown jurisdiction,
   version, or effective date.
5. Current local EMS protocols, medical direction,
   scope of practice, manufacturer instructions,
   and applicable law take precedence.
6. This application is for education and demonstration,
   not diagnosis or treatment.
"""


def build_messages(
    messages,
    context="",
):

    system_prompt = SYSTEM_PROMPT

    if context:

        system_prompt += f"""

RETRIEVED LOCAL KNOWLEDGE:

{context}

Treat this material as reference information.
Pay attention to jurisdiction, document type,
status, version, and effective date.
"""

    return [
        {
            "role": "system",
            "content": system_prompt,
        }
    ] + messages


def chat(
    messages,
    context="",
):

    model_messages = build_messages(
        messages=messages,
        context=context,
    )

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=model_messages,
    )

    return response["message"]["content"]
