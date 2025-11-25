pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/nipun221/flask-blog-app.git'
            }
        }

        stage('Build & Deploy with Docker Compose') {
            steps {
                sh '''
                  # Stop and remove old containers (if any)
                  docker compose down || true

                  # Build web image from Dockerfile and start web + db
                  docker compose up -d --build
                '''
            }
        }
    }
}
