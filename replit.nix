{ pkgs }: {
  # Provide Python and Node for Replit environments and install deps on shell start.
  deps = [ pkgs.python311Full pkgs.nodejs-18_x ];
  shellHook = ''
    echo "Setting up Python and Node dependencies..."
    python -m pip install --upgrade pip || true
    if [ -f requirements.txt ]; then
      pip install -r requirements.txt || true
    fi
    if [ -d frontend ]; then
      (cd frontend && npm install) || true
    fi
  '';
}
