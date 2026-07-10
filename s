services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: practicepro
      POSTGRES_PASSWORD: practicepro
      POSTGRES_DB: practicepro
    ports:
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U practicepro"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  api:
    build: ./backend
    env_file: .env
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - audio_data:/data/audio
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started

  worker:
    build: ./backend
    command: celery -A worker.celery_app worker --loglevel=info
    env_file: .env
    volumes:
      - ./backend:/app
      - audio_data:/data/audio
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - api

volumes:
  postgres_data:
  audio_data:
