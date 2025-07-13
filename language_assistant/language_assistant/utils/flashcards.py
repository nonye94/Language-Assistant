from utils.gpt_module import ask_gpt
import json


def generate_flashcards(topic, batch_size=20, max_batches=5):
    all_cards = []

    for batch in range(max_batches):
        prompt = (
            f"Create {batch_size} unique Spanish flashcards on the topic '{topic}'. "
            "Each should include: Word, English Meaning, and Usage in a sentence. "
            "Return as JSON: [{\"word\": \"...\", \"meaning\": \"...\", \"example\": \"...\"}]"
        )

        raw_output = ask_gpt(prompt)
        try:
            cards = json.loads(raw_output)
            cards = [c for c in cards if all(k in c and c[k].strip() for k in ('word', 'meaning', 'example'))]
            all_cards.extend(cards)
        except Exception as e:
            print(f"Batch {batch + 1} failed:", e)
            break  # Stop if something goes wrong

    return all_cards
