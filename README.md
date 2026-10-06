# Toa

Workout tracker web-app (soon iOS app)

## Getting Started

### Setup Database

```bash
cd backend
docker compose up

# In another terminal, in backend directory
docker compose exec db psql -U user -d workout -c "CREATE DATABASE workout_test;"
```
