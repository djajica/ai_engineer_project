from __future__ import annotations

from typing import Any

import logging

import weaviate
from httpx import ConnectError as HTTPXConnectError
from weaviate.classes.query import MetadataQuery
from weaviate.exceptions import WeaviateBaseError, WeaviateConnectionError


class WeaviateRepository:
    """Simple Weaviate client wrapper for document storage and retrieval."""

    def __init__(
        self,
        url: str,
        api_key: str | None = None,
        collection_name: str = "Documents",
        openai_api_key: str | None = None,
        allow_fallback: bool = False,
        grpc_port: int | None = None,
    ) -> None:
        """
        Initialize Weaviate client.

        Args:
            url: Weaviate instance URL (e.g., http://localhost:8080 or https://...)
            api_key: Optional Weaviate API key for authentication
            collection_name: Name of the collection to use
            openai_api_key: OpenAI API key for embeddings (required for vectorizer)
        """
        self._logger = logging.getLogger(__name__)
        auth = weaviate.auth.AuthApiKey(api_key=api_key) if api_key else None
        self.openai_api_key = openai_api_key
        self.collection_name = collection_name
        self._offline = False
        self.client = None

        try:
            self.client = self._connect(url=url, auth=auth, grpc_port_override=grpc_port)
        except (WeaviateConnectionError, WeaviateBaseError, HTTPXConnectError, OSError) as exc:
            if allow_fallback:
                self._offline = True
                self._logger.warning(
                    "Unable to connect to Weaviate at %s. Continuing in offline mode. Error: %s",
                    url,
                    exc,
                )
            else:
                raise

    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """
        Perform hybrid search on documents.

        Args:
            query: Search query string
            limit: Maximum number of results to return

        Returns:
            List of documents with text and metadata
        """
        if self.client is None:
            self._logger.debug("Offline Weaviate repo - returning empty search results")
            return []

        try:
            collection = self.client.collections.get(self.collection_name)
            response = collection.query.hybrid(
                query=query,
                limit=limit,
                return_metadata=MetadataQuery(distance=True),
            )

            results: list[dict[str, Any]] = []
            for obj in response.objects:
                properties = obj.properties
                results.append(
                    {
                        "text": properties.get("text", ""),
                        "metadata": {k: v for k, v in properties.items() if k != "text"},
                        "distance": obj.metadata.distance if obj.metadata else None,
                    }
                )
            return results
        except Exception as e:
            # If collection doesn't exist, return empty list
            if "does not exist" in str(e).lower():
                return []
            raise

    def add_documents(self, documents: list[dict[str, Any]]) -> None:
        """
        Add documents to the collection.

        Args:
            documents: List of documents, each with 'text' and optional 'metadata'
        """
        if self.client is None:
            self._logger.debug("Offline Weaviate repo - skipping document add")
            return

        try:
            collection = self.client.collections.get(self.collection_name)
        except Exception:
            # Collection doesn't exist, create it
            self._create_collection()
            collection = self.client.collections.get(self.collection_name)

        with collection.batch.dynamic() as batch:
            for idx, doc in enumerate(documents):
                text = doc.get("text", "")
                metadata = doc.get("metadata", {})
                properties = {"text": text, **metadata}
                batch.add_object(
                    properties=properties,
                    uuid=weaviate.util.generate_uuid5(properties),
                )
    def get_status(self) -> dict[str, Any]:
        """Return basic health info and collection statistics."""
        status: dict[str, Any] = {
            "collection": self.collection_name,
            "online": False,
        }

        if self.client is None:
            status["message"] = "Weaviate client unavailable (offline mode)."
            return status

        try:
            collection = self.client.collections.get(self.collection_name)
        except Exception as exc:
            status["message"] = f"Unable to access collection: {exc}"
            return status

        status["online"] = True

        try:
            config = collection.config.get()
            status["schema"] = {
                "name": config.name,
                "description": getattr(config, "description", None),
                "vectorizer": getattr(config, "vectorizer", None),
                "module_config": getattr(config, "module_config", None),
                "properties": [prop.name for prop in getattr(config, "properties", [])],
            }
        except Exception as exc:
            status["schema_error"] = str(exc)

        try:
            aggregate = collection.aggregate.over_all(total_count=True)
            status["object_count"] = aggregate.total_count or 0
        except Exception as exc:
            status["aggregation_error"] = str(exc)

        return status

    def list_objects(self, limit: int = 20) -> list[dict[str, Any]]:
        """Return recent objects stored in the collection."""
        if self.client is None:
            self._logger.debug("Offline Weaviate repo - cannot list objects")
            return []

        try:
            collection = self.client.collections.get(self.collection_name)
        except Exception as exc:
            self._logger.error("Unable to read collection %s: %s", self.collection_name, exc)
            return []

        try:
            response = collection.query.fetch_objects(limit=limit)
        except Exception as exc:
            self._logger.error("Error fetching objects from Weaviate: %s", exc)
            return []

        items: list[dict[str, Any]] = []
        for obj in response.objects or []:
            properties = obj.properties or {}
            metadata = {k: v for k, v in properties.items() if k != "text"}
            entry: dict[str, Any] = {
                "id": str(obj.uuid),
                "text": properties.get("text", ""),
                "metadata": metadata,
            }

            if obj.metadata:
                entry["distance"] = getattr(obj.metadata, "distance", None)
                entry["created"] = getattr(obj.metadata, "creation_time", None)
                entry["updated"] = getattr(obj.metadata, "last_update_time", None)

            items.append(entry)

        return items

    def _create_collection(self) -> None:
        """Create the Documents collection if it doesn't exist."""
        if self.client is None:
            self._logger.debug("Offline Weaviate repo - skipping collection creation")
            return

        if self.openai_api_key:
            # Use OpenAI text-embedding-3-large vectorizer
            vectorizer_config = weaviate.classes.config.Configure.Vectorizer.text2vec_openai(
                model="text-embedding-3-large",
                model_version="",
                type_="text",
            )
        else:
            # Fallback to none if no OpenAI key
            vectorizer_config = weaviate.classes.config.Configure.Vectorizer.none()

        # Define properties for the collection
        properties = [
            weaviate.classes.Property(
                name="text",
                data_type=weaviate.classes.DataType.TEXT,
                description="Document text content",
            ),
        ]

        self.client.collections.create(
            name=self.collection_name,
            vectorizer_config=vectorizer_config,
            properties=properties,
            generative_config=weaviate.classes.config.Configure.Generative.none(),
        )

    def close(self) -> None:
        """Close the Weaviate client connection."""
        if self.client:
            self.client.close()

    def _connect(
        self,
        url: str,
        auth: weaviate.auth.AuthApiKey | None,
        grpc_port_override: int | None = None,
    ):
        """Create a Weaviate client for the provided URL."""
        url_clean = url.replace("http://", "").replace("https://", "")
        is_secure = url.startswith("https://")

        if ":" in url_clean:
            host, port = url_clean.split(":", 1)
        else:
            host = url_clean
            port = "443" if is_secure else "8080"

        if host in ("localhost", "127.0.0.1") and not is_secure and grpc_port_override is None:
            import weaviate.classes.init as wvc

            return weaviate.connect_to_custom(
                http_host=host,
                http_port="8080",
                http_secure=False,
                grpc_host=host,
                grpc_port="50051",
                grpc_secure=False,
                auth_credentials=auth,
                additional_config=wvc.AdditionalConfig(
                    timeout=wvc.Timeout(init=30, query=60, insert=60),
                ),
            )

        if grpc_port_override is not None:
            grpc_port = str(grpc_port_override)
        else:
            grpc_port = str(int(port) + 1) if port.isdigit() and not is_secure else "50051"

        return weaviate.connect_to_custom(
            http_host=host,
            http_port=port,
            http_secure=is_secure,
            grpc_host=host,
            grpc_port=grpc_port,
            grpc_secure=is_secure,
            auth_credentials=auth,
        )

