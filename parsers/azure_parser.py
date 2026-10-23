import os
from pathlib import Path

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential


def parse_document(file_path: str | Path) -> str:
    """Extract document content as Markdown using Azure Document Intelligence."""
    endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")

    if not endpoint or not key:
        raise RuntimeError(
            "Set AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT and "
            "AZURE_DOCUMENT_INTELLIGENCE_KEY first."
        )

    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(path)

    client = DocumentIntelligenceClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
    )

    with path.open("rb") as document:
        poller = client.begin_analyze_document(
            "prebuilt-layout",
            body=document,
            content_type="application/octet-stream",
        )

    result = poller.result()

    # Preserve Azure's extracted text and table structure where available.
    if result.tables:
        from azure.ai.documentintelligence.models import DocumentContentFormat

        markdown_client = DocumentIntelligenceClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key),
        )
        with path.open("rb") as document:
            markdown_poller = markdown_client.begin_analyze_document(
                "prebuilt-layout",
                body=document,
                content_type="application/octet-stream",
                output_content_format=DocumentContentFormat.MARKDOWN,
            )
        result = markdown_poller.result()

    return result.content or ""
