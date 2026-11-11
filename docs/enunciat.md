# Enunciat — Lab Skills + Hooks + MCP

**Durada:** ~2 h · **Nivell:** bàsic-intermedi de Claude Code · **Format:** individual o parelles

## Escenari

El vostre equip gestiona els requisits a **Jira**. Voleu que Claude Code pugui:

1. **Ajudar a redactar** un requisit ben format i crear-lo a Jira,
2. **Llegir** aquest requisit des del projecte i **implementar-lo** amb qualitat,
3. **Tornar a Jira** amb un resum verificable del que s'ha fet.

I voleu que tot això passi amb **garanties** (codi formatejat, res perillós, tests en verd).
La feina és configurar les peces; no cal que escriviu el codi del requisit a mà.

## Punt de partida

Copieu `starter/` a una carpeta vostra i prepareu l'entorn:

```bash
cp -R starter ~/lab-tasks-api && cd ~/lab-tasks-api
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q          # 5 tests en verd
git init && git add -A && git commit -m "Starter"
```

> El projecte **no té cap configuració de Claude**: skills, hooks i MCP els heu de construir vosaltres.

---

## Fase 0 — Connectar l'MCP de Jira (15 min)

1. Afegiu el servidor d'Atlassian al projecte (scope `project` → genera `.mcp.json`):
   ```bash
   claude mcp add --transport http --scope project atlassian https://mcp.atlassian.com/v2/mcp
   ```
2. Obriu `claude` **amb el venv activat** (perquè els hooks trobin `ruff` i `pytest`). Us demanarà
   aprovar el servidor del projecte: accepteu-lo. Després executeu `/mcp`, trieu `atlassian` i feu
   l'**autenticació OAuth** al navegador.
   > Si ja teniu el connector "Atlassian" de claude.ai activat, desactiveu-lo durant la lab: dos
   > servidors per al mateix Jira confonen Claude.
3. Comproveu la connexió demanant a Claude: *"Llista els projectes de Jira que puc veure"*.

**✅ Hi ha èxit quan:** Claude us retorna el projecte de la lab (el formador us dirà la clau, p. ex. `LAB`).

> 💡 Aquest servidor no exposa totes les eines de cop: n'ofereix unes quantes (`getJiraIssue`,
> `createJiraIssue`, `editJiraIssue`, `transitionJiraIssue`, `addOrEditJiraIssueComment`, …) i la resta
> es descobreixen sota demanda. Demaneu a Claude *"quines eines de Jira tens?"* per veure-les.

---

## Fase 1 — Skills (30 min)

Una **skill** és una carpeta `.claude/skills/<nom>/SKILL.md` amb un frontmatter (`name`, `description`)
i instruccions. Claude la carrega quan la `description` encaixa amb el que li demaneu.

**Reptes:** creeu les skills que considereu necessàries per al cicle. Com a mínim, penseu en:

| Moment | Què hauria de saber fer Claude |
|--------|--------------------------------|
| Redactar | Convertir una idea en un requisit amb criteris d'acceptació comprovables i crear-lo a Jira |
| Implementar | Llegir el tiquet, planificar, treballar amb tests i complir els criteris |
| Informar | Escriure a Jira un resum **verificable** (no un "tot fet!") |
| Convencions | Les regles del projecte (estructura, tests, estil de commits) |

**Pistes**
- La `description` és el que decideix si la skill s'activa: digueu **quan** s'ha d'usar i amb quines frases.
- Escriviu passos concrets i regles negatives ("no toquis Jira en aquesta fase").
- Una skill = una responsabilitat. Les skills petites i ben delimitades s'activen millor.
- Podeu demanar a Claude que us ajudi a escriure-les, però **reviseu** el resultat.

**✅ Hi ha èxit quan:** en una sessió nova, `/skills` (o preguntant-ho a Claude) mostra les vostres skills.

---

## Fase 2 — Hooks (30 min)

Un **hook** és una ordre que el harness executa automàticament en un esdeveniment, amb el JSON de
l'esdeveniment per `stdin`. Es defineixen a `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      { "matcher": "Edit|Write",
        "hooks": [ { "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/x.py" } ] }
    ]
  }
}
```

Codis de sortida que cal conèixer: **0** = ok · **2** = bloqueja i retorna `stderr` a Claude.

**Reptes:** implementeu hooks (en Python, amb només la llibreria estàndard) que garanteixin, com a mínim:

1. **Format automàtic** — després d'editar un `.py`, passar `ruff` (i retornar els errors a Claude si no es poden arreglar sols). *(PostToolUse)*
2. **Barrera de seguretat** — bloquejar comandes perilloses (`git push --force`, `rm -rf`, …) i l'edició de fitxers `.env`. *(PreToolUse)*
3. **Porta de qualitat** — que Claude no pugui "acabar" si els tests fallen. *(Stop)*
4. **Context inicial** — injectar a cada sessió un recordatori del flux de treball. *(SessionStart)*

**Pistes**
- Llegiu l'entrada amb `json.load(sys.stdin)`; per a eines de fitxers el camí és a `tool_input.file_path`.
- Useu `$CLAUDE_PROJECT_DIR` per no dependre del directori actual.
- ⚠️ **Hook Stop:** si bloqueja sempre, Claude no pot parar mai. Mireu el camp `stop_hook_active`.
- Proveu cada script a mà abans de connectar-lo:
  ```bash
  echo '{"tool_name":"Bash","tool_input":{"command":"git push --force"}}' | python3 .claude/hooks/guard.py; echo $?
  ```
- Després de canviar `settings.json`, reinicieu la sessió (o reviseu `/hooks`).

**✅ Hi ha èxit quan:** demaneu a Claude que faci un `git push --force` i veieu com és bloquejat.

---

## Fase 3 — El cicle complet (30 min)

Ara feu servir el que heu construït. **Una sessió de Claude per pas** (simula tres moments diferents
de la vida real).

**3.1 Redactar.** Trieu un requisit de `docs/idees-requisits.md` (o inventeu-ne un) i demaneu-ho en
llenguatge natural: *"Vull que l'API permeti filtrar tasques per estat. Ajuda'm a redactar-ho i
crea'l a Jira."* Revisar l'esborrany, corregiu-lo i confirmeu. Anoteu la **clau** del tiquet.

**3.2 Implementar.** Nova sessió (`/clear` o `claude` de nou): *"Implementa LAB-xx"*.
Observeu: es carrega la skill? Llegeix el tiquet via MCP? Escriu primer els tests? Salten els hooks?

**3.3 Informar.** *"Actualitza el tiquet amb el resultat."* Comproveu a Jira que el comentari és
fiable: criteris, fitxers, resultat real dels tests.

**✅ Hi ha èxit quan:** el tiquet té el requisit complet **i** un comentari final que un company podria
verificar sense obrir el codi, i `pytest -q` passa.

---

## Fase 4 — Verificació i reflexió (15 min)

```bash
python3 <ruta-lab>/scripts/check_lab.py .
```

Objectiu: **0 FAIL**. Discutiu en grup:

1. Què ha acabat sent skill i què hook? Per què?
2. Quin hook us ha estalviat un error real durant la fase 3?
3. Què passaria si l'MCP tingués permisos d'escriptura a tot Jira? Quins límits posaríeu?
4. Què canviaríeu de la `description` d'una skill que no s'ha activat quan tocava?

## 🎯 Reptes extra

- Hook `PostToolUse` que afegeixi automàticament la clau Jira (de la branca) als commits.
- Skill que, abans d'implementar, **comprovi que el tiquet té criteris d'acceptació** i, si no, ho digui.
- Permisos (`permissions.allow/deny` a `settings.json`) perquè Claude només pugui *escriure* a Jira amb
  les eines que necessiteu.
- Un sub-agent revisor que valida el codi contra els criteris abans d'informar a Jira.
