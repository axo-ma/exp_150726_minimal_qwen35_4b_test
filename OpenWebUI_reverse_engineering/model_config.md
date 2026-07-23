
---
### Создать ModelFile


Перейти в папку models

```
cd ./models
```

Создать файл тесктовый файл Modelfile с текстом:

```
FROM .\Qwen_Qwen3.5-4B-Q4_K_M.gguf
```
---
### Импортировать модель в Ollama


```
ollama create qwen35-4b -f Modelfile
```

---

### Запустить модель в Ollama


```
ollama run qwen35-4b
```