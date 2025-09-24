#!/usr/bin/env bash
set -euo pipefail

# =============================================
# DevSecOps Deployment Generator
# Auteur: [Ton Nom]
# Date: $(date '+%Y-%m-%d')
# Description: Génère une arborescence de déploiement sécurisée pour Kubernetes/Docker/Jenkins.
# =============================================

# --------------------------------------------
# CONSTANTES ET VALEURS PAR DÉFAUT
# --------------------------------------------
readonly DEFAULT_NAMESPACE="pnud-agvm"
readonly DEFAULT_VITE_API_URL="https://api.example.com"
readonly DEFAULT_VITE_APP_CLIENT_ID="default-client-id"
readonly CONFIG_FILE=".env"
readonly SCRIPT_VERSION="1.1.0"

# --------------------------------------------
# FONCTIONS UTILITAIRES
# --------------------------------------------

# Affiche l'usage du script
usage() {
  cat <<EOF
Usage: $0 --app <name> --port <port> [--namespace <namespace>] [--config <file>]

Options:
  --app       Nom de l'application (requis)
  --port      Numéro de port (requis)
  --namespace Namespace Kubernetes (défaut: $DEFAULT_NAMESPACE)
  --config    Fichier de configuration (défaut: $CONFIG_FILE)
  --help      Affiche cette aide

Exemple:
  $0 --app mon-app --port 8080 --namespace mon-namespace --config .env.prod
EOF
  exit 1
}

# Journalisation avec horodatage
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Valide qu'une valeur est numérique
validate_numeric() {
  local input=$1
  local name=$2
  if ! [[ "$input" =~ ^[0-9]+$ ]]; then
    log "ERREUR: $name doit être une valeur numérique"
    exit 1
  fi
}

# Charge les variables d'environnement depuis un fichier
load_config() {
  local config_file=$1
  if [[ -f "$config_file" ]]; then
    log "Chargement des variables depuis $config_file"
    set -a
    # shellcheck disable=SC1090
    source "$config_file"
    set +a
  else
    log "ATTENTION: Fichier $config_file non trouvé, utilisation des valeurs par défaut"
  fi
  # Valeurs par défaut si non définies
  VITE_API_URL=${VITE_API_URL:-$DEFAULT_VITE_API_URL}
  VITE_APP_CLIENT_ID=${VITE_APP_CLIENT_ID:-$DEFAULT_VITE_APP_CLIENT_ID}
}

# Remplace les variables dans un template
render() {
  local src="$1"
  local dst="$2"
  log "Génération de $dst depuis $src"
  envsubst '$APP,$PORT,$NAMESPACE' < "$src" > "$dst"
  chmod 640 "$dst"  # Restreint les permissions
}

# --------------------------------------------
# PARSEUR D'ARGUMENTS
# --------------------------------------------
APP=""
PORT=""
NAMESPACE="$DEFAULT_NAMESPACE"
CONFIG="$CONFIG_FILE"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --app)       APP="$2"; shift 2 ;;
    --port)      PORT="$2"; shift 2 ;;
    --namespace) NAMESPACE="$2"; shift 2 ;;
    --config)    CONFIG="$2"; shift 2 ;;
    --help)      usage ;;
    *)           log "Option inconnue: $1"; usage ;;
  esac
done

# Validation des paramètres requis
[[ -z "$APP" ]] && { log "ERREUR: --app est requis"; usage; }
[[ -z "$PORT" ]] && { log "ERREUR: --port est requis"; usage; }
validate_numeric "$PORT" "Port"

# --------------------------------------------
# CHARGEMENT DE LA CONFIGURATION
# --------------------------------------------
load_config "$CONFIG"
export APP PORT NAMESPACE VITE_API_URL VITE_APP_CLIENT_ID

# --------------------------------------------
# CRÉATION DE L'ARBORESCENCE
# --------------------------------------------
OUT_DIR="$APP"
log "Création de l'arborescence dans $OUT_DIR"
rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"/k8s

# --------------------------------------------
# GÉNÉRATION DES FICHIERS
# --------------------------------------------

# --- Dockerfile ---
log "Génération du Dockerfile (build sécurisé + user non-root)"
cat > "$OUT_DIR/Dockerfile" <<'DOCKERFILE'
# ---------- Build ----------
FROM node:20.11.1-slim AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev && npm cache clean --force
COPY . .
ARG VITE_API_URL
ARG VITE_APP_CLIENT_ID
ARG VITE_PORT
ENV VITE_API_URL=$VITE_API_URL \
    VITE_APP_CLIENT_ID=$VITE_APP_CLIENT_ID \
    VITE_PORT=$VITE_PORT
RUN npm run build

# ---------- Run ----------
FROM nginxinc/nginx-unprivileged:1.25.3-alpine
USER 101
WORKDIR /usr/share/nginx/html
COPY --from=builder --chown=101:101 /app/dist .
COPY nginx.conf /etc/nginx/conf.d/default.conf
ENV PORT=$VITE_PORT
EXPOSE $VITE_PORT
CMD ["nginx", "-g", "daemon off;"]
DOCKERFILE

# --- nginx.conf (sécurisé) ---
log "Génération de nginx.conf (headers de sécurité + cache)"
cat > "$OUT_DIR/nginx.conf" <<NGINX
server {
    listen       $PORT;
    server_name  _;
    # Redirections et sécurité
    location = / {
        return 301 /login;
    }
    # Headers de sécurité
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self';" always;
    # Performances
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    root /usr/share/nginx/html;
    index index.html;
    location / {
        try_files \$uri \$uri/ /index.html;
    }
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
NGINX

# --- Manifests Kubernetes ---
log "Génération des manifests Kubernetes (sécurisés)"

# Deployment avec securityContext et probes
cat > "$OUT_DIR/k8s/${APP}-deployment.yaml" <<DEPLOY
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${APP}
  namespace: ${NAMESPACE}
  labels:
    app: ${APP}
    app.kubernetes.io/version: "1.0.0"
  annotations:
    pod-security.kubernetes.io/enforce: "baseline"
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
      securityContext:
        runAsNonRoot: true
        runAsUser: 101
        fsGroup: 101
      containers:
      - name: ${APP}
        image: \${FULL_IMAGE_NAME}
        securityContext:
          readOnlyRootFilesystem: true
          allowPrivilegeEscalation: false
          capabilities:
            drop: ["ALL"]
        ports:
        - containerPort: ${PORT}
          name: http
        envFrom:
        - secretRef:
            name: ${APP}-secret
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "300m"
            memory: "256Mi"
        livenessProbe:
          httpGet:
            path: /login
            port: ${PORT}
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /login
            port: ${PORT}
          initialDelaySeconds: 5
          periodSeconds: 5
      imagePullSecrets:
      - name: harbor-registry-secret
DEPLOY

# Service (NodePort)
cat > "$OUT_DIR/k8s/${APP}-service.yaml" <<SERVICE
apiVersion: v1
kind: Service
metadata:
  name: ${APP}-service
  namespace: ${NAMESPACE}
spec:
  selector:
    app: ${APP}
  ports:
    - protocol: TCP
      port: ${PORT}
      targetPort: ${PORT}
  type: NodePort
SERVICE

# HPA (Auto-scaling)
cat > "$OUT_DIR/k8s/${APP}-hpa.yaml" <<HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ${APP}-hpa
  namespace: ${NAMESPACE}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ${APP}
  minReplicas: 1
  maxReplicas: 3
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
HPA

# NetworkPolicy (restriction réseau)
cat > "$OUT_DIR/k8s/${APP}-network-policy.yaml" <<NETPOL
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ${APP}-network-policy
  namespace: ${NAMESPACE}
spec:
  podSelector:
    matchLabels:
      app: ${APP}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: ${APP}
    ports:
    - protocol: TCP
      port: ${PORT}
  egress:
  - to:
    - ipBlock:
        cidr: 0.0.0.0/0
    ports:
    - protocol: TCP
      port: 443
NETPOL

# SealedSecret (chiffré)
cat > "$OUT_DIR/k8s/${APP}-sealed-secret.yaml" <<SEALED_SECRET
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: ${APP}-secret
  namespace: ${NAMESPACE}
  annotations:
    sealedsecrets.bitnami.com/cluster-wide: "true"
spec:
  encryptedData:
    VITE_API_URL: <à-remplacer-par-kubeseal>
    VITE_APP_CLIENT_ID: <à-remplacer-par-kubeseal>
  template:
    metadata:
      name: ${APP}-secret
      namespace: ${NAMESPACE}
SEALED_SECRET

# --- Jenkinsfile (pipeline CI/CD sécurisé) ---
log "Génération du Jenkinsfile (scan + validation)"
cat > "$OUT_DIR/Jenkinsfile" <<'JENKINS'
pipeline {
    agent any
    environment {
        REGISTRY         = 'harbor.tsirylab.com'
        HARBOR_PROJECT   = '${NAMESPACE}'
        IMAGE_NAME       = '${APP}'
        IMAGE_TAG        = "${BUILD_NUMBER}"
        FULL_IMAGE_NAME  = "${REGISTRY}/${HARBOR_PROJECT}/${IMAGE_NAME}:${IMAGE_TAG}"
        K8S_DIR          = 'k8s'
    }
    stages {
        stage('Build & Push') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'harbor-credentials', usernameVariable: 'HARBOR_USER', passwordVariable: 'HARBOR_PASS')]) {
                    sh '''
                        docker build --build-arg VITE_API_URL=${VITE_API_URL} \
                                     --build-arg VITE_PORT=${PORT} \
                                     --build-arg VITE_APP_CLIENT_ID=${VITE_APP_CLIENT_ID} \
                                     -t ${FULL_IMAGE_NAME} .
                        echo ${HARBOR_PASS} | docker login -u ${HARBOR_USER} --password-stdin ${REGISTRY}
                        docker push ${FULL_IMAGE_NAME}
                    '''
                }
            }
        }
        stage('Scan & Validate') {
            steps {
                sh '''
                    docker pull ${FULL_IMAGE_NAME}
                    trivy image --exit-code 1 --severity CRITICAL ${FULL_IMAGE_NAME}
                    kubeval --strict ${K8S_DIR}
                '''
            }
        }
        stage('Deploy') {
            steps {
                withCredentials([
                    file(credentialsId: 'kubeconfig-jenkins', variable: 'KUBECONFIG'),
                    usernamePassword(credentialsId: 'harbor-credentials', usernameVariable: 'HARBOR_USER', passwordVariable: 'HARBOR_PASS')
                ]) {
                    sh '''
                        export KUBECONFIG=${KUBECONFIG}
                        kubectl apply -f ${K8S_DIR}/${IMAGE_NAME}-sealed-secret.yaml
                        for m in deployment service hpa network-policy; do
                            envsubst '\${FULL_IMAGE_NAME}' < ${K8S_DIR}/${IMAGE_NAME}-${m}.yaml | kubectl apply -f -
                        done
                        kubectl rollout status deployment/${IMAGE_NAME} -n ${NAMESPACE} --timeout=120s
                    '''
                }
            }
        }
    }
    post { always { cleanWs() } }
}
JENKINS

# --- README.md (documentation) ---
log "Génération de la documentation (README.md)"
cat > "$OUT_DIR/README.md" <<README
# Déploiement de l'application ${APP}

## Structure du projet
\`\`\`
${OUT_DIR}/
├── Dockerfile          # Image Docker sécurisée (non-root + alpine)
├── nginx.conf          # Configuration Nginx (headers de sécurité)
├── k8s/
│   ├── ${APP}-deployment.yaml    # Déploiement Kubernetes (securityContext, probes)
│   ├── ${APP}-service.yaml       # Service NodePort
│   ├── ${APP}-hpa.yaml           # Auto-scaling horizontal
│   ├── ${APP}-network-policy.yaml # Restrictions réseau
│   └── ${APP}-sealed-secret.yaml # Secrets chiffrés (à générer avec kubeseal)
└── Jenkinsfile         # Pipeline CI/CD (build, scan, deploy)

## Prérequis
- Kubernetes 1.25+
- kubeseal (pour chiffrer les secrets)
- trivy (scan de vulnérabilités)
- kubeval (validation des manifests)

## Déploiement
1. Chiffrer les secrets:
   \`\`\`bash
   kubeseal --cert sealed-secrets-cert.pem < secret.yaml > ${APP}-sealed-secret.yaml
   \`\`\`
2. Lancer le pipeline Jenkins:
   \`\`\`bash
   jenkins build ${APP}-deploy
   \`\`\`

## Sécurité
- Images scannées avec Trivy.
- Pods exécutés en non-root avec securityContext restrictif.
- NetworkPolicy pour limiter le trafic réseau.
- Secrets chiffrés avec SealedSecret.
README

# --------------------------------------------
# FIN DU SCRIPT
# --------------------------------------------
log "✅ Génération terminée dans: $OUT_DIR"
log "Prochaines étapes:"
log "  1. Chiffrer les secrets avec kubeseal"
log "  2. Configurer le pipeline Jenkins"
log "  3. Déployer avec: kubectl apply -f $OUT_DIR/k8s/"
