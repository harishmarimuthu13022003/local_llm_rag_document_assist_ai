"""Backend main package initialization.

Disables telemetry and bypasses gRPC C-extensions blocked by Windows Application Control policies.
"""

import os
import sys
from unittest.mock import MagicMock

os.environ["ANONYMIZED_TELEMETRY"] = "False"

# Safely stub gRPC OTLP telemetry module imports if native C-extension DLL loading is restricted
try:
    import grpc._cython.cygrpc  # type: ignore # noqa: F401
except ImportError:
    grpc_mock = MagicMock()
    sys.modules["grpc"] = grpc_mock
    sys.modules["grpc._cython"] = grpc_mock
    sys.modules["grpc._cython.cygrpc"] = grpc_mock
    sys.modules["opentelemetry.exporter.otlp.proto.grpc"] = grpc_mock
    sys.modules["opentelemetry.exporter.otlp.proto.grpc.trace_exporter"] = grpc_mock
