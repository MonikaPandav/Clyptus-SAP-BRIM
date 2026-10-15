import re
import time
import logging
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from tavily import TavilyClient

from backend.app.config import settings

logger = logging.getLogger(__name__)

# Strict approved SAP domain allowlist
APPROVED_SAP_DOMAINS = [
    "help.sap.com",
    "community.sap.com",
    "blogs.sap.com",
    "learning.sap.com",
    "sap.com"
]

class WebSearchService:
    """
    Authoritative SAP Web Search Service using Tavily API with official SAP Help Portal fallback.
    """

    def __init__(self):
        self.api_key = settings.WEB_SEARCH_API_KEY.strip()
        self.client: Optional[TavilyClient] = None
        self._cache: Dict[str, Dict[str, Any]] = {}  # query_hash -> {"timestamp": float, "results": list}
        self._cache_ttl = 3600  # 1 hour cache TTL

        if self.api_key:
            try:
                self.client = TavilyClient(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize TavilyClient: {e}")
                self.client = None

    @staticmethod
    def _is_approved_sap_domain(url: str) -> bool:
        """Enforces hard domain restriction on approved SAP domains."""
        try:
            hostname = (urllib.parse.urlsplit(url).hostname or "").lower().rstrip(".")
        except ValueError:
            return False
        return any(hostname == domain or hostname.endswith("." + domain) for domain in APPROVED_SAP_DOMAINS)

    @staticmethod
    def _extract_authority_tier(url: str, domain: str) -> int:
        """
        Determines authority tier:
        Tier 1: Official SAP Product Documentation (help.sap.com, learning.sap.com)
        Tier 2: SAP Community & Expert Blogs (community.sap.com, blogs.sap.com)
        Tier 3: Other verified SAP web resources
        """
        target = f"{url} {domain}".lower()
        if "help.sap.com" in target or "learning.sap.com" in target:
            return 1
        elif "community.sap.com" in target or "blogs.sap.com" in target:
            return 2
        return 3

    @staticmethod
    def _clean_text(value: Any) -> str:
        """Cleans HTML tags, multiple spaces, and escape sequences."""
        if not value:
            return ""
        text = str(value)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _normalize_query(self, query: str) -> str:
        """Normalizes query for deterministic caching."""
        return re.sub(r"[^a-zA-Z0-9\s]", "", query.lower()).strip()

    @staticmethod
    def wants_visuals(query: str) -> bool:
        """Return true only when the user has explicitly asked for visual material."""
        return bool(re.search(
            r"\b(image|images|diagram|architecture\s+diagram|visual|illustration|"
            r"screenshot|screen\s*shot|process\s*flow|flowchart|workflow\s+diagram)\b",
            query or "",
            flags=re.IGNORECASE,
        ))

    def build_image_query(self, query: str, conversation_context: Optional[str] = None) -> str:
        """Build a focused Tavily query without asking the model to invent search terms."""
        base = self._clean_text(query)
        context = self._clean_text(conversation_context or "")
        # Keep relevant prior SAP terms, but cap the request so an entire chat is never sent to Tavily.
        context_terms = " ".join(re.findall(r"\b(?:SAP|BRIM|SOM|FI-CA|CI|Convergent\s+\w+|billable\s+item)\b", context, re.I))
        if "sap" not in base.lower():
            base = f"SAP BRIM {base}"
        visual_hint = "diagram" if re.search(r"diagram|architecture|flow|workflow", base, re.I) else "technical illustration"
        return f"{base} {context_terms} {visual_hint}".strip()[:500]

    @staticmethod
    def _safe_http_url(value: Any) -> str:
        """Only return absolute HTTP(S) URLs to clients; never pass executable schemes through."""
        try:
            url = str(value or "").strip()
            parts = urllib.parse.urlsplit(url)
            if parts.scheme.lower() not in {"http", "https"} or not parts.netloc:
                return ""
            return url
        except (TypeError, ValueError):
            return ""

    def _normalize_images(self, response: Any, query: str, limit: int) -> List[Dict[str, Any]]:
        """Normalize Tavily's top-level and result-attached image shapes defensively."""
        if not isinstance(response, dict):
            return []
        candidates: List[tuple[Any, Dict[str, Any]]] = []
        for image in response.get("images") or response.get("image_results") or []:
            candidates.append((image, {}))
        for result in response.get("results") or []:
            if not isinstance(result, dict):
                continue
            for image in result.get("images") or result.get("image_results") or []:
                candidates.append((image, result))

        terms = {t for t in re.findall(r"[a-z0-9]{3,}", query.lower()) if t not in {"with", "show", "explain", "image", "images", "diagram", "technical"}}
        images: List[Dict[str, Any]] = []
        seen = set()
        for raw, parent in candidates:
            raw = {"url": raw} if isinstance(raw, str) else raw
            if not isinstance(raw, dict):
                continue
            url = self._safe_http_url(raw.get("url") or raw.get("image_url") or raw.get("src"))
            if not url or url in seen:
                continue
            source_url = self._safe_http_url(raw.get("source_url") or raw.get("source") or raw.get("page_url") or parent.get("url"))
            title = self._clean_text(raw.get("source_title") or raw.get("title") or parent.get("title"))
            description = self._clean_text(raw.get("description") or raw.get("image_description") or raw.get("alt") or parent.get("content"))
            alt_text = self._clean_text(raw.get("alt") or raw.get("alt_text") or description or title)
            context = f"{title} {description} {source_url}".lower()
            # Reject obvious unrelated assets but do not require descriptions, which Tavily may omit.
            if terms and context and not any(term in context for term in terms) and "sap" not in context and "brim" not in context:
                continue
            seen.add(url)
            images.append({
                "url": url,
                "description": description or None,
                "alt_text": alt_text or "Relevant SAP technical visual",
                "source_url": source_url or None,
                "source_title": title or None,
                "relevance_score": None,
            })
            if len(images) >= limit:
                break
        return images

    def search_sap_images(self, query: str, conversation_context: Optional[str] = None, max_images: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve relevant visuals without changing evidence selection or grounding scores."""
        if not settings.WEB_FALLBACK_ENABLED or not self.client or not self.wants_visuals(query):
            return []
        limit = max(1, min(max_images or settings.TAVILY_MAX_IMAGES, 8))
        image_query = self.build_image_query(query, conversation_context)
        cache_key = f"images:{self._normalize_query(image_query)}"
        cached = self._cache.get(cache_key)
        if cached and time.time() - cached["timestamp"] < self._cache_ttl:
            return cached["results"][:limit]
        try:
            response = self.client.search(
                query=image_query,
                search_depth="basic",
                max_results=max(limit * 2, settings.TAVILY_MAX_RESULTS),
                include_answer=False,
                include_raw_content=False,
                include_images=True,
                include_image_descriptions=True,
                include_domains=APPROVED_SAP_DOMAINS,
            )
            images = self._normalize_images(response, image_query, limit)
        except Exception as exc:
            logger.warning("[Tavily] Image search failed: %s", exc)
            images = []
        self._cache[cache_key] = {"timestamp": time.time(), "results": images}
        return images

    def _fallback_sap_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """
        Direct fallback search querying official SAP documentation (help.sap.com).
        Guarantees authoritative external evidence if Tavily is unavailable.
        """
        clean_q = f"site:help.sap.com SAP {query}" if not query.lower().startswith("sap") else f"site:help.sap.com {query}"
        try:
            data = urllib.parse.urlencode({"q": clean_q}).encode("utf-8")
            req = urllib.request.Request(
                "https://html.duckduckgo.com/html/",
                data=data,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
                }
            )
            with urllib.request.urlopen(req, timeout=8) as res:
                soup = BeautifulSoup(res.read(), "html.parser")
                raw_results = soup.find_all("div", class_="result")
                parsed = []
                for r in raw_results:
                    link_tag = r.find("a", class_="result__url")
                    snippet_tag = r.find("a", class_="result__snippet")
                    title_tag = r.find("a", class_="result__a")
                    if not link_tag or not title_tag:
                        continue
                    url = link_tag.get("href", "").strip()
                    if not url.startswith("http"):
                        url = "https://" + url
                    title = title_tag.text.strip()
                    snippet = snippet_tag.text.strip() if snippet_tag else ""
                    parsed.append({
                        "title": title,
                        "url": url,
                        "content": snippet
                    })
                    if len(parsed) >= limit * 2:
                        break
                return parsed
        except Exception as e:
            logger.warning(f"Authoritative SAP fallback search error: {e}")
            return []

    def search_sap_authoritative(
        self,
        query: str,
        max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Searches the live web using Tavily with strict SAP domain restrictions.
        Returns deduplicated, structured, authoritative SAP passages.
        """
        if not settings.WEB_FALLBACK_ENABLED:
            return []

        limit = max_results or settings.TAVILY_MAX_RESULTS
        normalized_q = self._normalize_query(query)

        # Check Cache
        cached_entry = self._cache.get(normalized_q)
        if cached_entry:
            if time.time() - cached_entry["timestamp"] < self._cache_ttl:
                logger.info(f"Returning cached Tavily search results for query: '{normalized_q[:40]}'")
                return cached_entry["results"][:limit]

        raw_results = []
        if self.client:
            # Execute Tavily Search with hard domain restriction
            try:
                # Format search query to focus on SAP official material
                search_query = f"SAP {query}" if not query.lower().startswith("sap") else query
                response = self.client.search(
                    query=search_query,
                    search_depth="basic",
                    max_results=limit * 2,  # request extra to allow filtering
                    include_answer=False,
                    include_raw_content=False,
                    include_domains=["help.sap.com"],
                )
                raw_results = response.get("results", []) if isinstance(response, dict) else []
                # The Help Portal is authoritative and preferred. Only broaden to other
                # official SAP properties when that portal search returned nothing.
                if not raw_results:
                    response = self.client.search(
                        query=search_query,
                        search_depth="basic",
                        max_results=limit * 2,
                        include_answer=False,
                        include_raw_content=False,
                        include_domains=APPROVED_SAP_DOMAINS,
                    )
                    raw_results = response.get("results", []) if isinstance(response, dict) else []
            except Exception as exc:
                logger.warning(f"[Tavily] Search API failed for query '{query[:40]}': {exc}. Engaging SAP documentation fallback engine.")
                raw_results = []

        if not raw_results:
            # Fallback to direct authoritative SAP web search
            raw_results = self._fallback_sap_search(query, limit)
        results: List[Dict[str, Any]] = []
        seen_urls = set()

        for item in raw_results:
            url = str(item.get("url", "")).strip()
            if not url or url in seen_urls:
                continue

            # Hard domain restriction check
            if not self._is_approved_sap_domain(url):
                continue

            seen_urls.add(url)

            title = self._clean_text(item.get("title", "")) or "SAP Official Documentation"
            snippet = self._clean_text(item.get("content", "")) or "No preview available."

            # Determine specific domain
            url_lower = url.lower()
            if "help.sap.com" in url_lower:
                domain = "help.sap.com"
            elif "blogs.sap.com" in url_lower:
                domain = "blogs.sap.com"
            elif "community.sap.com" in url_lower:
                domain = "community.sap.com"
            else:
                domain = "help.sap.com"

            authority_tier = self._extract_authority_tier(url, domain)

            results.append({
                "source_id": f"web_{len(results)+1}_{domain}",
                "title": title,
                "url": url,
                "domain": domain,
                "snippet": snippet,
                "chunk_text": f"{title}\n{snippet}",
                "authority_tier": authority_tier,
                "source_type": "web",
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            })

            if len(results) >= limit:
                break

        # Cache results
        self._cache[normalized_q] = {
            "timestamp": time.time(),
            "results": results
        }

        return results


web_search_service = WebSearchService()
