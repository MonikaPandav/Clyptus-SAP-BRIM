"""
Centralized GitHub Repository Source Registry for cClyptus.AI SAP BRIM.
Defines Tiers A, B, and C repositories, provenance tiers, approved ingestion scopes,
and tracks keep/drop statistics, license audit status, and sync times.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class RepositoryRegistryEntry(BaseModel):
    repo_url: str
    owner: str
    name: str
    tier: str  # 'Tier A', 'Tier B', 'Tier C'
    provenance_tier: str  # 'sap_partner_or_book', 'github_repo', 'official_sap'
    expected_domain: str  # 'SAP_BRIM', 'SAP_ECOSYSTEM', 'GENERIC_INFRA', 'NON_SAP_FINANCIAL', 'NON_BRIM_EV_CHARGING'
    license_id: Optional[str] = None
    license_status: str = "unknown"  # 'approved', 'unknown', 'restricted'
    approved_ingestion_scope: str = "approved_supported_files"
    pinned_commit_sha: Optional[str] = None
    last_synced_at: Optional[str] = None
    files_discovered: int = 0
    files_skipped: int = 0
    chunks_considered: int = 0
    identifier_matches: int = 0
    contextual_keyword_matches: int = 0
    anchor_similarity_rejections: int = 0
    chunks_retained: int = 0
    chunks_dropped: int = 0
    ingestion_status: str = "pending"  # 'pending', 'active', 'skipped_low_yield', 'rejected_unlicensed'
    notes: Optional[str] = None


REGISTERED_REPOSITORIES: List[Dict[str, Any]] = [
    # --- Tier A: BRIM-specific repository ---
    {
        "repo_url": "https://github.com/api-evangelist/sap-brim-billing-and-revenue-innovation-management",
        "owner": "api-evangelist",
        "name": "sap-brim-billing-and-revenue-innovation-management",
        "tier": "Tier A",
        "provenance_tier": "sap_partner_or_book",
        "expected_domain": "SAP_BRIM",
        "approved_ingestion_scope": "approved_supported_files",
        "notes": "Third-party API metadata and OpenAPI specifications for SAP BRIM."
    },

    # --- Tier B: SAP and other repositories ---
    {
        "repo_url": "https://github.com/SAP-samples/open-payment-framework-integration",
        "owner": "SAP-samples",
        "name": "open-payment-framework-integration",
        "tier": "Tier B",
        "provenance_tier": "sap_partner_or_book",
        "expected_domain": "SAP_ECOSYSTEM",
        "approved_ingestion_scope": "approved_supported_files",
        "notes": "SAP digital payment framework integration sample."
    },
    {
        "repo_url": "https://github.com/SAP-samples/cloud-cap-samples-java",
        "owner": "SAP-samples",
        "name": "cloud-cap-samples-java",
        "tier": "Tier B",
        "provenance_tier": "sap_partner_or_book",
        "expected_domain": "SAP_ECOSYSTEM",
        "approved_ingestion_scope": "approved_supported_files",
        "notes": "Cloud Application Programming (CAP) Java samples."
    },
    {
        "repo_url": "https://github.com/SAP-samples/btp-developer-guide-cap",
        "owner": "SAP-samples",
        "name": "btp-developer-guide-cap",
        "tier": "Tier B",
        "provenance_tier": "sap_partner_or_book",
        "expected_domain": "SAP_ECOSYSTEM",
        "approved_ingestion_scope": "approved_supported_files",
        "notes": "SAP BTP Developer Guide for CAP."
    },
    {
        "repo_url": "https://github.com/SAP-samples/fiori-tools-samples",
        "owner": "SAP-samples",
        "name": "fiori-tools-samples",
        "tier": "Tier B",
        "provenance_tier": "sap_partner_or_book",
        "expected_domain": "SAP_ECOSYSTEM",
        "approved_ingestion_scope": "approved_supported_files",
        "notes": "SAP Fiori tools samples."
    },
    {
        "repo_url": "https://github.com/SAP-samples/hana-developer-cli-tool-example",
        "owner": "SAP-samples",
        "name": "hana-developer-cli-tool-example",
        "tier": "Tier B",
        "provenance_tier": "sap_partner_or_book",
        "expected_domain": "SAP_ECOSYSTEM",
        "approved_ingestion_scope": "approved_supported_files",
        "notes": "SAP HANA CLI developer examples."
    },
    {
        "repo_url": "https://github.com/SAP-samples/btp-service-metadata",
        "owner": "SAP-samples",
        "name": "btp-service-metadata",
        "tier": "Tier B",
        "provenance_tier": "sap_partner_or_book",
        "expected_domain": "SAP_ECOSYSTEM",
        "approved_ingestion_scope": "approved_supported_files",
        "notes": "BTP service metadata descriptions."
    },
    {
        "repo_url": "https://github.com/SAP/cloud-sdk-js",
        "owner": "SAP",
        "name": "cloud-sdk-js",
        "tier": "Tier B",
        "provenance_tier": "sap_partner_or_book",
        "expected_domain": "SAP_ECOSYSTEM",
        "approved_ingestion_scope": "approved_supported_files",
        "notes": "SAP Cloud SDK for JavaScript/TypeScript."
    },
    {
        "repo_url": "https://github.com/SAP/cloud-sdk-java",
        "owner": "SAP",
        "name": "cloud-sdk-java",
        "tier": "Tier B",
        "provenance_tier": "sap_partner_or_book",
        "expected_domain": "SAP_ECOSYSTEM",
        "approved_ingestion_scope": "approved_supported_files",
        "notes": "SAP Cloud SDK for Java."
    },
    {
        "repo_url": "https://github.com/SAP/spartacus",
        "owner": "SAP",
        "name": "spartacus",
        "tier": "Tier B",
        "provenance_tier": "sap_partner_or_book",
        "expected_domain": "SAP_ECOSYSTEM",
        "approved_ingestion_scope": "approved_supported_files",
        "notes": "SAP Commerce Cloud Spartacus storefront."
    },
    {
        "repo_url": "https://github.com/sap-labs-france/ev-server",
        "owner": "sap-labs-france",
        "name": "ev-server",
        "tier": "Tier B",
        "provenance_tier": "github_repo",
        "expected_domain": "NON_BRIM_EV_CHARGING",
        "approved_ingestion_scope": "approved_supported_files",
        "notes": "Archived electric vehicle charging project. Must NOT be confused with SAP Convergent Charging."
    },
    {
        "repo_url": "https://github.com/dpbarry/BRIM-ExI",
        "owner": "dpbarry",
        "name": "BRIM-ExI",
        "tier": "Tier B",
        "provenance_tier": "github_repo",
        "expected_domain": "NON_SAP_FINANCIAL",
        "approved_ingestion_scope": "approved_supported_files",
        "notes": "Brim Financial consumer banking platform. Must NOT be treated as SAP BRIM."
    },

    # --- Tier C: Generic infrastructure repositories ---
    {
        "repo_url": "https://github.com/grafana/k6",
        "owner": "grafana",
        "name": "k6",
        "tier": "Tier C",
        "provenance_tier": "github_repo",
        "expected_domain": "GENERIC_INFRA",
        "approved_ingestion_scope": "approved_supported_files",
        "notes": "Load testing tool. Generic infrastructure."
    },
    {
        "repo_url": "https://github.com/open-telemetry/opentelemetry-collector",
        "owner": "open-telemetry",
        "name": "opentelemetry-collector",
        "tier": "Tier C",
        "provenance_tier": "github_repo",
        "expected_domain": "GENERIC_INFRA",
        "approved_ingestion_scope": "approved_supported_files",
        "notes": "OpenTelemetry telemetry collector. Generic infrastructure."
    },
    {
        "repo_url": "https://github.com/prometheus/prometheus",
        "owner": "prometheus",
        "name": "prometheus",
        "tier": "Tier C",
        "provenance_tier": "github_repo",
        "expected_domain": "GENERIC_INFRA",
        "approved_ingestion_scope": "approved_supported_files",
        "notes": "Prometheus monitoring system. Generic infrastructure."
    },
    {
        "repo_url": "https://github.com/grafana/grafana",
        "owner": "grafana",
        "name": "grafana",
        "tier": "Tier C",
        "provenance_tier": "github_repo",
        "expected_domain": "GENERIC_INFRA",
        "approved_ingestion_scope": "approved_supported_files",
        "notes": "Observability and dashboard platform. Generic infrastructure."
    },
    {
        "repo_url": "https://github.com/confluentinc/examples-cluster-production",
        "owner": "confluentinc",
        "name": "examples-cluster-production",
        "tier": "Tier C",
        "provenance_tier": "github_repo",
        "expected_domain": "GENERIC_INFRA",
        "approved_ingestion_scope": "approved_supported_files",
        "notes": "Kafka production cluster deployment examples. Generic infrastructure."
    },
    {
        "repo_url": "https://github.com/apache/kafka",
        "owner": "apache",
        "name": "kafka",
        "tier": "Tier C",
        "provenance_tier": "github_repo",
        "expected_domain": "GENERIC_INFRA",
        "approved_ingestion_scope": "approved_supported_files",
        "notes": "Distributed event streaming platform. Generic infrastructure."
    }
]


class RepositoryRegistry:
    def __init__(self):
        self._entries: Dict[str, RepositoryRegistryEntry] = {}
        for r in REGISTERED_REPOSITORIES:
            entry = RepositoryRegistryEntry(**r)
            self._entries[entry.repo_url.lower()] = entry

    def get_all(self) -> List[RepositoryRegistryEntry]:
        return list(self._entries.values())

    def get_by_url(self, repo_url: str) -> Optional[RepositoryRegistryEntry]:
        return self._entries.get(repo_url.lower().strip())

    def update_stats(self, repo_url: str, **kwargs) -> Optional[RepositoryRegistryEntry]:
        entry = self.get_by_url(repo_url)
        if entry:
            for k, v in kwargs.items():
                if hasattr(entry, k):
                    setattr(entry, k, v)
        return entry


repo_registry = RepositoryRegistry()
