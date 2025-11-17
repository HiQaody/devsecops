#!/bin/sh
set -e

echo "NODE_ENV=$NODE_ENV"
if [ ! -f .migrated ]; then
  echo "Migrations..."
  npx sequelize-cli db:migrate || { echo "Echec migrations"; exit 1; }
  touch .migrated
else
  echo "Migrations déjà effectuées"
fi

node server.js