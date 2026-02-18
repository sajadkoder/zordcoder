#!/bin/bash

set -e

echo "=== Fly.io Deployment Script for ZordCoder ==="
echo ""

APP_NAME="zordcoder"
VOLUME_NAME="model_cache"
VOLUME_SIZE="10gb"

check_cli() {
    if ! command -v fly &> /dev/null; then
        echo "Error: Fly CLI not installed."
        echo "Install with: curl -L https://fly.io/install.sh | sh"
        exit 1
    fi
}

check_auth() {
    if ! fly auth whoami &> /dev/null; then
        echo "Not authenticated. Running 'fly auth login'..."
        fly auth login
    fi
}

create_app() {
    if fly apps list | grep -q "$APP_NAME"; then
        echo "App '$APP_NAME' already exists."
    else
        echo "Creating app '$APP_NAME'..."
        fly apps create "$APP_NAME"
    fi
}

create_volume() {
    if fly volumes list | grep -q "$VOLUME_NAME"; then
        echo "Volume '$VOLUME_NAME' already exists."
    else
        echo "Creating persistent volume '$VOLUME_NAME' ($VOLUME_SIZE)..."
        fly volumes create "$VOLUME_NAME" --size "$VOLUME_SIZE" --region ord
    fi
}

deploy_cpu() {
    echo "Deploying with CPU configuration..."
    fly deploy --dockerfile Dockerfile --build-arg USE_GPU=false
}

deploy_gpu() {
    echo "Deploying with GPU configuration..."
    fly deploy --dockerfile Dockerfile --build-arg USE_GPU=true \
        --vm-gpu-kind a100-pcie-40gb \
        --vm-cpu-kind dedicated \
        --vm-cpus 4 \
        --vm-memory 16384
}

scale_to_zero() {
    echo "Configuring scale-to-zero..."
    fly scale count 0 --process-group app
    fly machines update --auto-stop true
}

show_status() {
    echo ""
    echo "=== Deployment Status ==="
    fly status
    echo ""
    echo "=== App URL ==="
    echo "https://$APP_NAME.fly.dev"
}

usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  init        Initialize app and create volume"
    echo "  deploy-cpu  Deploy with CPU-only configuration"
    echo "  deploy-gpu  Deploy with GPU support"
    echo "  scale-zero  Scale to zero machines (cost savings)"
    echo "  status      Show deployment status"
    echo "  logs        Show application logs"
    echo "  destroy     Destroy the app and volumes"
    echo ""
    echo "Examples:"
    echo "  $0 init"
    echo "  $0 deploy-cpu"
    echo "  $0 deploy-gpu"
}

case "${1:-}" in
    init)
        check_cli
        check_auth
        create_app
        create_volume
        ;;
    deploy-cpu)
        check_cli
        deploy_cpu
        show_status
        ;;
    deploy-gpu)
        check_cli
        deploy_gpu
        show_status
        ;;
    scale-zero)
        scale_to_zero
        ;;
    status)
        show_status
        ;;
    logs)
        fly logs
        ;;
    destroy)
        echo "Warning: This will delete the app and all data!"
        read -p "Are you sure? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            fly apps destroy "$APP_NAME" --yes
        fi
        ;;
    *)
        usage
        ;;
esac
