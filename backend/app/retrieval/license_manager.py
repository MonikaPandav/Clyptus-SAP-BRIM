"""
License and Provenance Management for Ingested GitHub Repositories.
Complies with cClyptus.AI SAP BRIM enterprise governance:
- Detects SPDX identifiers from LICENSE files and headers
- Records detection method and confidence score
- Flags unidentifiable or missing licenses as license_status='unknown'
- Restricts distribution/indexing for unverified licenses
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

KNOWN_SPDX_PATTERNS = [
    (r"Apache License\s*,?\s*Version 2\.0", "Apache-2.0", 0.98),
    (r"MIT License", "MIT", 0.98),
    (r"Permission is hereby granted, free of charge, to any person obtaining a copy", "MIT", 0.95),
    (r"GNU GENERAL PUBLIC LICENSE\s+Version 3", "GPL-3.0", 0.98),
    (r"GNU GENERAL PUBLIC LICENSE\s+Version 2", "GPL-2.0", 0.98),
    (r"GNU LESSER GENERAL PUBLIC LICENSE", "LGPL-3.0", 0.95),
    (r"Eclipse Public License\s*-\s*v\s*2\.0", "EPL-2.0", 0.98),
    (r"BSD 3-Clause", "BSD-3-Clause", 0.98),
    (r"BSD 2-Clause", "BSD-2-Clause", 0.98),
    (r"Creative Commons Attribution 4\.0", "CC-BY-4.0", 0.98),
    (r"The Unlicense", "Unlicense", 0.98),
    (r"Mozilla Public License Version 2\.0", "MPL-2.0", 0.98),
    (r"SAP DEVELOPER LICENSE AGREEMENT", "SAP-Developer-License", 0.95),
    (r"SAP SAMPLE CODE LICENSE AGREEMENT", "SAP-Sample-Code-License", 0.95),
]

PERMISSIBLE_FOR_RETRIEVAL = {
    "Apache-2.0", "MIT", "BSD-3-Clause", "BSD-2-Clause", "EPL-2.0",
    "CC-BY-4.0", "Unlicense", "SAP-Developer-License", "SAP-Sample-Code-License",
    "MPL-2.0"
}


class LicenseManager:
    """Detects, audits, and validates repository license metadata."""

    @staticmethod
    def detect_license_from_text(text: str) -> Tuple[str, str, float]:
        """
        Scans text for known license declarations.
        Returns: (spdx_id, method, confidence)
        """
        if not text or len(text.strip()) == 0:
            return "NOASSERTION", "empty_text", 0.0

        for pattern, spdx_id, conf in KNOWN_SPDX_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return spdx_id, "pattern_match", conf

        # Check SPDX header tag
        spdx_tag_match = re.search(r"SPDX-License-Identifier:\s*([A-Za-z0-9\.\-]+)", text)
        if spdx_tag_match:
            return spdx_tag_match.group(1), "spdx_header", 0.99

        return "UNKNOWN", "unrecognized_text", 0.2

    @staticmethod
    def is_license_permitted(spdx_id: str) -> bool:
        """Checks if the SPDX license identifier is permitted for retrieval and internal indexing."""
        return spdx_id in PERMISSIBLE_FOR_RETRIEVAL

    def inspect_repository_license(
        self,
        repo_dir: Path,
        repo_url: str,
        commit_sha: Optional[str] = None,
        github_api_license: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Audits the repository for LICENSE / COPYING files, computes confidence,
        and determines license eligibility for retrieval.
        """
        license_files = ["LICENSE", "LICENSE.txt", "LICENSE.md", "LICENCE", "COPYING"]
        found_license_path = None
        license_content = ""

        if repo_dir and repo_dir.exists():
            for fname in license_files:
                p = repo_dir / fname
                if p.exists() and p.is_file():
                    found_license_path = p
                    try:
                        license_content = p.read_text(encoding="utf-8", errors="ignore")
                    except Exception:
                        license_content = ""
                    break

        if found_license_path and license_content:
            spdx_id, method, confidence = self.detect_license_from_text(license_content)
        elif github_api_license and github_api_license.upper() not in ("NONE", "OTHER", "UNKNOWN"):
            spdx_id = github_api_license
            method = "github_api_metadata"
            confidence = 0.85
        else:
            spdx_id = "UNKNOWN"
            method = "missing_license_file"
            confidence = 0.0

        is_allowed = spdx_id in PERMISSIBLE_FOR_RETRIEVAL
        license_status = "approved" if is_allowed else ("unknown" if spdx_id == "UNKNOWN" else "restricted")

        return {
            "repo_url": repo_url,
            "commit_sha": commit_sha or "unknown",
            "license": spdx_id,
            "license_status": license_status,
            "detection_method": method,
            "confidence": round(confidence, 2),
            "license_file_path": str(found_license_path) if found_license_path else None,
            "is_retrieval_permitted": is_allowed,
            "attribution_required": spdx_id not in ("Unlicense",),
            "notes": (
                f"License identified as {spdx_id} with {confidence:.0%} confidence via {method}."
                if is_allowed
                else f"License unverified or restricted ({spdx_id}); external distribution forbidden."
            )
        }


license_manager = LicenseManager()
