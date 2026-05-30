#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# start_local_pg.sh — Start local PostgreSQL (Homebrew install) for dev
#
# Usage:
#   ./start_local_pg.sh          # start postgres + open psql shell
#   ./start_local_pg.sh start    # start only
#   ./start_local_pg.sh stop     # stop postgres
#   ./start_local_pg.sh status   # check if running
# ─────────────────────────────────────────────────────────────────────────────

export PATH="/home/linuxbrew/.linuxbrew/bin:/home/linuxbrew/.linuxbrew/opt/postgresql@16/bin:$PATH"

PG_DATA="/home/linuxbrew/.linuxbrew/var/postgresql@16"
PG_LOG="/tmp/pg_uscontenthub.log"
PG_CTL="/home/linuxbrew/.linuxbrew/opt/postgresql@16/bin/pg_ctl"

CMD="${1:-start}"

case "$CMD" in
  start)
    if pg_isready -q 2>/dev/null; then
      echo "PostgreSQL is already running on port 5432"
    else
      echo "Starting PostgreSQL..."
      "$PG_CTL" -D "$PG_DATA" -l "$PG_LOG" start
      sleep 2
      pg_isready && echo "Ready. Connect: psql -U uscontenthub -d uscontenthub"
    fi
    ;;
  stop)
    echo "Stopping PostgreSQL..."
    "$PG_CTL" -D "$PG_DATA" stop
    ;;
  status)
    pg_isready && echo "Running" || echo "Not running"
    ;;
  *)
    echo "Usage: $0 [start|stop|status]"
    exit 1
    ;;
esac
