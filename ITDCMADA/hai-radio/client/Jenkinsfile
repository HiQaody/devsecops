pipeline {
    agent any

    environment {
        CONTAINER_NAME      = 'hai-radio-front'
        IMAGE_NAME          = 'hai-radio-front'
        IMAGE_TAG           = "${BUILD_NUMBER}"
        VITE_PORT           = '3173'
        VITE_API_URL   = 'https://hai-radio-api.itdcmada.com'
        VITE_STREAM_URL = 'https://ton-stream-radio.com/live'
        VITE_APP_NAME = 'HAI-RADIO'

        // Gestion Memory
        MEMORY_LIMIT        = '512m'
        MEMORY_RESERVATION  = '256m'
        CPU_SHARES          = '512'
        
    }

    stages {

        stage('Build Image') {
            steps {
                script {
                    echo "Construction de l'image Docker..."
                    sh '''
                        docker build \
                            --build-arg VITE_PORT=${VITE_PORT} \
                            --build-arg VITE_API_URL=${VITE_API_URL} \
                            --build-arg VITE_STREAM_URL=${VITE_STREAM_URL} \
                            --build-arg VITE_APP_NAME=${VITE_APP_NAME} \
                            -t ${IMAGE_NAME}:${IMAGE_TAG} .
                        
                        echo "Image construite : ${IMAGE_NAME}:${IMAGE_TAG}"
                        docker images | grep ${IMAGE_NAME}
                    '''
                }
            }
        }

        stage('Stop Old Container') {
            steps {
                script {
                    echo "Arrêt de l'ancien conteneur..."
                    sh '''
                        if [ "$(docker ps -aq -f name=${CONTAINER_NAME})" ]; then
                            echo "Conteneur ${CONTAINER_NAME} détecté, arrêt en cours..."
                            docker stop ${CONTAINER_NAME} || true
                            sleep 2
                            docker rm ${CONTAINER_NAME} || true
                            echo "Ancien conteneur supprimé"
                        else
                            echo "Aucun conteneur ${CONTAINER_NAME} en cours d'exécution"
                        fi
                    '''
                }
            }
        }

        stage('Deploy Container') {
            steps {
                script {
                    echo "Déploiement du nouveau conteneur..."
                    sh '''
                        # Démarrer le conteneur
                        docker run -d \
                            --memory ${MEMORY_LIMIT} \
                            --memory-reservation ${MEMORY_RESERVATION} \
                            --cpu-shares ${CPU_SHARES} \
                            --name ${CONTAINER_NAME} \
                            -p ${VITE_PORT}:${VITE_PORT} \
                            --restart unless-stopped \
                            -e VITE_API_URL=${VITE_API_URL} \
                            -e VITE_PORT=${VITE_PORT} \
                            -e VITE_STREAM_URL=${VITE_STREAM_URL} \
                            -e VITE_APP_NAME=${VITE_APP_NAME} \
                            --log-driver json-file \
                            --log-opt max-size=10m \
                            --log-opt max-file=3 \
                            ${IMAGE_NAME}:${IMAGE_TAG}
                        
                        echo "Conteneur démarré"
                        sleep 3
                    '''
                }
            }
        }

    }

    post {
        success {
            script {
                echo "Pipeline terminé avec succès!"
                sh '''
                    echo "Résumé du déploiement :"
                    echo "- Image : ${IMAGE_NAME}:${IMAGE_TAG}"
                    echo "- Conteneur : ${CONTAINER_NAME}"
                    echo "- Port : ${VITE_PORT}"
                    echo "- URL : http://localhost:${VITE_PORT}"
                    echo "- Mémoire : ${MEMORY_LIMIT} (réservation: ${MEMORY_RESERVATION})"
                    echo "- CPU Shares : ${CPU_SHARES}"
                    echo ""
                    echo "Accédez à l'application à http://localhost:${VITE_PORT}"
                '''
            }
        }
        
        failure {
            script {
                echo "Pipeline échoué!"
                sh '''
                    echo "Diagnostique :"
                    echo "--- Logs du conteneur ---"
                    docker logs ${CONTAINER_NAME} 2>&1 | tail -50 || echo "Conteneur non trouvé"
                    echo ""
                    echo "--- Images disponibles ---"
                    docker images | grep ${IMAGE_NAME} || echo "Aucune image trouvée"
                    echo ""
                    echo "--- Conteneurs ---"
                    docker ps -a --filter "name=${CONTAINER_NAME}" || true
                '''
            }
        }

        always {
            script {
                echo "Nettoyage..."
                sh '''
                    # Garder les workspace clean
                    echo "Workspace nettoyé"
                '''
            }
            cleanWs()
        }

        unstable {
            script {
                echo "Pipeline instable"
            }
        }
    }
}
