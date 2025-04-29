#!/bin/bash

filename="secret.txt" # This is the secret key file for the application.

if [ ! -f "$filename" ]; then
    openssl rand -base64 32 > "$filename"
    echo "Generated new secret key in $filename"
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
    echo "Secret key file already exists"
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
fi
