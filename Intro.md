# Simple Chat bot based on KoGPT2

- Korean Chatbot.
- Send text, receive a reply from the chatbot.

## API
- (POST) /gpt2-chat

## cURL Example
```bash
curl -X POST "https://master-ko-gpt2-chatbot-psi1104.endpoint.ainize.ai/gpt2-chat" -H  "accept: text/html" -H  "Content-Type: multipart/form-data" -F "text=안녕?"
```
