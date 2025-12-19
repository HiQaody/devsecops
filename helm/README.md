# Microservice Helm Chart

Ce Helm chart permet de déployer facilement des microservices dans Kubernetes avec une configuration réutilisable.

## Description

Ce chart fournit une configuration complète et flexible pour déployer des microservices avec :
- Deployment avec replicas configurables
- Service (NodePort, ClusterIP, LoadBalancer)
- HorizontalPodAutoscaler (HPA) pour l'autoscaling
- Secrets et ConfigMaps pour les variables d'environnement
- Ingress pour l'exposition externe
- Health checks (liveness et readiness probes)
- Security context
- Resource limits et requests

## Installation

### Installation basique

```bash
helm install my-microservice ./helm \
  --set image.repository=my-app \
  --set image.tag=v1.0.0 \
  --set service.port=8080
```

### Installation avec fichier de valeurs personnalisé

```bash
helm install my-microservice ./helm -f my-values.yaml
```

## Exemples d'utilisation

### Exemple 1: Déployer un service frontend (comme criv-client)

Créer un fichier `frontend-values.yaml`:

```yaml
nameOverride: "criv-client"
namespace:
  name: pnud-agvm
  create: true

image:
  registry: harbor.example.com
  repository: criv-client
  tag: latest

service:
  type: NodePort
  port: 4004
  targetPort: 4004
  nodePort: 30040

resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "512Mi"

autoscaling:
  enabled: true
  minReplicas: 1
  maxReplicas: 5
  targetCPUUtilizationPercentage: 80

envFromSecret:
  enabled: true
  createSecret: true
  data:
    VITE_API_URL: "https://api.example.com"
    VITE_PORT: "4004"

livenessProbe:
  httpGet:
    path: /
    port: http
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /
    port: http
  initialDelaySeconds: 5
  periodSeconds: 5
```

Déployer:
```bash
helm install criv-client ./helm -f frontend-values.yaml
```

### Exemple 2: Déployer un service backend (comme serviceforum)

Créer un fichier `backend-values.yaml`:

```yaml
nameOverride: "serviceforum"
namespace:
  name: pnud-agvm
  create: true

image:
  registry: harbor.example.com
  repository: serviceforum
  tag: latest

service:
  type: NodePort
  port: 5015
  targetPort: 5015
  nodePort: 30025

resources:
  requests:
    cpu: "200m"
    memory: "256Mi"
  limits:
    cpu: "1000m"
    memory: "1Gi"

autoscaling:
  enabled: true
  minReplicas: 1
  maxReplicas: 5
  targetCPUUtilizationPercentage: 80

envFromSecret:
  enabled: true
  createSecret: true
  data:
    DB_HOST: "postgres.default.svc.cluster.local"
    DB_PORT: "5432"
    DB_USERNAME: "forumuser"
    DB_PASSWORD: "secure-password"
    DB_DATABASE: "forum_db"
    UPLOAD_URL: "https://upload.example.com"

livenessProbe:
  httpGet:
    path: /serviceforum
    port: http
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /serviceforum
    port: http
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3

securityContext:
  enabled: true
  runAsNonRoot: true
  runAsUser: 1000
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
```

Déployer:
```bash
helm install serviceforum ./helm -f backend-values.yaml
```

### Exemple 3: Déployer avec Ingress

```yaml
nameOverride: "my-api"
namespace:
  name: production
  create: true

image:
  registry: harbor.example.com
  repository: my-api
  tag: v2.0.0

service:
  type: ClusterIP
  port: 8080
  targetPort: 8080

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
  hosts:
    - host: api.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: api-tls
      hosts:
        - api.example.com

envFromSecret:
  enabled: true
  createSecret: true
  data:
    API_KEY: "your-api-key"
    DATABASE_URL: "postgresql://user:pass@host:5432/db"
```

## Paramètres principaux

| Paramètre | Description | Valeur par défaut |
|-----------|-------------|-------------------|
| `nameOverride` | Nom du microservice | `""` |
| `namespace.name` | Nom du namespace | `default` |
| `namespace.create` | Créer le namespace | `true` |
| `image.registry` | Registre Docker | `harbor.example.com` |
| `image.repository` | Nom de l'image | `my-microservice` |
| `image.tag` | Tag de l'image | `latest` |
| `service.type` | Type de service (ClusterIP, NodePort, LoadBalancer) | `NodePort` |
| `service.port` | Port du service | `8080` |
| `service.targetPort` | Port du container | `8080` |
| `autoscaling.enabled` | Activer l'autoscaling | `true` |
| `autoscaling.minReplicas` | Nombre minimum de replicas | `1` |
| `autoscaling.maxReplicas` | Nombre maximum de replicas | `5` |
| `resources.requests.cpu` | CPU demandé | `100m` |
| `resources.requests.memory` | Mémoire demandée | `128Mi` |
| `resources.limits.cpu` | Limite CPU | `500m` |
| `resources.limits.memory` | Limite mémoire | `512Mi` |

## Commandes utiles

### Vérifier la configuration avant déploiement
```bash
helm template my-microservice ./helm -f my-values.yaml
```

### Mettre à jour un déploiement existant
```bash
helm upgrade my-microservice ./helm -f my-values.yaml
```

### Lister les déploiements Helm
```bash
helm list -A
```

### Désinstaller
```bash
helm uninstall my-microservice
```

### Debug
```bash
helm install my-microservice ./helm -f my-values.yaml --dry-run --debug
```

## Structure du chart

```
helm/
├── Chart.yaml              # Métadonnées du chart
├── values.yaml            # Valeurs par défaut
├── .helmignore           # Fichiers à ignorer
├── README.md             # Documentation
└── templates/            # Templates Kubernetes
    ├── _helpers.tpl      # Helpers et fonctions
    ├── namespace.yaml    # Namespace
    ├── deployment.yaml   # Deployment
    ├── service.yaml      # Service
    ├── secret.yaml       # Secret
    ├── configmap.yaml    # ConfigMap
    ├── hpa.yaml          # HorizontalPodAutoscaler
    ├── ingress.yaml      # Ingress
    └── serviceaccount.yaml # ServiceAccount
```

## Migration depuis les configurations K8s existantes

Pour migrer une configuration existante vers ce chart :

1. Identifier les valeurs dans vos fichiers YAML existants
2. Créer un fichier `values.yaml` personnalisé avec ces valeurs
3. Adapter les chemins et noms si nécessaire
4. Tester avec `helm template` avant de déployer

## Support et contribution

Pour toute question ou amélioration, contactez l'équipe DevSecOps.
