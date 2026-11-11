# Lab: Skills + Hooks + MCP amb Claude Code

Pràctica guiada (~2 h) on configureu **skills**, **hooks** i l'**MCP d'Atlassian** per automatitzar el
cicle complet d'un requisit:

```
 Redactar requisit ──MCP──► Jira ──► Llegir i implementar (skills + hooks) ──MCP──► Jira (resultat)
```

| Peça   | Quin problema resol                                   | Qui l'executa       |
|--------|-------------------------------------------------------|---------------------|
| MCP    | Donar a Claude accés a un sistema extern (Jira)       | Claude (eines)      |
| Skills | Ensenyar a Claude **com** fer una tasca repetible     | Claude (decideix)   |
| Hooks  | Garanties **deterministes** (format, bloqueig, tests) | El harness (sempre) |

## Per començar

1. Llegiu **[`docs/enunciat.md`](docs/enunciat.md)**: conté les fases, els objectius i les pistes.
2. Si no sabeu quin requisit fer, mireu **[`docs/idees-requisits.md`](docs/idees-requisits.md)**.
3. Treballeu sobre una **còpia** de [`starter/`](starter/) (no dins d'aquest repositori).
4. Quan acabeu, verifiqueu la configuració:
   ```bash
   python3 scripts/check_lab.py <ruta-al-vostre-projecte>
   ```

## Prerequisits

- Claude Code instal·lat i autenticat
- Python 3.11+ i `git`
- Accés al projecte Jira de la lab (el formador us indicarà la clau)
