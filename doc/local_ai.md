# local ai Setup


```
docker compose up -d
```

check http://localhost:11434

![ollama](./images/ollama.png)

<br>

http://localhost:3000/auth

register user
![open_webui_reg.png](./images/open_webui_reg.png)

<br>

download model
![open_webui_model.png](./images/open_webui_model.png)

or run in ollama container without open webui

```
ollama pull qwen2:0.5b
```