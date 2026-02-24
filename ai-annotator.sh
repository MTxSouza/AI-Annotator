# CLI parameters.
ARG0="$1"
ARG1="$2"

# Utilities.
load_env_file() {
    if [ -f .env ]; then
        export $(grep -v '^#' .env | xargs)
    else
        echo "Error: .env file not found in the current directory."
        echo "Please create a .env file based on the .env.example provided."
        exit 1
    fi
}

setup_development_dependencies() {
    echo "🔧 Setting up development dependencies..."
    echo ""
    pip install -r requirements-dev.txt
    echo "Setup pre-commit hooks..."
    pre-commit install
    pre-commit install --hook-type commit-msg
    pre-commit install --hook-type pre-push
    echo ""
    echo "✅ Development environment is ready!"
    exit 0
}

build_application() {
    echo "🔧 Building AI-Annotator application..."
    docker compose --profile app build -q
    echo ""
    echo "✅ Build complete!"
    exit 0
}

deploy_application() {
    echo "🚀 Starting AI-Annotator application..."
    docker compose --profile app up -d
    echo ""
    echo "🖥️ Application is running at http://127.0.0.1:80"
    exit 0
}

development_deploy_application() {
    echo "🚀 Starting AI-Annotator application (in development mode)..."
    echo ""
    docker compose --profile test up
    exit 0
}

stop_application() {
    echo "🛑 Stopping AI-Annotator application..."
    docker compose --profile app down
    docker compose --profile test down
    echo ""
    echo "✅ Application stopped."
    exit 0
}

clean_application() {
    echo "🧹 Cleaning up AI-Annotator application..."
    docker compose --profile app down --rmi all -v --remove-orphans 2>/dev/null || true
    docker compose --profile test down --rmi all -v --remove-orphans 2>/dev/null || true
    echo ""
    echo "✅ Cleanup complete."
    exit 0
}

test_application() {
    echo "🧪 Running backend tests..."
    docker compose --profile unittest up --build --quiet-build --abort-on-container-exit
    EXIT_CODE=$?
    echo "✅ Backend tests completed."
    docker compose --profile unittest down --rmi all -v
    exit $EXIT_CODE
}

# Check option.
if [ "$ARG0" = "--help" ] || [ "$ARG0" = "-h" ]; then
    echo "Usage: ai-annotator.sh [--help|-h]"
    echo ""
    echo "This script provides help information for the AI-Annotator application."
    echo ""
    echo "Options:"
    echo "  --help, -h    Show this help message and exit."
    echo "  --install, -i  Runs the docker compose command to install the AI-Annotator application locally."
    echo "  --run, -r   Runs the docker compose command to start the AI-Annotator application."
    echo "  --dev-run, -dr   Runs the docker compose command to start the AI-Annotator application in development mode."
    echo "  --stop, -s   Runs the docker compose command to stop the AI-Annotator application."
    echo "  --clean, -c   Runs the docker compose command to stop and remove all containers, networks, images, and volumes."
    echo ""
    echo "  --dev, -d   Sets up the development environment by installing dependencies and pre-commit hooks. Only for development purposes."
    echo "  --test, -t   Runs the backend tests using pytest. Only for development purposes."
    exit 0
fi

# Install option.
if [ "$ARG0" = "--install" ] || [ "$ARG0" = "-i" ]; then

    # Check --help option.
    if [ "$ARG1" = "--help" ] || [ "$ARG1" = "-h" ]; then
        echo "Usage: ai-annotator.sh --install [--help|-h]"
        echo ""
        echo "This command installs the AI-Annotator application using Docker Compose."
        echo ""
        echo "Options:"
        echo "  --help, -h    Show this help message and exit."
        echo ""
        echo "This command sets up the necessary Docker containers for the AI-Annotator application."
        echo "Before running the build command, it will try to find a .env file in the current directory"
        echo "to load environment variables. Make sure to create and configure the .env file as needed."
        exit 0
    fi

    # Check for .env file.
    load_env_file

    # Setup local storage path.
    if [ -z "$LOCAL_STORAGE_PATH" ]; then
        echo "Error: LOCAL_STORAGE_PATH is not set in the .env file."
        echo "Please set the LOCAL_STORAGE_PATH variable to specify the local storage directory."
        exit 1
    fi
    mkdir -p "$LOCAL_STORAGE_PATH/mongodb"
    mkdir -p "$LOCAL_STORAGE_PATH/static"

    # Run docker compose build.
    build_application

elif [ "$ARG0" = "--run" ] || [ "$ARG0" = "-r" ]; then

    # Check --help option.
    if [ "$ARG1" = "--help" ] || [ "$ARG1" = "-h" ]; then
        echo "Usage: ai-annotator.sh --run [--help|-h]"
        echo ""
        echo "This command starts the AI-Annotator application using Docker Compose."
        echo ""
        echo "Options:"
        echo "  --help, -h    Show this help message and exit."
        echo ""
        echo "This command starts the AI-Annotator application containers. You must have already"
        echo "installed the application using the --install option."
        exit 0
    fi

    # Deploy application.
    deploy_application

elif [ "$ARG0" = "--dev-run" ] || [ "$ARG0" = "-dr" ]; then

    # Check --help option.
    if [ "$ARG1" = "--help" ] || [ "$ARG1" = "-h" ]; then
        echo "Usage: ai-annotator.sh --dev-run [--help|-h]"
        echo ""
        echo "This command starts the AI-Annotator application in development mode using Docker Compose."
        echo ""
        echo "Options:"
        echo "  --help, -h    Show this help message and exit."
        echo ""
        echo "This command starts the AI-Annotator application containers with development settings. You"
        echo "must have already installed the application using the --install option. This mode is intended"
        echo "for development purposes only and may include additional tools or configurations for debugging."
        exit 0
    fi

    # Deploy application in development mode.
    development_deploy_application

elif [ "$ARG0" = "--stop" ] || [ "$ARG0" = "-s" ]; then

    # Check --help option.
    if [ "$ARG1" = "--help" ] || [ "$ARG1" = "-h" ]; then
        echo "Usage: ai-annotator.sh --stop [--help|-h]"
        echo ""
        echo "This command stops the AI-Annotator application using Docker Compose."
        echo ""
        echo "Options:"
        echo "  --help, -h    Show this help message and exit."
        echo ""
        echo "This command stops and removes the AI-Annotator application containers."
        exit 0
    fi

    # Stop application.
    stop_application

elif [ "$ARG0" = "--clean" ] || [ "$ARG0" = "-c" ]; then

    # Check --help option.
    if [ "$ARG1" = "--help" ] || [ "$ARG1" = "-h" ]; then
        echo "Usage: ai-annotator.sh --clean [--help|-h]"
        echo ""
        echo "This command cleans up the AI-Annotator application using Docker Compose."
        echo ""
        echo "Options:"
        echo "  --help, -h    Show this help message and exit."
        echo ""
        echo "This command stops the AI-Annotator application and removes all containers, networks,"
        echo "images, and volumes associated with it."
        exit 0
    fi

    # Clean application.
    clean_application

elif [ "$ARG0" = "--dev" ] || [ "$ARG0" = "-d" ]; then

    # Check --help option.
    if [ "$ARG1" = "--help" ] || [ "$ARG1" = "-h" ]; then
        echo "Usage: ai-annotator.sh --dev [--help|-h]"
        echo ""
        echo "This command sets up the development environment for the AI-Annotator application."
        echo ""
        echo "Options:"
        echo "  --help, -h    Show this help message and exit."
        echo ""
        echo "This command installs the development dependencies and sets up pre-commit hooks."
        echo "It is intended for development purposes only."
        exit 0
    fi

    # Setup development environment.
    setup_development_dependencies

elif [ "$ARG0" = "--test" ] || [ "$ARG0" = "-t" ]; then

    # Check --help option.
    if [ "$ARG1" = "--help" ] || [ "$ARG1" = "-h" ]; then
        echo "Usage: ai-annotator.sh --test [--help|-h]"
        echo ""
        echo "This command runs the backend tests for the AI-Annotator application."
        echo ""
        echo "Options:"
        echo "  --help, -h    Show this help message and exit."
        echo ""
        echo "This command executes the backend tests using pytest. It is intended for development"
        echo "purposes only."
        exit 0
    fi

    # Run backend tests.
    test_application

else
    echo "Invalid option. Use --help to see available commands."
    exit 1

fi
