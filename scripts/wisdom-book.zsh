#!/bin/zsh

# Wisdom Book Service Manager
# Manages Django backend and React frontend services

PROJECT_DIR="/Users/quasaur/Developer/wisdom-book"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
PID_DIR="$HOME/.wisdom-book-pids"
PYTHON_EXEC="$PROJECT_DIR/.venv/bin/python"

# Create PID directory if it doesn't exist
mkdir -p "$PID_DIR"

BACKEND_PID_FILE="$PID_DIR/backend.pid"
FRONTEND_PID_FILE="$PID_DIR/frontend.pid"
BACKEND_LOG="/tmp/wisdom_backend.log"
FRONTEND_LOG="/tmp/wisdom_frontend.log"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

start_backend() {
    echo "${YELLOW}Starting Django backend...${NC}"
    
    if [[ -f "$BACKEND_PID_FILE" ]]; then
        PID=$(cat "$BACKEND_PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "${YELLOW}Backend already running with PID $PID${NC}"
            return
        fi
    fi
    
    cd "$BACKEND_DIR" || {
        echo "${RED}✗ Failed to change to backend directory: $BACKEND_DIR${NC}"
        return 1
    }
    
    if [[ ! -f "$PYTHON_EXEC" ]]; then
        echo "${RED}✗ Python executable not found at $PYTHON_EXEC${NC}"
        return 1
    fi

    nohup "$PYTHON_EXEC" manage.py runserver > "$BACKEND_LOG" 2>&1 &
    echo $! > "$BACKEND_PID_FILE"
    echo "${GREEN}✓ Backend started with PID $(cat $BACKEND_PID_FILE)${NC}"
    echo "Logs: $BACKEND_LOG"
}

start_frontend() {
    echo "${YELLOW}Starting React frontend...${NC}"
    
    if [[ -f "$FRONTEND_PID_FILE" ]]; then
        PID=$(cat "$FRONTEND_PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "${YELLOW}Frontend already running with PID $PID${NC}"
            return
        fi
    fi
    
    cd "$FRONTEND_DIR" || {
        echo "${RED}✗ Failed to change to frontend directory: $FRONTEND_DIR${NC}"
        return 1
    }
    # Use npm start as defined in package.json (defaults to port 3000)
    nohup npm start > "$FRONTEND_LOG" 2>&1 &
    echo $! > "$FRONTEND_PID_FILE"
    echo "${GREEN}✓ Frontend started with PID $(cat $FRONTEND_PID_FILE)${NC}"
    echo "Logs: $FRONTEND_LOG"
}

stop_backend() {
    echo "${YELLOW}Stopping Django backend...${NC}"
    
    if [[ -f "$BACKEND_PID_FILE" ]]; then
        PID=$(cat "$BACKEND_PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            kill $PID
            rm "$BACKEND_PID_FILE"
            echo "${GREEN}✓ Backend stopped${NC}"
        else
            echo "${RED}Backend not running${NC}"
            rm "$BACKEND_PID_FILE"
        fi
    else
        echo "${RED}No backend PID file found${NC}"
    fi
}

stop_frontend() {
    echo "${YELLOW}Stopping React frontend...${NC}"
    
    if [[ -f "$FRONTEND_PID_FILE" ]]; then
        PID=$(cat "$FRONTEND_PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            kill $PID
            rm "$FRONTEND_PID_FILE"
            echo "${GREEN}✓ Frontend stopped${NC}"
        else
            echo "${RED}Frontend not running${NC}"
            rm "$FRONTEND_PID_FILE"
        fi
    else
        echo "${RED}No frontend PID file found${NC}"
    fi
}

status_check() {
    echo "${YELLOW}Checking service status...${NC}"
    
    # Check backend
    if [[ -f "$BACKEND_PID_FILE" ]]; then
        PID=$(cat "$BACKEND_PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "${GREEN}✓ Backend running (PID: $PID)${NC}"
        else
            echo "${RED}✗ Backend not running (stale PID file)${NC}"
        fi
    else
        echo "${RED}✗ Backend not running${NC}"
    fi
    
    # Check frontend
    if [[ -f "$FRONTEND_PID_FILE" ]]; then
        PID=$(cat "$FRONTEND_PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "${GREEN}✓ Frontend running (PID: $PID)${NC}"
        else
            echo "${RED}✗ Frontend not running (stale PID file)${NC}"
        fi
    else
        echo "${RED}✗ Frontend not running${NC}"
    fi
}

open_chrome() {
    echo "${YELLOW}Opening Chrome at http://localhost:3000...${NC}"
    sleep 2  # Give services a moment to start
    open -a "Google Chrome" "http://localhost:3000" 2>/dev/null
    if [[ $? -eq 0 ]]; then
        echo "${GREEN}✓ Chrome opened${NC}"
    else
        echo "${RED}✗ Could not open Chrome (is it installed?)${NC}"
    fi
}

case "$1" in
    start)
        echo "${GREEN}Starting Wisdom Book services...${NC}"
        # Activate Python environment
        if [[ -f "$PROJECT_DIR/.venv/bin/activate" ]]; then
            source "$PROJECT_DIR/.venv/bin/activate"
            echo "${GREEN}✓ Python environment activated${NC}"
        fi
        start_backend
        start_frontend
        open_chrome
        echo "${GREEN}All services started!${NC}"
        echo "Backend: http://localhost:8000"
        echo "Frontend: http://localhost:3000"
        ;;
    stop)
        echo "${RED}Stopping Wisdom Book services...${NC}"
        stop_backend
        stop_frontend
        # Deactivate Python environment if function exists
        if type deactivate > /dev/null 2>&1; then
            deactivate
            echo "${GREEN}✓ Python environment deactivated${NC}"
        fi
        echo "${GREEN}All services stopped!${NC}"
        ;;
    restart)
        echo "${YELLOW}Restarting Wisdom Book services...${NC}"
        stop_backend
        stop_frontend
        # Deactivate if active before restarting (clean slate)
        if type deactivate > /dev/null 2>&1; then
            deactivate
        fi
        
        sleep 2
        
        # Activate Python environment
        if [[ -f "$PROJECT_DIR/.venv/bin/activate" ]]; then
            source "$PROJECT_DIR/.venv/bin/activate"
            echo "${GREEN}✓ Python environment activated${NC}"
        fi
        start_backend
        start_frontend
        open_chrome
        echo "${GREEN}All services restarted!${NC}"
        ;;
    status)
        status_check
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        echo ""
        echo "Commands:"
        echo "  start   - Start both backend and frontend services"
        echo "  stop    - Stop both backend and frontend services"
        echo "  restart - Restart both services"
        echo "  status  - Check if services are running"
        exit 1
        ;;
esac
