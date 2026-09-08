# Postman collection

## Import (GUI)

1. Postman → **Import** → select `JuniorSwipe.postman_collection.json` and
   `JuniorSwipe.postman_environment.json`.
2. Pick the **JuniorSwipe Local** environment (top-right).
3. Start the backend (`docker compose up` or `python backend/run.py`).
4. Run **Auth → Login (stores token)** first — it saves `{{token}}` as a
   collection variable; every other request inherits Bearer auth automatically.
5. Then run **Projects → Create project** (saves `{{projectId}}`) before the
   Tasks folder.

## Run headless with Newman (used by CI)

```bash
npm install -g newman
newman run postman/JuniorSwipe.postman_collection.json \
  --env-var baseUrl=http://localhost:5000
```

The collection has assertions on every request (status codes, JWT shape,
pagination envelope, ownership), so a green Newman run proves the API works
end-to-end.
