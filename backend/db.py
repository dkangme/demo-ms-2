"""
Firestore client initialization module.
Provides a factory function that returns a Firestore client
configured using environment variables.
"""

import os
import logging
from google.cloud import firestore

logger = logging.getLogger(__name__)


def get_db() -> firestore.Client:
    """
    Initializes and returns a thread-safe Firestore client.

    Raises:
        EnvironmentError: If GCP_PROJECT environment variable is not set.

    Returns:
        google.cloud.firestore.Client: A Firestore client connected to the
        project specified in GCP_PROJECT, using credentials from
        GOOGLE_APPLICATION_CREDENTIALS if present, or the default service
        account otherwise.
    """
    project = os.environ.get("GCP_PROJECT")
    if not project:
        raise EnvironmentError(
            "GCP_PROJECT environment variable is required to initialize Firestore client."
        )

    # Ensure the underlying Google Cloud libraries can locate the project
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project)

    logger.debug("Initializing Firestore client for project: %s", project)
    return firestore.Client(project=project)
