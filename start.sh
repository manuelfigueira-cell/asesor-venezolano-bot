#!/bin/bash
echo "🤖 Iniciando Asistente Emprendedor Venezolano..."
echo "🔧 Puerto asignado: $PORT"

# Iniciar servidor de acciones
python -m rasa_sdk --actions actions --port 5055 &

# Esperar 3 segundos
sleep 3

# Iniciar servidor principal
rasa run \
  --enable-api \
  --cors "*" \
  --port $PORT \
  --endpoints endpoints.yml \
  --credentials credentials.yml \
  --debug