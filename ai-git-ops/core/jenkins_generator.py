"""
jenkins_generator.py - Génère Jenkinsfile en 2 modes à partir de la knowledge base
- mode k3s : push Harbor + kubectl apply
- mode docker : push Harbor + docker run standalone
"""
import json
import pathlib

KB_PATH = pathlib.Path(__file__).parent / "knowledge_base.json"

def load_kb():
    with open(KB_PATH, encoding="utf-8") as f:
        return json.load(f)

def sanitize_name(name: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "-" for c in name.lower()).strip("-") or "app"

def generate_k3s_jenkinsfile(app_name, port, node_port, envs, docker_info=None):
    kb = load_kb()
    registry = kb["registry"]
    project = kb["harbor_project"]
    namespace = kb["namespace"]
    app = sanitize_name(app_name)
    env_block = "\n".join([f"        {e['name']} = ''" for e in envs]) if envs else "        // no env"
    # credentials withCredentials
    creds_build = "                    string(credentialsId: '{id}', variable: '{var}'),\n".format
    # On mappe envs -> credentials
    build_creds = "".join([f"                    string(credentialsId: '{e['secret_id']}', variable: '{e['name']}'),\n" for e in envs])
    deploy_creds = build_creds

    docker_build_args = "".join([f"                          --build-arg {e['name']}=\"\\${{{e['name']}}}\" \\\n" for e in envs])

    return f"""pipeline {{
    agent any
    environment {{
        REGISTRY         = '{registry}'
        HARBOR_PROJECT   = '{project}'
        IMAGE_NAME       = '{app}'
        IMAGE_TAG        = "\\${{BUILD_NUMBER}}"
        FULL_IMAGE_NAME  = "\\${{REGISTRY}}/\\${{HARBOR_PROJECT}}/\\${{IMAGE_NAME}}:\\${{IMAGE_TAG}}"
        NAMESPACE        = '{namespace}'
        K8S_DIR          = 'k8s'
        DEPLOYMENT_NAME  = '{app}'
        SERVICE_NAME     = '{app}-service'
        HPA_NAME         = '{app}-hpa'
        SECRET_NAME      = '{app}-secret'
        PORT             = '{port}'
        NODE_PORT        = '{node_port}'
{env_block}
    }}
    stages {{
        stage('Build & Push') {{
            steps {{
                withCredentials([
                    usernamePassword(credentialsId: 'harbor-credentials', usernameVariable: 'HARBOR_USER', passwordVariable: 'HARBOR_PASS'),
{build_creds}                ]) {{
                    sh '''
                        set -e
                        docker logout \\${{REGISTRY}} || true
                        docker build \\
{docker_build_args}                          --build-arg PORT={port} \\
                          -t \\${{FULL_IMAGE_NAME}} .
                        echo \\${{HARBOR_PASS}} | docker login -u \\${{HARBOR_USER}} --password-stdin \\${{REGISTRY}}
                        docker push \\${{FULL_IMAGE_NAME}}
                        docker logout \\${{REGISTRY}}
                    '''
                }}
            }}
        }}
        stage('Deploy to K3s') {{
            steps {{
                withCredentials([
                    file(credentialsId: 'kubeconfig-jenkins', variable: 'KUBECONFIG'),
                    usernamePassword(credentialsId: 'harbor-credentials', usernameVariable: 'HARBOR_USER', passwordVariable: 'HARBOR_PASS'),
{deploy_creds}                ]) {{
                    sh '''
                        set -e
                        export KUBECONFIG=\\${{KUBECONFIG}}
                        kubectl create namespace \\${{NAMESPACE}} --dry-run=client -o yaml | kubectl apply -f -
                        kubectl delete secret harbor-registry-secret -n \\${{NAMESPACE}} --ignore-not-found
                        kubectl create secret docker-registry harbor-registry-secret \\
                          --docker-server=\\${{REGISTRY}} \\
                          --docker-username="\\${{HARBOR_USER}}" \\
                          --docker-password="\\${{HARBOR_PASS}}" \\
                          --namespace=\\${{NAMESPACE}}
                        kubectl delete secret \\${{SECRET_NAME}} -n \\${{NAMESPACE}} --ignore-not-found
                        kubectl create secret generic \\${{SECRET_NAME}} \\
{"".join([f"                          --from-literal={e['name']}=\"\\${{{e['name']}}}\" \\\n" for e in envs])}                          --namespace=\\${{NAMESPACE}}
                        for res in deployment service hpa; do
                            envsubst < \\${{K8S_DIR}}/{app}-${{res}}.yaml > /tmp/{app}-${{res}}.yaml
                            kubectl apply -f /tmp/{app}-${{res}}.yaml
                        done
                        kubectl rollout status deployment/{app} -n \\${{NAMESPACE}} --timeout=120s
                        kubectl get pods -n \\${{NAMESPACE}} -l app={app}
                    '''
                }}
            }}
        }}
    }}
    post {{ always {{ cleanWs() }} }}
}}
"""

def generate_docker_jenkinsfile(app_name, port, envs, docker_info=None):
    kb = load_kb()
    registry = kb["registry"]
    project = kb["harbor_project"]
    app = sanitize_name(app_name)
    env_list = " ".join([f"-e {e['name']}=\\\"\\${{{e['name']}}}\\\"" for e in envs])
    build_args = "".join([f"                          --build-arg {e['name']}=\"\\${{{e['name']}}}\" \\\n" for e in envs])
    creds = "".join([f"                    string(credentialsId: '{e['secret_id']}', variable: '{e['name']}'),\n" for e in envs])

    return f"""pipeline {{
    agent any
    environment {{
        REGISTRY         = '{registry}'
        HARBOR_PROJECT   = '{project}'
        IMAGE_NAME       = '{app}'
        IMAGE_TAG        = "\\${{BUILD_NUMBER}}"
        FULL_IMAGE_NAME  = "\\${{REGISTRY}}/\\${{HARBOR_PROJECT}}/\\${{IMAGE_NAME}}:\\${{IMAGE_TAG}}"
        CONTAINER_NAME   = '{app}'
        PORT             = '{port}'
{"".join([f"        {e['name']} = ''\n" for e in envs])}    }}
    stages {{
        stage('Build & Push') {{
            steps {{
                withCredentials([
                    usernamePassword(credentialsId: 'harbor-credentials', usernameVariable: 'HARBOR_USER', passwordVariable: 'HARBOR_PASS'),
{creds}                ]) {{
                    sh '''
                        set -e
                        docker logout \\${{REGISTRY}} || true
                        docker build \\
{build_args}                          --build-arg PORT={port} \\
                          -t \\${{FULL_IMAGE_NAME}} .
                        echo \\${{HARBOR_PASS}} | docker login -u \\${{HARBOR_USER}} --password-stdin \\${{REGISTRY}}
                        docker push \\${{FULL_IMAGE_NAME}}
                        docker logout \\${{REGISTRY}}
                    '''
                }}
            }}
        }}
        stage('Deploy (docker run)') {{
            steps {{
                withCredentials([
                    usernamePassword(credentialsId: 'harbor-credentials', usernameVariable: 'HARBOR_USER', passwordVariable: 'HARBOR_PASS'),
{creds}                ]) {{
                    sh '''
                        set -e
                        echo \\${{HARBOR_PASS}} | docker login -u \\${{HARBOR_USER}} --password-stdin \\${{REGISTRY}}
                        docker pull \\${{FULL_IMAGE_NAME}}
                        docker stop \\${{CONTAINER_NAME}} || true
                        docker rm \\${{CONTAINER_NAME}} || true
                        docker run -d --name \\${{CONTAINER_NAME}} \\
                          --restart unless-stopped \\
                          -p \\${{PORT}}:\\${{PORT}} \\
                          {env_list} \\
                          \\${{FULL_IMAGE_NAME}}
                        docker ps | grep \\${{CONTAINER_NAME}}
                        docker logs --tail 50 \\${{CONTAINER_NAME}} || true
                    '''
                }}
            }}
        }}
    }}
    post {{ always {{ cleanWs() }} }}
}}
"""

def generate_jenkinsfile(mode: str, app_name: str, port: str, node_port: str = "30130", envs=None, docker_info=None):
    envs = envs or []
    if mode == "k3s":
        return generate_k3s_jenkinsfile(app_name, port, node_port, envs, docker_info)
    elif mode == "docker":
        return generate_docker_jenkinsfile(app_name, port, envs, docker_info)
    else:
        raise ValueError("mode doit être 'k3s' ou 'docker'")
