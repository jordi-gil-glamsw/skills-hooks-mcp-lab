#!/usr/bin/env python3
"""Verificador de la lab Skills + Hooks + MCP.

Ús:
    python3 scripts/check_lab.py [directori_del_projecte]

Comprova la CONFIGURACIÓ del participant (no el codi del requisit). Resultat per consola:
    OK   -> compleix
    WARN -> revisa-ho (no bloqueja)
    FAIL -> cal arreglar-ho
Surt amb codi 1 si hi ha algun FAIL.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

results: list[tuple[str, str]] = []


def ok(msg: str) -> None:
    results.append(("OK", msg))


def warn(msg: str) -> None:
    results.append(("WARN", msg))


def fail(msg: str) -> None:
    results.append(("FAIL", msg))


def parse_frontmatter(text: str) -> dict[str, str] | None:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    data: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            data[k.strip()] = v.strip()
    return data


# ---------------------------------------------------------------- MCP
def check_mcp(root: Path) -> None:
    mcp_file = root / ".mcp.json"
    if mcp_file.exists():
        try:
            servers = json.loads(mcp_file.read_text()).get("mcpServers", {})
        except json.JSONDecodeError:
            fail(".mcp.json no és JSON vàlid")
            return
        if any("mcp.atlassian.com" in json.dumps(s) for s in servers.values()):
            ok(".mcp.json declara el servidor d'Atlassian")
        else:
            fail(".mcp.json existeix però no apunta a mcp.atlassian.com")
    else:
        warn("No hi ha .mcp.json. Si has fet `claude mcp add` en scope local està bé; "
             "comprova-ho amb `claude mcp list`.")


# ---------------------------------------------------------------- Skills
def check_skills(root: Path) -> None:
    skills_dir = root / ".claude" / "skills"
    skills = sorted(p for p in skills_dir.glob("*/SKILL.md")) if skills_dir.exists() else []
    if len(skills) < 3:
        fail(f"Calen com a mínim 3 skills a .claude/skills/ (n'hi ha {len(skills)})")
    else:
        ok(f"{len(skills)} skills trobades")

    corpus = ""
    for path in skills:
        text = path.read_text()
        corpus += text.lower()
        fm = parse_frontmatter(text)
        name = path.parent.name
        if fm is None:
            fail(f"{name}: falta el frontmatter YAML (--- name/description ---)")
            continue
        if fm.get("name") != name:
            fail(f"{name}: el camp `name` ({fm.get('name')!r}) ha de coincidir amb el directori")
        elif len(fm.get("description", "")) < 60:
            warn(f"{name}: la description és molt curta; diu QUAN s'ha d'activar la skill")
        else:
            ok(f"{name}: frontmatter correcte")

    if skills:
        for label, needle in [
            ("redactar/crear requisits", "createjiraissue"),
            ("llegir tiquets", "getjiraissue"),
            ("actualitzar/comentar tiquets", "addoreditjiraissuecomment"),
        ]:
            if needle in corpus:
                ok(f"Alguna skill cobreix: {label} ({needle})")
            else:
                warn(f"Cap skill menciona l'eina `{needle}` ({label})")


# ---------------------------------------------------------------- Hooks
def run_hook(command: str, root: Path, payload: dict) -> subprocess.CompletedProcess:
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(root)}
    return subprocess.run(
        command, shell=True, cwd=root, env=env, input=json.dumps(payload),
        capture_output=True, text=True, timeout=120,
    )


def check_hooks(root: Path) -> None:
    settings_path = root / ".claude" / "settings.json"
    if not settings_path.exists():
        fail("Falta .claude/settings.json")
        return
    try:
        hooks = json.loads(settings_path.read_text()).get("hooks", {})
    except json.JSONDecodeError as e:
        fail(f".claude/settings.json no és JSON vàlid: {e}")
        return

    events = [e for e, v in hooks.items() if v]
    if len(events) < 3:
        fail(f"Calen hooks en com a mínim 3 esdeveniments diferents (n'hi ha {len(events)}: {events})")
    else:
        ok(f"Hooks configurats per a: {', '.join(events)}")

    for required in ("PreToolUse", "PostToolUse"):
        if required not in hooks:
            warn(f"No hi ha cap hook {required}")

    # Els scripts referenciats existeixen?
    for event, groups in hooks.items():
        for group in groups:
            for h in group.get("hooks", []):
                cmd = h.get("command", "")
                for ref in re.findall(r"\.claude/hooks/[\w./-]+", cmd):
                    if (root / ref).exists():
                        ok(f"{event}: {ref} existeix")
                    else:
                        fail(f"{event}: el script {ref} no existeix")

    # Prova de comportament 1: un PreToolUse sobre Bash ha de bloquejar `git push --force`.
    blocked = False
    tested = False
    for group in hooks.get("PreToolUse", []):
        if "Bash" not in group.get("matcher", "") and group.get("matcher", "") not in ("", "*"):
            continue
        for h in group.get("hooks", []):
            tested = True
            r = run_hook(h["command"], root, {
                "tool_name": "Bash",
                "tool_input": {"command": "git push --force origin main"},
            })
            blocked = blocked or r.returncode == 2
    if blocked:
        ok("Un hook PreToolUse bloqueja `git push --force` (exit 2)")
    elif tested:
        fail("Cap hook PreToolUse bloqueja `git push --force`: ha de sortir amb exit 2")
    else:
        warn("No hi ha cap hook PreToolUse per a Bash: no es pot provar el bloqueig")

    # Prova de comportament 2: un hook Stop no pot crear un bucle infinit.
    for group in hooks.get("Stop", []):
        for h in group.get("hooks", []):
            r = run_hook(h["command"], root, {"hook_event_name": "Stop", "stop_hook_active": True})
            if r.returncode == 0:
                ok("El hook Stop respecta `stop_hook_active` (evita bucles)")
            else:
                fail("El hook Stop ha de sortir amb exit 0 quan `stop_hook_active` és true")


# ---------------------------------------------------------------- Tests del projecte
def check_project_tests(root: Path) -> None:
    py = root / ".venv" / "bin" / "python"
    exe = str(py) if py.exists() else sys.executable
    r = subprocess.run([exe, "-m", "pytest", "-q", "--no-header"], cwd=root,
                       capture_output=True, text=True)
    if r.returncode == 0:
        ok("pytest passa")
    elif "No module named pytest" in r.stderr + r.stdout:
        warn("pytest no està instal·lat a l'entorn (activa el .venv i `pip install -e .[dev]`)")
    else:
        fail("pytest falla")


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    print(f"Verificant {root}\n")
    check_mcp(root)
    check_skills(root)
    check_hooks(root)
    check_project_tests(root)

    for status, msg in results:
        print(f"[{status:4}] {msg}")
    fails = sum(1 for s, _ in results if s == "FAIL")
    warns = sum(1 for s, _ in results if s == "WARN")
    print(f"\n{len(results) - fails - warns} OK · {warns} WARN · {fails} FAIL")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
