#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 --app <nom> --port <PORT>"
  echo "       --db-host <host> --db-port <port>"
  echo "       --db-user <user> --db-password <pwd>"
  echo "       --db-name <name> --base-url <url>"
  exit 1
}

# -----------------------------------------------------------
# 1. Parsing CLI
# -----------------------------------------------------------
APP=""
PORT=""
POSTGRES_HOST=""
POSTGRES_PORT=""
POSTGRES_USER=""
POSTGRES_PASSWORD=""
POSTGRES_DB=""
IMAGE_URL=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --app)         APP="$2"; shift 2 ;;
    --port)        PORT="$2"; shift 2 ;;
    --db-host)     POSTGRES_HOST="$2"; shift 2 ;;
    --db-port)     POSTGRES_PORT="$2"; shift 2 ;;
    --db-user)     POSTGRES_USER="$2"; shift 2 ;;
    --db-password) POSTGRES_PASSWORD="$2"; shift 2 ;;
    --db-name)     POSTGRES_DB="$2"; shift 2 ;;
    --base-url)    IMAGE_URL="$2"; shift 2 ;;
    *) usage ;;
  esac
done

[[ -z $APP || -z $PORT || -z $POSTGRES_HOST || -z $POSTGRES_PORT || \
   -z $POSTGRES_USER || -z $POSTGRES_PASSWORD || -z $POSTGRES_DB || -z $IMAGE_URL ]] && usage

OUT_DIR="$APP"
rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"/k8s

export APP PORT POSTGRES_HOST POSTGRES_PORT POSTGRES_USER POSTGRES_PASSWORD POSTGRES_DB IMAGE_URL

# -----------------------------------------------------------
# 2. Dockerfile
# -----------------------------------------------------------
cat > "$OUT_DIR/Dockerfile" <<DOCKERFILE
FROM node:20-slim

WORKDIR /app

COPY package*.json ./
RUN npm ci --ignore-scripts && npm cache clean --force
COPY . .

ARG POSTGRES_HOST
ARG POSTGRES_PORT
ARG POSTGRES_USERNAME
ARG POSTGRES_PASSWORD
ARG DB_DATABASE
ARG IMAGE_URL
ARG PORT

ENV POSTGRES_HOST=\${POSTGRES_HOST} \
    POSTGRES_PORT=\${POSTGRES_PORT} \
    POSTGRES_USERNAME=\${POSTGRES_USERNAME} \
    POSTGRES_PASSWORD=\${POSTGRES_PASSWORD} \
    DB_DATABASE=\${DB_DATABASE} \
    IMAGE_URL=\${IMAGE_URL} \
    PORT=\${PORT}

EXPOSE \${PORT}

USER node
CMD ["node", "dist/main", "--port", "\${PORT}"]
DOCKERFILE

# -----------------------------------------------------------
# 3. Manifestes Kubernetes
# -----------------------------------------------------------
cat > "$OUT_DIR/k8s/${APP}.yaml" <<DEPLOY
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${APP}
  namespace: pnud-agvm
  labels:
    app: ${APP}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ${APP}
  template:
    metadata:
      labels:
        app: ${APP}
    spec:
      containers:
        - name: ${APP}
          image: \${FULL_IMAGE_NAME}
          imagePullPolicy: Always
          ports:
            - containerPort: ${PORT}
              name: http
          envFrom:
            - secretRef:
                name: ${APP}-secret
          resources:
            requests:
              cpu: "200m"
              memory: "256Mi"
            limits:
              cpu: "1000m"
              memory: "1Gi"
          livenessProbe:
            httpGet:
              path: /${APP}
              port: http
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /${APP}
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
DEPLOY

cat > "$OUT_DIR/k8s/${APP}-service.yaml" <<SERVICE
apiVersion: v1
kind: Service
metadata:
  name: ${APP}-service
  namespace: pnud-agvm
spec:
  type: NodePort
  selector:
    app: ${APP}
  ports:
    - protocol: TCP
      port: ${PORT}
      targetPort: ${PORT}
      nodePort: 30130
SERVICE

cat > "$OUT_DIR/k8s/${APP}-hpa.yaml" <<HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ${APP}-hpa
  namespace: pnud-agvm
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ${APP}
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
HPA

cat > "$OUT_DIR/k8s/${APP}-secret.yaml" <<SECRET
apiVersion: v1
kind: Secret
metadata:
  name: ${APP}-secret
  namespace: pnud-agvm
type: Opaque
stringData:
  POSTGRES_HOST: "${POSTGRES_HOST}"
  POSTGRES_PORT: "${POSTGRES_PORT}"
  POSTGRES_USERNAME: "${POSTGRES_USER}"
  POSTGRES_PASSWORD: "${POSTGRES_PASSWORD}"
  DB_DATABASE: "${POSTGRES_DB}"
  IMAGE_URL: "${IMAGE_URL}"
SECRET

# -----------------------------------------------------------
# 4. Jenkinsfile
# -----------------------------------------------------------
cat > "$OUT_DIR/Jenkinsfile" <<JENKINS
pipeline {
    agent any
    environment {
        REGISTRY         = 'harbor.tsirylab.com'
        HARBOR_PROJECT   = 'pnud-agvm'
        IMAGE_NAME       = '${APP}'
        IMAGE_TAG        = "\\\${BUILD_NUMBER}"
        FULL_IMAGE_NAME  = "\\\${REGISTRY}/\\\${HARBOR_PROJECT}/\\\${IMAGE_NAME}:\\\${IMAGE_TAG}"
        NAMESPACE        = 'pnud-agvm'
        K8S_DIR          = 'k8s'
        DEPLOYMENT_NAME  = '${APP}'
        SERVICE_NAME     = '${APP}-service'
        HPA_NAME         = '${APP}-hpa'
        SECRET_NAME      = '${APP}-secret'
        PORT             = '${PORT}'
        POSTGRES_DB      = '${POSTGRES_DB}'
    }
    stages {
        stage('Build & Push') {
            steps {
                withCredentials([
                    usernamePassword(credentialsId: 'harbor-credentials',
                                     usernameVariable: 'HARBOR_USER',
                                     passwordVariable: 'HARBOR_PASS')
                ]) {
                    sh '''
                        set -e
                        docker logout \\\${REGISTRY} || true
                        docker build \
                          --build-arg POSTGRES_HOST="\\\${POSTGRES_HOST}" \
                          --build-arg POSTGRES_PORT="\\\${POSTGRES_PORT}" \
                          --build-arg POSTGRES_USERNAME="\\\${POSTGRES_USERNAME}" \
                          --build-arg POSTGRES_PASSWORD="\\\${POSTGRES_PASSWORD}" \
                          --build-arg DB_DATABASE="\\\${POSTGRES_DB}" \
                          --build-arg IMAGE_URL="\\\${IMAGE_URL}" \
                          --build-arg PORT=${PORT} \
                          -t \\\${FULL_IMAGE_NAME} .
                        echo \\\${HARBOR_PASS} | \
                          docker login -u \\\${HARBOR_USER} --password-stdin \\\${REGISTRY}
                        docker push \\\${FULL_IMAGE_NAME}
                        docker logout \\\${REGISTRY}
                    '''
                }
            }
        }
        stage('Deploy') {
            steps {
                withCredentials([
                    string(credentialsId: 'POSTGRES_HOST_ID', variable: 'POSTGRES_HOST'),
                    string(credentialsId: 'POSTGRES_PORT_ID', variable: 'POSTGRES_PORT'),
                    string(credentialsId: 'POSTGRES_USER_ID', variable: 'POSTGRES_USERNAME'),
                    string(credentialsId: 'POSTGRES_PASSWORD_ID', variable: 'POSTGRES_PASSWORD'),
                    string(credentialsId: 'GATEWAY_URL_ID', variable: 'IMAGE_URL'),
                    file(credentialsId: 'kubeconfig-jenkins', variable: 'KUBECONFIG'),
                    usernamePassword(credentialsId: 'harbor-credentials',
                                     usernameVariable: 'HARBOR_USER',
                                     passwordVariable: 'HARBOR_PASS')
                ]) {
                    sh '''
                        set -e
                        export KUBECONFIG=\\\${KUBECONFIG}

                        kubectl create namespace \\\${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
                        kubectl delete secret harbor-registry-secret -n \\\${NAMESPACE} --ignore-not-found
                        kubectl create secret docker-registry harbor-registry-secret \
                          --docker-server=\\\${REGISTRY} \
                          --docker-username="\\\${HARBOR_USER}" \
                          --docker-password="\\\${HARBOR_PASS}" \
                          --namespace=\\\${NAMESPACE}

                        kubectl delete secret \\\${SECRET_NAME} -n \\\${NAMESPACE} --ignore-not-found
                        kubectl create secret generic \\\${SECRET_NAME} \
                          --from-literal=POSTGRES_HOST="\\\${POSTGRES_HOST}" \
                          --from-literal=POSTGRES_PORT="\\\${POSTGRES_PORT}" \
                          --from-literal=POSTGRES_USERNAME="\\\${POSTGRES_USERNAME}" \
                          --from-literal=POSTGRES_PASSWORD="\\\${POSTGRES_PASSWORD}" \
                          --from-literal=DB_DATABASE="\\\${POSTGRES_DB}" \
                          --from-literal=IMAGE_URL="\\\${IMAGE_URL}" \
                          --namespace=\\\${NAMESPACE}

                        for res in deployment service hpa; do
                            envsubst < \\\${K8S_DIR}/${APP}-\\\${res}.yaml > /tmp/${APP}-\\\${res}.yaml
                            kubectl apply -f /tmp/${APP}-\\\${res}.yaml
                        done

                        kubectl rollout status deployment/${APP} -n \\\${NAMESPACE} --timeout=120s
                        kubectl get pods -n \\\${NAMESPACE} -l app=${APP}
                    '''
                }
            }
        }
    }
    post { always { cleanWs() } }
}
JENKINS

echo "✅ Backend ${APP} généré dans $OUT_DIR"