import os
from dotenv import load_dotenv
from openai import OpenAI
import json
import re


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def ask_gpt(prompt):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a Spanish language teacher who explains concepts clearly."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


def ask_gpt_chat(prompt):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system",
             "content": "You are a Spanish language teacher who explains concepts in English and Spanish clearly."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


def generate_quiz(topic, num_questions):
    prompt = f"""
    Create a Spanish vocabulary quiz with {num_questions} multiple-choice questions on the topic '{topic}'.
    Format the response as a raw JSON list like and use English language to ask the question:
    [
      {{
        "question": "What is the Spanish word for 'apple'?",
        "options": ["pera", "naranja", "manzana", "uva"],
        "answer": "manzana"
      }},
      ...
    ]
    Do not add any explanation or formatting before or after the JSON array.
    """

    response = ask_gpt(prompt)

    # Optional: show raw response for debugging
    # st.code(response)

    try:
        # Try to directly load it first
        return json.loads(response)
    except json.JSONDecodeError:
        # Try extracting the JSON array manually if there's extra text
        match = re.search(r'\[\s*{.*?}\s*\]', response, re.DOTALL)
        if match:
            json_str = match.group(0)
            return json.loads(json_str)
        else:
            raise ValueError("Could not extract valid JSON quiz data from GPT response.")
