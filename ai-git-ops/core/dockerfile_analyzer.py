"""
dockerfile_analyzer.py - Analyse conformité Dockerfile vs technologie
"""
import re
import json
import pathlib

KB_PATH = pathlib.Path(__file__).parent / "knowledge_base.json"

def load_kb():
    with open(KB_PATH, encoding="utf-8") as f:
        return json.load(f)

def detect_technology(dockerfile_content: str, file_list=None):
    """Détecte stack via FROM + fichiers présents"""
    file_list = file_list or []
    content = dockerfile_content or ""
    lower = content.lower()

    # Priorité Dockerfile FROM
    if "from node" in lower:
        return "node"
    if "from python" in lower:
        return "python"
    if "from eclipse-temurin" in lower or "from openjdk" in lower:
        return "java"
    if "from golang" in lower:
        return "go"
    # Fallback fichiers
    if "package.json" in file_list:
        return "node"
    if "requirements.txt" in file_list or "pyproject.toml" in file_list:
        return "python"
    if "pom.xml" in file_list or "build.gradle" in file_list:
        return "java"
    if "go.mod" in file_list:
        return "go"
    return "unknown"

def analyze_dockerfile(content: str, file_list=None, port: str = None):
    kb = load_kb()
    tech = detect_technology(content, file_list)
    lines = content.splitlines() if content else []

    from_line = next((l.strip() for l in lines if l.strip().upper().startswith("FROM")), None)
    user_line = next((l for l in lines if re.match(r"^\s*USER\s+", l, re.I)), None)
    expose_lines = [l for l in lines if re.match(r"^\s*EXPOSE\s+", l, re.I)]
    has_arg_port = bool(re.search(r"^\s*ARG\s+PORT", content, re.M))
    has_env_port = bool(re.search(r"ENV.*PORT", content))

    # Checks
    checks = []
    def add(name, ok, detail, severity="info"):
        checks.append({"rule": name, "ok": ok, "detail": detail, "severity": severity})

    # FROM :latest interdit
    if from_line:
        if ":latest" in from_line:
            add("FROM sans :latest", False, f"Trouvé: {from_line} -> utiliser tag fixe (ex: node:20-slim)", "critical")
        else:
            add("FROM sans :latest", True, from_line, "info")

        # Base image conforme?
        tech_cfg = kb["technologies"].get(tech, {})
        allowed = tech_cfg.get("base_images", [])
        if allowed and not any(a.split(":")[0] in from_line for a in allowed):
            # warning si base non recommandée mais pas bloquant
            add("Base image recommandée", False, f"{from_line} | Recommandé: {', '.join(allowed)}", "warning")
        elif allowed:
            add("Base image recommandée", True, f"Conforme: {from_line}", "info")
    else:
        add("FROM présent", False, "Aucun FROM trouvé", "critical")

    # USER non-root
    if user_line:
        if re.search(r"USER\s+(0|root)", user_line, re.I):
            add("USER non-root", False, f"{user_line.strip()} -> utiliser USER node / 1000 / 101", "critical")
        else:
            add("USER non-root", True, user_line.strip(), "info")
    else:
        add("USER non-root", False, "Aucun USER -> ajout requis (USER node)", "warning")

    # EXPOSE
    if expose_lines:
        add("EXPOSE présent", True, ", ".join(l.strip() for l in expose_lines), "info")
        if port:
            if not any(port in l for l in expose_lines) and not any("${PORT}" in l or "$PORT" in l for l in expose_lines):
                add("EXPOSE correspond au PORT", False, f"EXPOSE {expose_lines[0].strip()} != PORT {port}", "warning")
    else:
        add("EXPOSE présent", False, "Manquant -> ajouter EXPOSE ${PORT}", "warning")

    add("ARG PORT", has_arg_port, "Présent" if has_arg_port else "Manquant (recommandé pour build-arg)", "info" if has_arg_port else "warning")
    add("Multi-stage build", bool(re.search(r"^\s*FROM.*AS\s+\w+", content, re.M | re.I)), "Détecté" if re.search(r"FROM.*AS", content, re.I) else "Non détecté (recommandé pour Java/Node build)", "info")

    # Secrets en dur ?
    if re.search(r"ENV\s+.*(PASSWORD|SECRET|TOKEN).*=.*[a-zA-Z0-9]{3,}", content):
        add("Pas de secrets en dur", False, "ENV contient valeur en clair -> utiliser ARG/secret", "critical")
    else:
        add("Pas de secrets en dur", True, "OK", "info")

    # Score
    critical_failed = sum(1 for c in checks if not c["ok"] and c["severity"] == "critical")
    warning_failed = sum(1 for c in checks if not c["ok"] and c["severity"] == "warning")
    score = max(0, 100 - critical_failed*25 - warning_failed*10)
    compliant = critical_failed == 0 and score >= 70

    return {
        "technology": tech,
        "from": from_line,
        "user": user_line.strip() if user_line else None,
        "expose": [l.strip() for l in expose_lines],
        "checks": checks,
        "score": score,
        "compliant": compliant,
        "critical_failed": critical_failed,
        "summary": "Conforme" if compliant else "Non conforme - corrections requises" if critical_failed else "Partiellement conforme",
    }
