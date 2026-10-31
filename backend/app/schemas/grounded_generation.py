from typing import List, Optional, Dict, Any, Literal, Union
from pydantic import BaseModel, Field, model_validator


class AnswerSection(BaseModel):
    title: str = Field(description="Section heading or title")
    module: str = Field(description="Primary SAP module for this section (e.g. SOM, CC, CI, FI-CA, RAR, General)")


class CalculationItem(BaseModel):
    formula: str = Field(description="Mathematical or accounting formula applied (e.g. Transaction Price Allocation)")
    inputs: Union[Dict[str, Any], str] = Field(description="Input variables and monetary values")
    result: str = Field(description="Calculated monetary or unit result")
    citations: List[str] = Field(default_factory=list, description="Chunk IDs substantiating formula or parameters")


class GroundedClaim(BaseModel):
    claim_id: str = Field(description="Unique identifier for the claim (e.g. c1, c2)")
    text: str = Field(description="Factual claim text backed by cited chunks")
    citations: List[str] = Field(default_factory=list, description="List of exact chunk_ids supporting this claim")
    identifiers_used: List[str] = Field(
        default_factory=list,
        description="Exact technical identifiers (T-codes, tables, programs, fields, config paths). Acronyms belong to glossary."
    )
    module: str = Field(default="General", description="Primary SAP module for this claim")
    support: Literal["direct", "inferred"] = Field(
        default="direct",
        description="Direct statement from text vs grounded architectural inference"
    )


class GroundedAnswerResponse(BaseModel):
    summary: str = Field(default="", description="Executive summary of the answer")
    sections: List[AnswerSection] = Field(default_factory=list, description="Structured answer sections")
    claims: List[GroundedClaim] = Field(default_factory=list, description="List of verified factual claims")
    calculations: List[CalculationItem] = Field(
        default_factory=list,
        description="Deterministic calculations for pricing, allocation, or rating"
    )
    premise_correction: Optional[str] = Field(
        default=None,
        description="Explicit correction if user query contains an invalid or false premise"
    )
    gaps: List[str] = Field(
        default_factory=list,
        description="Specific sub-questions or technical aspects not covered by the knowledge base chunks"
    )
    next_questions: List[str] = Field(
        default_factory=list,
        description="Clickable proactive next questions for technical exploration"
    )
    is_abstention: bool = Field(default=False, description="Whether the answer is an abstention due to lack of knowledge")
    abstention_reason: Optional[str] = Field(default=None, description="Reason for abstention if applicable")

    @model_validator(mode="before")
    @classmethod
    def handle_gaps_alias(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Support alias between 'not_covered' and 'gaps'
            if "not_covered" in data and "gaps" not in data:
                data["gaps"] = data["not_covered"]
            elif "gaps" in data and "not_covered" not in data:
                data["not_covered"] = data["gaps"]
        return data


class PackedChunk(BaseModel):
    chunk_id: str
    tier: str  # official_sap, book, official-sap-domain, forum, self_authored
    module: str  # SOM, CC, CI, FI-CA, RAR, General, etc.
    source: str
    page: int
    text: str
    score: float = 0.0
    tier_weight: float = 1.0
    final_rank_score: float = 0.0

    def to_context_header(self) -> str:
        return f"[{self.chunk_id} | {self.tier} | {self.module} | {self.source} | {self.page}]"

    def format_chunk(self) -> str:
        return f"{self.to_context_header()}\n{self.text.strip()}"


class ContextPackingResult(BaseModel):
    packed_chunks: List[PackedChunk] = Field(default_factory=list)
    packed_text: str = ""
    detected_question_modules: List[str] = Field(default_factory=list)
    covered_question_modules: List[str] = Field(default_factory=list)
    uncovered_question_modules: List[str] = Field(default_factory=list)
    is_insufficient: bool = False
    top_score: float = 0.0
    closest_sources: List[Dict[str, Any]] = Field(default_factory=list)
    total_estimated_tokens: int = 0
    token_budget: int = 3000
