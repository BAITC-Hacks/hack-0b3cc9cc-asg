"""FAQ-бот на 5 вопросов. Отвечает по совпадению ключевых слов, RAG не нужен."""
import re
import sys

FAQ_PATH = "faq.txt"

STOPWORDS = {
    "и", "в", "во", "на", "с", "со", "по", "для", "как", "что", "это",
    "какие", "какой", "какая", "какое", "мне", "я", "ты", "вы", "они",
    "он", "она", "есть", "до", "от", "за", "к", "о", "об", "а", "но",
    "или", "у", "из", "же", "ли", "бы", "то", "там", "тут", "вот",
}


def tokenize(text):
    words = re.findall(r"[а-яёa-z0-9]+", text.lower())
    tokens = {w for w in words if w not in STOPWORDS}
    return tokens or set(words)


def load_faq(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    pairs = []
    question, answer = None, None
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("Q:"):
            question = line[2:].strip()
        elif line.startswith("A:"):
            answer = line[2:].strip()
            if question and answer:
                pairs.append((question, answer, tokenize(question)))
            question, answer = None, None
    return pairs


def find_answer(user_question, faq):
    query_tokens = tokenize(user_question)
    if not query_tokens:
        return None

    best_score = 0
    best_answer = None
    for question, answer, tokens in faq:
        score = len(query_tokens & tokens)
        if score > best_score:
            best_score = score
            best_answer = answer

    if best_score == 0:
        return None
    return best_answer


def main():
    for stream in (sys.stdout, sys.stdin):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    try:
        faq = load_faq(FAQ_PATH)
    except FileNotFoundError:
        print(f"Не найден файл {FAQ_PATH}")
        sys.exit(1)

    print("FAQ-бот готов. Задайте вопрос (или 'выход' для завершения).")
    while True:
        try:
            user_question = input("Вопрос: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_question:
            continue
        if user_question.lower() in {"выход", "exit", "quit"}:
            break

        answer = find_answer(user_question, faq)
        print(answer if answer else "не знаю")


if __name__ == "__main__":
    main()
