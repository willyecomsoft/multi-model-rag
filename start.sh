if [ -z "$APP_HOST" ]; then
  sed -i 's|localhost:5002|$APP_HOST|' /app/templates/index.html
  sed -i 's|localhost:5002|$APP_HOST|' /app/templates/upload.html
fi

flask run