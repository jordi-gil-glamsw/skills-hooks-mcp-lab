# Banc de requisits per a la lab

Tots són petits (< 30 min) i independents, perquè cada participant en tingui un de diferent i no hi hagi
conflictes de codi. Estan pensats sobre l'API de tasques existent (`/tasks`).

| # | Requisit | Pistes de criteris d'acceptació |
|---|----------|--------------------------------|
| 1 | **Filtrar per estat** — `GET /tasks?status=done` | Filtre vàlid; estat desconegut → 422; sense filtre → totes |
| 2 | **Canviar l'estat** — `PATCH /tasks/{id}` amb `{"status": ...}` | 200 amb la tasca; 404 si no existeix; 422 si l'estat és invàlid |
| 3 | **Cerca per títol** — `GET /tasks?q=text` | Insensible a majúscules; coincidència parcial; buit → llista buida |
| 4 | **Paginació** — `GET /tasks?limit=&offset=` | Valors per defecte; `limit` màx. 100; fora de rang → 422 |
| 5 | **Prioritat** — camp `priority` (`low/medium/high`, per defecte `medium`) | Es guarda en crear; es retorna; valor invàlid → 422 |
| 6 | **Data límit** — camp opcional `due_date`; no pot ser al passat | Data futura OK; passada → 422; opcional |
| 7 | **Estadístiques** — `GET /tasks/stats` amb recompte per estat | `{todo, in_progress, done}`; zeros si buit; no col·lideix amb `/tasks/{id}` |
| 8 | **Esborrat en bloc de fetes** — `DELETE /tasks?status=done` | Retorna quantes n'ha esborrat; no toca les altres |
| 9 | **Actualitzar títol/descripció** — `PUT /tasks/{id}` | Valida com a crear; 404; conserva l'estat |
| 10 | **Ordenació** — `GET /tasks?sort=title` o `-title` | Ascendent/descendent; camp desconegut → 422 |

## Perquè sigui una bona pràctica de redacció

Un requisit ben escrit al tiquet **no** hauria de dir "com" sinó "què es pot comprovar":

❌ *"Afegir un filtre a la llista"*
✅ *"Given 3 tasques (1 done, 2 todo) When GET /tasks?status=done Then 200 i només la tasca done"*
