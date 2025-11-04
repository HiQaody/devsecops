pipeline {
    agent any

    environment {
        CONTAINER_NAME = 'material-backend'
        IMAGE_NAME = 'material-backend'
        IMAGE_TAG = "${BUILD_NUMBER}"
        PORT = '9095'
        POSTGRES_HOST = credentials('POSTGRES_HOST_ID')
        POSTGRES_PORT = credentials('POSTGRES_PORT_ID')
        POSTGRES_USER = credentials('POSTGRES_USER_ID')
        POSTGRES_PASSWORD = credentials('POSTGRES_PASSWORD_ID')
        POSTGRES_DB = 'chua_material'
        ENCODED_PASSWORD = sh(script: 'echo "${POSTGRES_PASSWORD}" | python3 -c "import urllib.parse; print(urllib.parse.quote(input()))"', returnStdout: true).trim()
        DATABASE_URL = "postgresql://${POSTGRES_USER}:${ENCODED_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}?connect_timeout=10&sslmode=prefer"
        CORS_ORIGIN = 'https://material.chu-andrainjato.mg,http://localhost:5713'
        JWT_SECRET = credentials('JWT_SECRET_ID')
        SALT_ROUNDS = 10
    }

    stages {
        stage('Build container') {
            steps {
                sh '''
                    echo "🛠️ Build de l'image Docker..."
                    docker build \
                      --build-arg CORS_ORIGIN="$CORS_ORIGIN" \
                      --build-arg DATABASE_URL="$DATABASE_URL" \
                      --build-arg JWT_SECRET="$JWT_SECRET" \
                      --build-arg PORT="$PORT" \
                      --build-arg SALT_ROUNDS="$SALT_ROUNDS" \
                      -t $IMAGE_NAME:$IMAGE_TAG .
                '''
            }
        }
        stage('Deploy container') {
            steps {
                sh '''
                    echo "🧹 Suppression du conteneur existant..."
                    docker rm -f $CONTAINER_NAME || true

                    echo "🚀 Démarrage du nouveau conteneur..."
                    docker run -d \
                        --name $CONTAINER_NAME \
                        -p $PORT:$PORT \
                        --restart unless-stopped \
                        -e CORS_ORIGIN="$CORS_ORIGIN" \
                        -e DATABASE_URL="$DATABASE_URL" \
                        -e JWT_SECRET="$JWT_SECRET" \
                        -e SALT_ROUNDS="$SALT_ROUNDS" \
                        -e PORT="$PORT" \
                        $IMAGE_NAME:$IMAGE_TAG
                '''
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}
