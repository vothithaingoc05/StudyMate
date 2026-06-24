from pydantic import BaseModel, Field


class ChatAskRequest(BaseModel):
    subject_id: int
    question: str = Field(min_length=1)
    top_k: int = Field(default=3, ge=1, le=5)


class RelatedChunkResponse(BaseModel):
    document_id: int
    document_title: str
    chunk_index: int
    content: str
    similarity_score: float


class ChatAskResponse(BaseModel):
    subject_id: int
    subject_name: str
    question: str
    answer: str
    confidence: float
    related_chunks: list[RelatedChunkResponse]
    algorithm: str


class ChatSummarizeRequest(BaseModel):
    subject_id: int
    document_id: int | None = None
    max_sentences: int = Field(default=5, ge=2, le=10)


class ChatSummarizeResponse(BaseModel):
    subject_id: int
    subject_name: str
    document_id: int | None = None
    document_title: str | None = None
    summary: str
    important_keywords: list[str]
    algorithm: str


class QuizGenerateRequest(BaseModel):
    subject_id: int
    document_id: int | None = None
    number_of_questions: int = Field(default=5, ge=1, le=10)


class QuizOptionResponse(BaseModel):
    label: str
    content: str


class QuizQuestionResponse(BaseModel):
    question: str
    options: list[QuizOptionResponse]
    correct_answer: str
    explanation: str
    source_sentence: str


class QuizGenerateResponse(BaseModel):
    subject_id: int
    subject_name: str
    document_id: int | None = None
    document_title: str | None = None
    questions: list[QuizQuestionResponse]
    algorithm: str
    
class SearchDocumentsRequest(BaseModel):
    subject_id: int
    topic: str = Field(min_length=1)
    max_results: int = Field(default=5, ge=1, le=10)


class RecommendedDocumentResponse(BaseModel):
    title: str
    snippet: str
    link: str
    display_link: str | None = None
    relevance_score: float
    matched_keywords: list[str]


class SearchDocumentsResponse(BaseModel):
    subject_id: int
    subject_name: str
    topic: str
    suggested_query: str
    results: list[RecommendedDocumentResponse]


class SaveRecommendedDocumentRequest(BaseModel):
    subject_id: int
    title: str = Field(min_length=1, max_length=255)
    snippet: str | None = None
    link: str = Field(min_length=1, max_length=500)
    content: str = Field(min_length=1)
    keywords: list[str] = []
    relevance_score: float | None = None