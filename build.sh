#!/bin/bash
echo "🚀 Instalando dependencias de Python..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🏗️ Entrenando el modelo de Rasa..."
rasa train --quiet

echo "✅ Build completado exitosamente!"