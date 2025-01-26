from openai import OpenAI
from pydantic import BaseModel
import json

client = OpenAI()


class Alternative(BaseModel):
    text: str
    is_true: bool
    explanation: str


class Question(BaseModel):
    enunciate: str
    alternatives: list[Alternative]


completion = client.beta.chat.completions.parse(
    model="gpt-4o",
    store=True,
    messages=[
        {
            "role": "system",
            "content": "Você é uma IA que gera uma questão aos moldes do prompt para provas de faculdade.",
        },
        {
            "role": "user",
            "content": "Gere uma questão com 5 alternativas sobre hipercalemia",
        },
    ],
    response_format=Question,
)

try:
    # Parse the generated content
    question_content = json.loads(completion.choices[0].message.content)

    ## Save the question in a json file
    with open("question.json", "w", encoding="utf-8") as f:
        json.dump(question_content, f, ensure_ascii=False, indent=4)

except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")
    print("Raw content:", completion.choices[0].message.content)
