import os
import shutil
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def generate_files(app_name, port, node_port, envs, output_dir):
    k8s_dir = os.path.join(output_dir, "k8s")
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(k8s_dir, exist_ok=True)

    # Dockerfile
    with open(os.path.join(output_dir, "Dockerfile"), "w") as f:
        f.write(f"""FROM node:20-slim

WORKDIR /app

COPY package*.json ./
RUN npm ci --ignore-scripts && npm cache clean --force
COPY . .

{"".join([f"ARG {e['name']}\n" for e in envs])}
ARG PORT

ENV {" \\\n    ".join([f"{e['name']}=${{{e['name']}}}" for e in envs])} \\
    PORT=${{PORT}}

EXPOSE ${{PORT}}

USER node
CMD ["node", "dist/main", "--port", "${{PORT}}"]
""")

    # K8S Deployment YAML
    with open(os.path.join(k8s_dir, f"{app_name}.yaml"), "w") as f:
        f.write(f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {app_name}
  namespace: pnud-agvm
  labels:
    app: {app_name}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {app_name}
  template:
    metadata:
      labels:
        app: {app_name}
    spec:
      containers:
        - name: {app_name}
          image: ${{FULL_IMAGE_NAME}}
          imagePullPolicy: Always
          ports:
            - containerPort: {port}
              name: http
          envFrom:
            - secretRef:
                name: {app_name}-secret
          resources:
            requests:
              cpu: "200m"
              memory: "256Mi"
            limits:
              cpu: "1000m"
              memory: "1Gi"
          livenessProbe:
            httpGet:
              path: /{app_name}
              port: http
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /{app_name}
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 3
          securityContext:
            runAsNonRoot: true
            runAsUser: 1000
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
      imagePullSecrets:
        - name: harbor-registry-secret
""")

    # K8S Service YAML
    with open(os.path.join(k8s_dir, f"{app_name}-service.yaml"), "w") as f:
        f.write(f"""apiVersion: v1
kind: Service
metadata:
  name: {app_name}-service
  namespace: pnud-agvm
spec:
  type: NodePort
  selector:
    app: {app_name}
  ports:
    - protocol: TCP
      port: {port}
      targetPort: {port}
      nodePort: {node_port}
""")

    # K8S HPA YAML
    with open(os.path.join(k8s_dir, f"{app_name}-hpa.yaml"), "w") as f:
        f.write(f"""apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {app_name}-hpa
  namespace: pnud-agvm
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {app_name}
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
""")

    # K8S Secret YAML
def write_secret_yaml(app_name, var_names, output_path):
    with open(output_path, "w") as f:
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

    # Jenkinsfile
    with open(os.path.join(output_dir, "Jenkinsfile"), "w") as f:
        f.write(f"""pipeline {{
    agent any
    environment {{
        REGISTRY         = 'harbor.tsirylab.com'
        HARBOR_PROJECT   = 'pnud-agvm'
        IMAGE_NAME       = '{app_name}'
        IMAGE_TAG        = "\\${{BUILD_NUMBER}}"
        FULL_IMAGE_NAME  = "\\${{REGISTRY}}/\\${{HARBOR_PROJECT}}/\\${{IMAGE_NAME}}:\\${{IMAGE_TAG}}"
        NAMESPACE        = 'pnud-agvm'
        K8S_DIR          = 'k8s'
        DEPLOYMENT_NAME  = '{app_name}'
        SERVICE_NAME     = '{app_name}-service'
        HPA_NAME         = '{app_name}-hpa'
        SECRET_NAME      = '{app_name}-secret'
        PORT             = '{port}'
        NODE_PORT        = '{node_port}'
{"".join([f"        {e['name']} = ''\n" for e in envs])}
    }}
    stages {{
        stage('Build & Push') {{
            steps {{
                withCredentials([
                    usernamePassword(credentialsId: 'harbor-credentials',
                                     usernameVariable: 'HARBOR_USER',
                                     passwordVariable: 'HARBOR_PASS'),\n""")
        # Credentials mapping
        for e in envs:
            f.write(f"                    string(credentialsId: '{e['secret_id']}', variable: '{e['name']}'),\n")
        f.write(f"""                ]) {{
                    sh '''
                        set -e
                        docker logout \\${{REGISTRY}} || true
                        docker build \\
""")
        for e in envs:
            f.write(f"                          --build-arg {e['name']}=\"\\${{{e['name']}}}\" \\\n")
        f.write(
            f"""                          --build-arg PORT={port} \\
                          -t \\${{FULL_IMAGE_NAME}} .
                        echo \\${{HARBOR_PASS}} | \\
                          docker login -u \\${{HARBOR_USER}} --password-stdin \\${{REGISTRY}}
                        docker push \\${{FULL_IMAGE_NAME}}
                        docker logout \\${{REGISTRY}}
                    '''
                }}
            }}
        }}
        stage('Deploy') {{
            steps {{
                withCredentials([
                    file(credentialsId: 'kubeconfig-jenkins', variable: 'KUBECONFIG'),
                    usernamePassword(credentialsId: 'harbor-credentials',
                                     usernameVariable: 'HARBOR_USER',
                                     passwordVariable: 'HARBOR_PASS'),\n""")
        for e in envs:
            f.write(f"                    string(credentialsId: '{e['secret_id']}', variable: '{e['name']}'),\n")
        f.write(f"""                ]) {{
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
""")
        for e in envs:
            f.write(f"                          --from-literal={e['name']}=\"\\${{{e['name']}}}\" \\\n")
        f.write("""                          --namespace=\\${NAMESPACE}

                        for res in deployment service hpa; do
                            envsubst < \\${K8S_DIR}/""" + f"{app_name}" + """-${res}.yaml > /tmp/""" + f"{app_name}" + """-${res}.yaml
                            kubectl apply -f /tmp/""" + f"{app_name}" + """-${res}.yaml
                        done

                        kubectl rollout status deployment/""" + f"{app_name}" + """ -n \\${NAMESPACE} --timeout=120s
                        kubectl get pods -n \\${NAMESPACE} -l app=""" + f"{app_name}" + """
                    '''
                }}
            }}
        }}
    }}
    post {{ always {{ cleanWs() }} }}
}}
""")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    app_name = data.get("app_name")
    port = data.get("port")
    node_port = data.get("node_port")
    envs = data.get("envs", [])
    output_dir = os.path.join("generated", app_name)
    try:
        generate_files(app_name, port, node_port, envs, output_dir)
        return jsonify({"success": True, "message": f"Fichiers générés dans {output_dir}"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)