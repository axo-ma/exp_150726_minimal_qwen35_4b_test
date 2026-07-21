Чтобы увидеть **именно итоговый запрос OpenWebUI → Ollama**, включая системный промпт, историю диалога, параметры модели и вставленный RAG-контекст, перехватывать запрос нужно **между OpenWebUI и Ollama**.

DevTools браузера для этого недостаточно: там виден запрос **браузер → OpenWebUI**, а OpenWebUI после этого может добавить системные инструкции, найденные фрагменты файлов и преобразовать формат запроса.

## Надёжный способ: поставить прозрачный прокси перед Ollama

В вашей схеме:

```
OpenWebUI в Docker
        ↓
mitmweb :11435
        ↓
Ollama :11434
```

### 1\. Запустите mitmweb

В PowerShell:

```
docker run -it `
  --name ollama-proxy `
  -p 11435:8080 `
  -p 8081:8081 `
  mitmproxy/mitmproxy `
  mitmweb `
  --listen-host 0.0.0.0 `
  --listen-port 8080 `
  --web-host 0.0.0.0 `
  --web-port 8081 `
  --set web_password=1 `
  --mode reverse:http://host.docker.internal:11434 `
  --set block_global=false
```

Окно не закрывайте.

### 2\. Перенаправьте OpenWebUI на прокси

В OpenWebUI откройте:

```
Admin Panel
→ Settings
→ Connections
→ Ollama
```

Вместо:

```
http://host.docker.internal:11434
```

укажите:

```
http://host.docker.internal:11435
```

Сохраните настройки.

### 3\. Откройте интерфейс перехватчика

В браузере:

```
http://localhost:8081/?token=1
```

Теперь отправьте сообщение в OpenWebUI.

В mitmweb появится запрос примерно такого вида:

```
POST /api/chat
```

Ollama официально использует `POST /api/chat` для диалоговых запросов; тело содержит модель, массив `messages` и дополнительные параметры.

Нажмите на запрос и откройте:

```
Request → Content
```

Там будет итоговый JSON, например:

```
{
  "model": "qwen3:4b",
  "messages": [
    {
      "role": "system",
      "content": "..."
    },
    {
      "role": "user",
      "content": "..."
    },
    {
      "role": "assistant",
      "content": "..."
    },
    {
      "role": "user",
      "content": "Ваш новый вопрос..."
    }
  ],
  "stream": true,
  "options": {
    "temperature": 0.6,
    "num_ctx": 8192
  }
}
```

Если использовались Excel-файлы и RAG, ищите внутри `messages`:

* текст извлечённых фрагментов;
* названия или метаданные файлов;
* конструкции вроде `Sources`, `Context`, `<source>`;
* системные инструкции OpenWebUI;
* ваш исходный вопрос.

Именно этот JSON Ollama получает до применения шаблона модели.

## Важное различие

Есть три разных уровня:

```
1. Браузер → OpenWebUI
   Ваш вопрос, chat_id, настройки интерфейса, ссылки на файлы.

2. OpenWebUI → Ollama
   Уже подготовленный messages JSON:
   system prompt + история + RAG + текущий вопрос.

3. Ollama → модель
   Единая строка после применения chat template:
   <|im_start|>system ...
   <|im_start|>user ...
```

Перехват через mitmweb показывает **уровень 2** — то, что вы сейчас хотите увидеть.

Он ещё не показывает окончательную строку после применения `chat_template`: её формирует уже Ollama перед передачей модели. OpenWebUI может работать с Ollama через его нативный API, а локальный Ollama API по умолчанию доступен на <http://localhost:11434/api>.

После эксперимента верните в OpenWebUI адрес:

```
http://host.docker.internal:11434
```

и остановите mitmweb сочетанием `Ctrl+C`.