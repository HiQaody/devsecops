"""
ai-git-ops/app.py - Service AI GitOps
Standalone: python ai-git-ops/app.py  -> http://localhost:5001
Integré: importé depuis app.py principal via blueprint
"""
import pathlib, sys
BASE = pathlib.Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE))

from flask import Flask, request, jsonify, render_template

from core.github_detector import parse_github_url, fetch_repo_info, detect_dockerfile, fetch_file_content, fetch_repo_file_list
from core.dockerfile_analyzer import analyze_dockerfile
from core.jenkins_generator import generate_jenkinsfile

app = Flask(__name__, template_folder=str(BASE / "templates"), static_folder=str(BASE / "static"))

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.json or {}
    github_url = (data.get("github_url") or "").strip()
    token = (data.get("token") or "").strip() or None
    port = (data.get("port") or "3000").strip()
    if not github_url:
        return jsonify({"success": False, "message": "github_url requis"}), 400
    try:
        owner, repo = parse_github_url(github_url)
        info = fetch_repo_info(owner, repo, token)
        branch = info["default_branch"]
        file_list = fetch_repo_file_list(owner, repo, branch, token)
        docker = detect_dockerfile(owner, repo, branch, token)
        result = {
            "repo": f"{owner}/{repo}",
            "branch": branch,
            "language": info.get("language"),
            "file_list": file_list,
            "dockerfile": docker,
            "analysis": None,
        }
        if docker["found"]:
            content = fetch_file_content(docker["raw_url"], token)
            analysis = analyze_dockerfile(content, file_list, port)
            result["analysis"] = analysis
            result["dockerfile"]["content_preview"] = content[:2500]
            result["dockerfile"]["lines"] = len(content.splitlines())
            result["dockerfile"]["content"] = content
        else:
            result["analysis"] = {
                "technology": "unknown",
                "compliant": False,
                "score": 0,
                "summary": "Dockerfile manquant - génération depuis base de connaissance possible",
                "checks": [],
            }
        return jsonify({"success": True, "data": result})
    except ValueError as ve:
        return jsonify({"success": False, "message": str(ve)}), 400
    except FileNotFoundError as fe:
        return jsonify({"success": False, "message": str(fe)}), 404
    except Exception as e:
        return jsonify({"success": False, "message": f"Erreur analyse: {e}"}), 500

@app.route("/api/generate-jenkinsfile", methods=["POST"])
def gen_jenkins():
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
        if not n:
            continue
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
        return jsonify({"success": False, "message": "mode doit être k3s ou docker"}), 400
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
