# Guide de déploiement avec le Helm Chart

## Prérequis

- Helm 3.x installé
- kubectl configuré avec accès au cluster Kubernetes
- Accès au registre Harbor

## Déploiement rapide

### 1. Frontend (criv-client)

```bash
# Depuis la racine du projet
helm install criv-client ./helm -f helm/examples/criv-client-values.yaml

# Vérifier le déploiement
kubectl get pods -n pnud-agvm
kubectl get svc -n pnud-agvm
```

### 2. Backend (serviceforum)

```bash
# Depuis la racine du projet
helm install serviceforum ./helm -f helm/examples/serviceforum-values.yaml

# Vérifier le déploiement
kubectl get pods -n pnud-agvm
kubectl get hpa -n pnud-agvm
```

## Mise à jour d'un déploiement existant

```bash
# Modifier votre fichier values.yaml
# Puis mettre à jour:
helm upgrade criv-client ./helm -f helm/examples/criv-client-values.yaml

# Vérifier l'historique
helm history criv-client
```

## Rollback en cas de problème

```bash
# Revenir à la version précédente
helm rollback criv-client

# Ou revenir à une version spécifique
helm rollback criv-client 1
```

## Variables d'environnement dynamiques

Pour passer des variables d'environnement sans modifier le fichier values.yaml :

```bash
helm install my-service ./helm \
  --set image.repository=my-app \
  --set image.tag=v1.0.0 \
  --set envFromSecret.data.DB_HOST=postgres.prod.svc \
  --set envFromSecret.data.DB_PASSWORD=secret123
```

## Utilisation dans un pipeline CI/CD

### Exemple avec Jenkins

```groovy
stage('Deploy to K8s') {
    steps {
        script {
            sh """
                helm upgrade --install ${SERVICE_NAME} ./helm \
                  --set image.repository=${IMAGE_REPO} \
                  --set image.tag=${IMAGE_TAG} \
                  --set namespace.name=${NAMESPACE} \
                  --set envFromSecret.data.DB_HOST=${DB_HOST} \
                  --set envFromSecret.data.DB_PASSWORD=${DB_PASSWORD} \
                  --wait --timeout 5m
            """
        }
    }
}
```

### Exemple avec GitLab CI

```yaml
deploy:
  stage: deploy
  script:
    - helm upgrade --install $CI_PROJECT_NAME ./helm
        --set image.repository=$CI_REGISTRY_IMAGE
        --set image.tag=$CI_COMMIT_SHORT_SHA
        --set namespace.name=$KUBE_NAMESPACE
        --wait --timeout 5m
  only:
    - main
```

## Debug et troubleshooting

### Vérifier le template avant déploiement

```bash
helm template my-service ./helm -f my-values.yaml > output.yaml
cat output.yaml
```

### Mode dry-run avec debug

```bash
helm install my-service ./helm -f my-values.yaml --dry-run --debug
```

### Vérifier les valeurs appliquées

```bash
helm get values my-service
```

### Voir tous les manifests déployés

```bash
helm get manifest my-service
```

## Désinstallation

```bash
# Désinstaller complètement
helm uninstall criv-client

# Garder l'historique
helm uninstall criv-client --keep-history
```

## Tips et bonnes pratiques

1. **Toujours tester en dry-run d'abord**
   ```bash
   helm install my-service ./helm -f my-values.yaml --dry-run
   ```

2. **Utiliser des namespaces séparés par environnement**
   ```yaml
   namespace:
     name: production  # ou staging, development
   ```

3. **Versionner vos fichiers values**
   - Committez vos fichiers `*-values.yaml` dans Git
   - Utilisez GitOps pour la gestion des déploiements

4. **Sécuriser les secrets**
   - Ne committez jamais les mots de passe dans Git
   - Utilisez des outils comme Sealed Secrets ou External Secrets
   - Ou passez les secrets via `--set` dans le pipeline

5. **Monitorer les déploiements**
   ```bash
   # Suivre le déploiement en temps réel
   kubectl rollout status deployment/my-service -n namespace
   
   # Voir les logs
   kubectl logs -f deployment/my-service -n namespace
   ```
