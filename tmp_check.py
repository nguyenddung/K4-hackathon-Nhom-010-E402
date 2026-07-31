from llm_client import parse_json_object
payload='''```json
{"ok": true}
```'''
print(parse_json_object(payload))
