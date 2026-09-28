# DevSecOps — Générateur & AI GitOps

> Factory DevSecOps pour microservices **Node / Python / Java / Go** — Génération automatique `Dockerfile` + `Kubernetes` + `Jenkinsfile` à partir d'une UI ou d'une URL GitHub.

[![Python](https://img.shields.io/badge/Python-3.11+-blue)](app.py)
[![Flask](https://img.shields.io/badge/Flask-3.1-green)](app.py)
[![Docker](https://img.shields.io/badge/Docker-20+-2496ED)](generate-deployment.sh)
[![K8s](https://img.shields.io/badge/Kubernetes-1.25+-326CE5)](generate-deployment.sh)
[![Jenkins](https://img.shields.io/badge/Jenkins-Pipeline-D24939)](app.py)

---

## Sommaire

- [Vue d'ensemble](#vue-densemble)
- [Architecture](#architecture)
- [Structure du projet](#structure-du-projet)
- [Module 1 — Générateur classique](#module-1--générateur-classique)
- [Module 2 — AI GitOps](#module-2--ai-gitops)
- [Installation](#installation)
- [Lancement](#lancement)
- [Utilisation](#utilisation)
- [API](#api)
- [Base de connaissance & conformité](#base-de-connaissance--conformité)
- [Sécurité DevSecOps](#sécurité-devsecops)
- [Exemples](#exemples)
- [Roadmap](#roadmap)

---

## Vue d'ensemble

Monorepo contenant **16+ microservices** (`urbanisme/matac`, `recette-locale/serviceregis`, `mobilite_urbaine/service-flotte`, ...) et une **factory** qui génère de façon uniforme :

| Artefact | Contenu |
|----------|---------|
| `Dockerfile` | `node:20-slim`, `USER node`, `ARG/ENV`, `EXPOSE ${PORT}` |
| `k8s/` | `Deployment` (probes, resources, securityContext), `Service NodePort`, `HPA`, `Secret` |
| `Jenkinsfile` | Pipeline Harbor `harbor.tsirylab.com` + mode `k3s` ou `docker run` |

Deux interfaces :

1. **Générateur classique** `templates/index.html` → saisie `name_images` + `PORT` + `variables d'environnement`
2. **AI GitOps** `ai-git-ops/` → saisie `URL GitHub` → détection `Dockerfile` → audit conformité → génération `Jenkinsfile` bi-mode

---

## Architecture

```mermaid
flowchart TB
    subgraph UI
        A[templates/index.html\nGénérateur classique]
        B[ai-git-ops/templates/index.html\nAI GitOps]
    end
    subgraph Backend[Flask app.py :5000]
        A --> C[POST /generate]
        B --> D[POST /api/analyze]
        B --> E[POST /api/generate-jenkinsfile]
        C --> F[generate_files()\nDockerfile + k8s + Jenkinsfile]
        D --> G[github_detector\n+ dockerfile_analyzer]
        E --> H[jenkins_generator\nk3s vs docker]
    end
    subgraph Sortie
        F --> I[generated/<app>/]
        H --> J[Jenkinsfile preview]
    end
```

**Flux AI GitOps détaillé :**

```mermaid
flowchart LR
    U[URL GitHub] --> P[parse_github_url]
    P --> R[GET /repos/:owner/:repo\ndefault_branch]
    R --> L[GET /contents\nfile_list]
    R --> DF{detect_dockerfile\nDockerfile|docker/Dockerfile}
    DF -->|trouvé| RW[fetch raw Dockerfile]
    DF -->|manquant| UNK[tech=unknown]
    RW --> AN[analyze_dockerfile\nscore 0-100]
    AN --> MO{mode}
    MO -->|k3s| JK[kubectl apply]
    MO -->|docker| JD[docker run]
```

---

## Structure du projet

```
devsecops/
├── app.py                              # Flask principal :5000 (générateur + AI GitOps intégré)
├── templates/index.html                # UI classique (name_images, PORT, envs)
├── static/{style.css,script.js}        # Assets UI classique
├── ai-git-ops/                         # Module AI GitOps
│   ├── app.py                          # Standalone :5001 (ou importé par app.py)
│   ├── core/
│   │   ├── knowledge_base.json         # Règles tech + templates k3s/docker
│   │   ├── github_detector.py          # GitHub API + raw
│   │   ├── dockerfile_analyzer.py      # Audit conformité
│   │   └── jenkins_generator.py        # Templates Jenkinsfile
│   ├── templates/index.html
│   ├── static/{style.css,script.js}
│   └── requirements.txt
├── generate-backend.sh                 # Générateur bash backend (DB_HOST etc.)
├── generate-backend-zaka.sh            # Variante POSTGRES_HOST
├── generate-deployment.sh              # Générateur frontend sécurisé (multi-stage, nginx, NetworkPolicy, SealedSecret, Trivy)
├── generate-deployment-without-k8s.sh  # Variante sans k8s (même base)
├── generated/                          # Sortie du générateur (Dockerfile + k8s + Jenkinsfile)
├── urbanisme/                          # 6 services : matac, matac-commune, servicecarto...
├── recette-locale/                     # 4 services : servicetsena, serviceregis...
├── mobilite_urbaine/service-flotte/
├── EMIT/, emilib/, CHUA/, agm/, BackCMS/, etc.  # Autres domaines
└── README.md
```

---

## Module 1 — Générateur classique

**Fichiers :** `app.py:24` `generate_files()`, `templates/index.html:24`, `static/script.js:62`

| Input | Description |
|-------|-------------|
| `name_images` | Nom image Docker + `app` K8s + dossier `generated/` (sanitize `a-z0-9-_`) |
| `PORT Container` | `containerPort` + `EXPOSE` + `ARG PORT` (1-65535) |
| `NodePort` | Optionnel `30000-32767`, défaut `30130` |
| `Variables d'environnement` | `Nom` (UPPER_SNAKE) + `Valeur` + `Credential Jenkins ID` (auto `NAME_ID` si vide) |

**Génération :** `POST /generate` → `generated/<app>/Dockerfile`, `k8s/<app>.yaml`, `k8s/<app>-service.yaml`, `k8s/<app>-hpa.yaml`, `Jenkinsfile` (Harbor `harbor.tsirylab.com/pnud-agvm`).

**Bash alternatifs :**
```bash
./generate-backend.sh --app mon-api --port 3000 --db-host pg.svc --db-port 5432 --db-user user --db-password pwd --db-name mydb --base-url https://api.com
./generate-deployment.sh --app mon-front --port 4015 --namespace pnud-agvm
```

---

## Module 2 — AI GitOps

**Dossier :** `ai-git-ops/` — détaillé dans `ai-git-ops/README.md`

### Fonctionnement

1. **Saisie URL** `https://github.com/org/repo` (supporte `.git`, `/tree/main`, `git@github.com:org/repo.git`) → `core/github_detector.py:18` `parse_github_url()`
2. **Détection** `detect_dockerfile()` cherche `Dockerfile`, `docker/Dockerfile`, `build/Dockerfile` via `GET /repos/:owner/:repo/contents` + fallback `raw.githubusercontent.com` HEAD
3. **Conformité** `core/dockerfile_analyzer.py:18` `analyze_dockerfile()` :

| Règle | Sévérité |
|-------|----------|
| `FROM` sans `:latest` | `critical` |
| `USER` non-root (`node`/`101`/`1000`) | `critical`/`warning` |
| `EXPOSE` présent, correspond à `PORT` | `warning` |
| `ARG PORT` | `warning` |
| Multi-stage `AS` | `info` |
| Pas de secrets en dur `ENV PASSWORD=...` | `critical` |

Score `100 - 25*critical - 10*warning`, `compliant = critical==0 && score>=70`. Tech détectée via `FROM node/python/eclipse-temurin/golang` ou `package.json/requirements.txt/pom.xml/go.mod`.

4. **Génération** `core/jenkins_generator.py:12` :

- **k3s** `generate_k3s_jenkinsfile()` : `docker build --build-arg` → `docker push Harbor` → `kubectl create secret docker-registry harbor-registry-secret` + `generic <app>-secret --from-literal` → `envsubst < k8s/*.yaml | kubectl apply` → `rollout status`
- **docker** `generate_docker_jenkinsfile()` : même build/push → `docker stop/rm` → `docker run -d --restart unless-stopped -p PORT:PORT -e VAR`

Env vars injectés en `withCredentials(string(credentialsId: ..., variable: ...))`.

---

## Installation

```bash
# Prérequis : Python 3.11+, pip
pip install flask requests

# Optionnel pour ai-git-ops standalone
pip install -r ai-git-ops/requirements.txt
```

Aucune autre dépendance. `requests` requis uniquement pour AI GitOps (GitHub API).

---

## Lancement

### Mode intégré (recommandé) — un seul serveur

```bash
python app.py
# http://localhost:5000/              -> Générateur classique
# http://localhost:5000/ai-git-ops    -> AI GitOps
```

`app.py:9` détecte `ai-git-ops/` et monte automatiquement `/ai-git-ops`, `/api/analyze`, `/api/generate-jenkinsfile`.

### Mode standalone AI GitOps

```bash
python ai-git-ops/app.py
# http://localhost:5001/
```

Les deux peuvent cohabiter (5000 + 5001).

---

## Utilisation

### UI classique

1. Ouvrir `http://localhost:5000/`
2. Renseigner `Nom de l'image` (ex: `servicetsena`), `PORT` (ex: `3000`)
3. Ajouter variables (`DB_HOST` / `postgres.svc` / `POSTGRES_HOST_ID`)
4. `🎯 Générer` → `generated/servicetsena/` prêt à `docker build` / `kubectl apply`

### UI AI GitOps

1. Ouvrir `http://localhost:5000/ai-git-ops` (ou `:5001`)
2. Coller `URL GitHub` (ex: `https://github.com/org/repo`), optionnel `Token ghp_xxx` pour privé, `PORT`
3. `🔍 Analyser` → rapport `score 0-100`, `technology`, `checks`, preview Dockerfile
4. Choisir mode `☸️ K3s` ou `🐳 Docker run`, compléter `envs` si besoin
5. `🏗️ Générer` → `📋 Copier` / `⬇️ Télécharger Jenkinsfile`

---

## API

### Générateur classique

| Endpoint | Méthode | Body | Réponse |
|----------|---------|------|---------|
| `/` | `GET` | - | `index.html` |
| `/generate` | `POST` | `{app_name|name_images, port|port_container, node_port?, envs:[{name,value,secret_id}]}` | `{success, message, app, port, envs}` |

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"name_images":"demo-app","port_container":"3000","envs":[{"name":"DB_HOST","value":"db","secret_id":"PG_HOST"}]}'
```

### AI GitOps

| Endpoint | Body | Réponse |
|----------|------|---------|
| `POST /api/analyze` | `{github_url, token?, port?}` | `{success, data:{repo, branch, language, file_list, dockerfile{found,path,raw_url,content_preview}, analysis{technology,score,compliant,checks}}}` |
| `POST /api/generate-jenkinsfile` | `{mode:"k3s"|"docker", github_url?, app_name?, port?, node_port?, envs?}` | `{success, mode, app_name, jenkinsfile, docker_info}` |

```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"github_url":"https://github.com/docker/getting-started","port":"3000"}'

curl -X POST http://localhost:5000/api/generate-jenkinsfile \
  -H "Content-Type: application/json" \
  -d '{"mode":"k3s","github_url":"https://github.com/org/demo","app_name":"demo-app","port":"3000","envs":[{"name":"DB_HOST","secret_id":"PG_HOST"}]}'
```

---

## Base de connaissance & conformité

`ai-git-ops/core/knowledge_base.json` :

- **registry** `harbor.tsirylab.com`, **project** `pnud-agvm`, **namespace** `pnud-agvm`
- **Technologies** `node` (`node:20-slim`), `python` (`python:3.11-slim`), `java` (`eclipse-temurin:17-jre-alpine`), `go` (`golang:1.21-alpine`) avec `patterns`, `build_cmd`, `compliance_rules`
- **Modes** `k3s` (requires `harbor-credentials`, `kubeconfig-jenkins`) et `docker`

Étendre : ajouter entrée dans `technologies` + règle dans `compliance_global`.

---

## Sécurité DevSecOps

Implémenté dans les templates générés :

- `USER node` / `101`, `runAsNonRoot: true`, `readOnlyRootFilesystem: true`, `allowPrivilegeEscalation: false`, `capabilities.drop: [ALL]` (`app.py:87`)
- `resources` requests/limits, `livenessProbe`/`readinessProbe`
- `HPA` `autoscaling/v2` CPU 50%
- `NetworkPolicy` + `SealedSecret` dans `generate-deployment.sh:289` (frontend)
- `Trivy` + `kubeval` dans `generate-deployment.sh:371` (scan stage)

À activer : `Harbor` credentials `harbor-credentials`, `kubeconfig-jenkins`, `SealedSecrets` via `kubeseal`.

---

## Exemples

- `https://github.com/nodejs/docker-node` → `FROM node:20-slim` → `score 100 compliant`
- `FROM node:latest` sans `USER` → `score 55 non compliant` (critical `FROM :latest` + warning `USER`)
- Repo sans Dockerfile + `package.json` → `tech node`, proposition génération Dockerfile par défaut
- Privé → fournir `token ghp_...` (header `Authorization: token`)

---

## Roadmap

- [ ] Helm chart / Kustomize pour factoriser les 386 `*.yaml` dupliqués
- [ ] GitOps ArgoCD/Flux au lieu de `kubectl apply` Jenkins
- [ ] HDOLint lib, SAST Semgrep/Sonar, SCA Snyk, SBOM Syft + Cosign
- [ ] Vault / External Secrets Operator
- [ ] OPA/Gatekeeper, Trivy systématique, OWASP ZAP DAST
- [ ] Prometheus/Grafana/Loki, tests Jest/Supertest/Playwright, cache Redis GitHub API, bouton `Créer PR`

---

## Développement

```bash
python -m py_compile app.py ai-git-ops/app.py ai-git-ops/core/*.py
python -m flask --app app run --debug          # :5000
python -m flask --app ai-git-ops/app run --port 5001 --debug
```

Structure des tests manuels : `ai-git-ops/README.md:9` + `C:\Users\randr\AppData\Local\Temp\opencode\test_ai.py`.

---

*Généré pour PNUD-AGVM — `app.py:24` `generate_files()`, `ai-git-ops/core/`*
