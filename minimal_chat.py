from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:8080/v1",
    api_key="not-needed",
    timeout=300.0,
)

response = client.chat.completions.create(
    model="qwen3.5-4b",
    messages=[
        {
            "role": "system",
            "content": (
                "Ты преобразуешь неструктурированные данные "
                "в строго структурированный результат."
            ),
        },
        {
            "role": "user",
            "content": (
                "Преобразуй запись в JSON: "
                "дата 15.07.2026, артикул A-17, сумма 1 250,50 руб."
            ),
        },
    ],
    temperature=0.1,
    max_tokens=256,
)

text = response.choices[0].message.content

if text is None:
    raise RuntimeError("Модель вернула пустой ответ")

print(text)