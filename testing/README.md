
```bash
curl http://localhost:8000/v1/chat/completions     -H "Content-Type: application/json"     -d '{
        "model": "mistralai/Mistral-7B-Instruct-v0.1",
        "messages": [
            {"role": "user", "content": "You are a helpful assistant who answers questions."},
            {"role": "assistant", "content": "Sounds great!"},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
    }'
```

```bash
curl http://localhost:8000/metrics
```
