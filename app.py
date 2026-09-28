import os
import shutil
import pathlib
import sys
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --- AI GitOps integration (dossier ai-git-ops) ---
AI_GIT_OPS_BASE = pathlib.Path(__file__).parent / "ai-git-ops"
if AI_GIT_OPS_BASE.exists():
    sys.path.insert(0, str(AI_GIT_OPS_BASE))
    try:
        from core.github_detector import parse_github_url, fetch_repo_info, detect_dockerfile, fetch_file_content, fetch_repo_file_list
        from core.dockerfile_analyzer import analyze_dockerfile
        from core.jenkins_generator import generate_jenkinsfile
        AI_GIT_OPS_AVAILABLE = True
    except Exception as _e:
        print(f"[ai-git-ops] import failed: {_e}")
        AI_GIT_OPS_AVAILABLE = False
else:
    AI_GIT_OPS_AVAILABLE = False

def _dockerfile_content(port, envs):
    return f"""FROM node:20-slim

WORKDIR /app

COPY package*.json ./
RUN npm ci --ignore-scripts && npm cache clean --force
COPY . .

{"".join([f"ARG {e['name']}\n" for e in envs])}ARG PORT

ENV {" \\\n    ".join([f"{e['name']}=${{{e['name']}}}" for e in envs])} \\
    PORT=${{PORT}}

EXPOSE ${{PORT}}

USER node
CMD ["node", "dist/main", "--port", "${{PORT}}"]
"""

def _jenkinsfile_docker(app_name, port, envs):
    env_args = " \\\n                          ".join([f"-e {e['name']}=\"\\${{{e['name']}}}\"" for e in envs])
    env_flags = f" \\\n                          {env_args}" if env_args else ""
    return f"""pipeline {{
    agent any
    environment {{
        IMAGE_NAME       = '{app_name}'
        IMAGE_TAG        = "\\${{BUILD_NUMBER}}"
        CONTAINER_NAME   = '{app_name}'
        PORT             = '{port}'
{"".join([f"        {e['name']} = ''\n" for e in envs])}    }}
    stages {{
        stage('Build') {{
            steps {{
                withCredentials([
{"".join([f"                    string(credentialsId: '{e['secret_id']}', variable: '{e['name']}'),\n" for e in envs])}                ]) {{
                    sh '''
                        set -e
                        docker build \\
{"".join([f"                          --build-arg {e['name']}=\"\\${{{e['name']}}}\" \\\n" for e in envs])}                          --build-arg PORT={port} \\
                          -t \\${{IMAGE_NAME}}:\\${{IMAGE_TAG}} .
                        docker images \\${{IMAGE_NAME}}:\\${{IMAGE_TAG}}
                    '''
                }}
            }}
        }}
        stage('Deploy (docker run)') {{
            steps {{
                withCredentials([
{"".join([f"                    string(credentialsId: '{e['secret_id']}', variable: '{e['name']}'),\n" for e in envs])}                ]) {{
                    sh '''
                        set -e
                        docker stop \\${{CONTAINER_NAME}} || true
                        docker rm \\${{CONTAINER_NAME}} || true
                        docker run -d --name \\${{CONTAINER_NAME}} \\
                          --restart unless-stopped \\
                          -p \\${{PORT}}:\\${{PORT}}{env_flags} \\
                          \\${{IMAGE_NAME}}:\\${{IMAGE_TAG}}
                        echo "Container \\${{CONTAINER_NAME}} demarre sur le port \\${{PORT}}"
                        docker ps | grep \\${{CONTAINER_NAME}} || true
                        docker logs --tail 50 \\${{CONTAINER_NAME}} || true
                    '''
                }}
            }}
        }}
    }}
    post {{ always {{ cleanWs() }} }}
}}
"""

def generate_files(app_name, port, envs, output_dir):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Dockerfile - Docker standalone (sans K3s)
    dockerfile = _dockerfile_content(port, envs)
    with open(os.path.join(output_dir, "Dockerfile"), "w", encoding="utf-8") as f:
        f.write(dockerfile)

    # Jenkinsfile Docker standalone sans registry : docker build -> docker run
    jenkins_content = _jenkinsfile_docker(app_name, port, envs)
    with open(os.path.join(output_dir, "Jenkinsfile"), "w", encoding="utf-8") as f:
        f.write(jenkins_content)

# K8S Secret YAML (utilitaire)
def write_secret_yaml(app_name, var_names, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"""apiVersion: v1
kind: Secret
metadata:
  name: {app_name}-secret
  namespace: ${{NAMESPACE}}
type: Opaque
stringData:
""")
        for var in var_names:
            f.write(f"  {var}: \"${{{var}}}\"\n")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/ai-git-ops", methods=["GET"])
def ai_git_ops_page():
    # Page dediee AI GitOps
    ai_tpl = AI_GIT_OPS_BASE / "templates" / "index.html"
    if ai_tpl.exists():
        # Rend le template ai-git-ops avec son propre dossier
        from flask import send_from_directory
        # Utilise le moteur Jinja avec chemin absolu
        import jinja2
        # Charge manuellement le template
        with open(ai_tpl, encoding="utf-8") as f:
            content = f.read()
        # Remplace url_for statique ai-git-ops par /ai-git-ops/static
        # On sert via render simple
        return content.replace("{{ url_for('static', filename='style.css') }}", "/ai-git-ops/static/style.css").replace("{{ url_for('static', filename='script.js') }}", "/ai-git-ops/static/script.js")
    return "Module ai-git-ops non trouve", 404

@app.route("/ai-git-ops/static/<path:filename>")
def ai_git_ops_static(filename):
    return app.send_static_file(f"../ai-git-ops/static/{filename}") if False else __import__("flask").send_from_directory(str(AI_GIT_OPS_BASE / "static"), filename)

@app.route("/api/analyze", methods=["POST"])
def ai_analyze():
    if not AI_GIT_OPS_AVAILABLE:
        return jsonify({"success": False, "message": "Module ai-git-ops non disponible (requests manquant?)"}), 500
    data = request.json or {}
    github_url = (data.get("github_url") or "").strip()
    token = (data.get("token") or "").strip() or None
    port = str(data.get("port") or "3000").strip()
    if not github_url:
        return jsonify({"success": False, "message": "github_url requis"}), 400
    try:
        owner, repo = parse_github_url(github_url)
        info = fetch_repo_info(owner, repo, token)
        branch = info["default_branch"]
        file_list = fetch_repo_file_list(owner, repo, branch, token)
        docker = detect_dockerfile(owner, repo, branch, token)
        result = {"repo": f"{owner}/{repo}", "branch": branch, "language": info.get("language"), "file_list": file_list, "dockerfile": docker, "analysis": None}
        if docker["found"]:
            content = fetch_file_content(docker["raw_url"], token)
            analysis = analyze_dockerfile(content, file_list, port)
            result["analysis"] = analysis
            result["dockerfile"]["content_preview"] = content[:2500]
            result["dockerfile"]["lines"] = len(content.splitlines())
            result["dockerfile"]["content"] = content
        else:
            result["analysis"] = {"technology": "unknown", "compliant": False, "score": 0, "summary": "Dockerfile manquant", "checks": []}
        return jsonify({"success": True, "data": result})
    except ValueError as ve:
        return jsonify({"success": False, "message": str(ve)}), 400
    except FileNotFoundError as fe:
        return jsonify({"success": False, "message": str(fe)}), 404
    except Exception as e:
        return jsonify({"success": False, "message": f"Erreur analyse: {e}"}), 500

@app.route("/api/generate-jenkinsfile", methods=["POST"])
def ai_generate_jenkinsfile():
    if not AI_GIT_OPS_AVAILABLE:
        return jsonify({"success": False, "message": "Module ai-git-ops non disponible"}), 500
    data = request.json or {}
    mode = (data.get("mode") or "k3s").strip().lower()
    github_url = (data.get("github_url") or "").strip()
    app_name = (data.get("app_name") or data.get("name_images") or "").strip()
    port = str(data.get("port") or data.get("port_container") or "3000").strip()
    node_port = str(data.get("node_port") or "30130").strip()
    envs = data.get("envs") or []
    norm_envs = []
    for e in envs:
        n = (e.get("name") or "").strip().upper()
        if not n: continue
        norm_envs.append({"name": n, "value": e.get("value") or "", "secret_id": (e.get("secret_id") or f"{n}_ID").strip()})
    if not app_name and github_url:
        try:
            _, repo = parse_github_url(github_url)
            app_name = repo.lower()
        except Exception:
            app_name = "app"
    if not app_name:
        return jsonify({"success": False, "message": "app_name requis"}), 400
    if mode not in ("k3s", "docker"):
        return jsonify({"success": False, "message": "mode doit etre k3s ou docker"}), 400
    docker_info = None
    if github_url:
        try:
            owner, repo = parse_github_url(github_url)
            info = fetch_repo_info(owner, repo, None)
            docker = detect_dockerfile(owner, repo, info["default_branch"], None)
            if docker["found"]:
                content = fetch_file_content(docker["raw_url"], None)
                fl = fetch_repo_file_list(owner, repo, info["default_branch"], None)
                docker_info = analyze_dockerfile(content, fl, port)
        except Exception:
            pass
    try:
        jenkinsfile = generate_jenkinsfile(mode, app_name, port, node_port, norm_envs, docker_info)
        return jsonify({"success": True, "mode": mode, "app_name": app_name, "jenkinsfile": jenkinsfile, "docker_info": docker_info})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json or {}
    app_name = (data.get("app_name") or data.get("name_images") or data.get("image_name") or "").strip()
    port = (data.get("port") or data.get("port_container") or data.get("PORT") or "").strip() if isinstance(data.get("port") or data.get("port_container"), str) else data.get("port") or data.get("port_container") or data.get("PORT")
    if port is not None:
        port = str(port).strip()
    envs = data.get("envs", [])

    normalized_envs = []
    for e in envs:
        name = (e.get("name") or "").strip().upper()
        if not name:
            continue
        value = e.get("value") or ""
        secret_id = (e.get("secret_id") or "").strip() or f"{name}_ID"
        normalized_envs.append({"name": name, "value": value, "secret_id": secret_id})

    if not app_name:
        return jsonify({"success": False, "message": "name_images / app_name est requis"}), 400
    if not port:
        return jsonify({"success": False, "message": "PORT Container est requis"}), 400
    try:
        int_port = int(port)
        if not (1 <= int_port <= 65535):
            raise ValueError("PORT invalide")
    except ValueError as ve:
        return jsonify({"success": False, "message": f"Port invalide: {ve}"}), 400

    safe_name = "".join(c if c.isalnum() or c in "-_" else "-" for c in app_name.lower()).strip("-")
    if not safe_name:
        safe_name = "app"
    output_dir = os.path.join("generated", safe_name)
    try:
        generate_files(safe_name, port, normalized_envs, output_dir)
        dockerfile_path = os.path.join(output_dir, "Dockerfile")
        jenkinsfile_path = os.path.join(output_dir, "Jenkinsfile")
        dockerfile_content = open(dockerfile_path, encoding="utf-8").read() if os.path.exists(dockerfile_path) else ""
        jenkinsfile_content = open(jenkinsfile_path, encoding="utf-8").read() if os.path.exists(jenkinsfile_path) else ""
        return jsonify({
            "success": True,
            "message": f"Fichiers generes dans {output_dir}",
            "app": safe_name,
            "port": port,
            "envs": len(normalized_envs),
            "mode": "docker",
            "dockerfile": dockerfile_content,
            "jenkinsfile": jenkinsfile_content
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
