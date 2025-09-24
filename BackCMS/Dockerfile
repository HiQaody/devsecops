# --- Étape 1 : Build ---
    FROM node:18-alpine AS build

    WORKDIR /usr/src/app
    
    COPY package*.json ./
    RUN npm ci
    
    COPY . .
    RUN npm run build || echo "Pas de script build, compilation ignorée"
    
    # --- Étape 2 : Production ---
    FROM node:18-alpine AS production
    
    WORKDIR /usr/src/app
    
    # Copier uniquement les fichiers nécessaires
    COPY package*.json ./
    RUN npm ci --only=production
    
    # Copier le build depuis l'étape précédente
    COPY --from=build /usr/src/app/dist ./dist
    
    # Définir les ARG (seront injectés par le CI/CD)
    ARG NODE_ENV=production
    ARG PORT=3137
    ARG DB_HOST
    ARG DB_PORT
    ARG DB_USERNAME
    ARG DB_PASSWORD
    ARG DB_DATABASE
    ARG EMAIL_USER
    ARG EMAIL_PASS
    ARG CLOUDINARY_CLOUD_NAME
    ARG CLOUDINARY_API_KEY
    ARG CLOUDINARY_API_SECRET
    ARG GOOGLE_CLIENT_ID
    ARG GOOGLE_CLIENT_SECRET
    
    # Appliquer les ARG comme ENV (runtime)
    ENV NODE_ENV=$NODE_ENV
    ENV PORT=$PORT
    ENV DB_HOST=$DB_HOST
    ENV DB_PORT=$DB_PORT
    ENV DB_USERNAME=$DB_USERNAME
    ENV DB_PASSWORD=$DB_PASSWORD
    ENV DB_DATABASE=$DB_DATABASE
    ENV EMAIL_USER=$EMAIL_USER
    ENV EMAIL_PASS=$EMAIL_PASS
    ENV CLOUDINARY_CLOUD_NAME=$CLOUDINARY_CLOUD_NAME
    ENV CLOUDINARY_API_KEY=$CLOUDINARY_API_KEY
    ENV CLOUDINARY_API_SECRET=$CLOUDINARY_API_SECRET
    ENV GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID
    ENV GOOGLE_CLIENT_SECRET=$GOOGLE_CLIENT_SECRET
    
    EXPOSE $PORT
    
    CMD ["node", "dist/index.js"]