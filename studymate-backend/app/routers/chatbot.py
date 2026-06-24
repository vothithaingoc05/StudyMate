import httpx

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.document import Document
from app.models.subject import Subject
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.chatbot_schema import (
    ChatAskRequest,
    ChatAskResponse,
    ChatSummarizeRequest,
    ChatSummarizeResponse,
    QuizGenerateRequest,
    QuizGenerateResponse,
    QuizOptionResponse,
    QuizQuestionResponse,
    RelatedChunkResponse,
    SearchDocumentsRequest,
    SearchDocumentsResponse,
    RecommendedDocumentResponse,
    SaveRecommendedDocumentRequest,
)

from app.services.chatbot_algorithm_service import (
    build_learning_answer,
    build_quiz_questions,
    prepare_document_chunks,
    rank_chunks_by_similarity,
    summarize_by_tfidf,
)

from app.services.web_document_search_service import (
    build_search_query,
    call_google_search_api,
    rank_search_results,
)

router = APIRouter(
    prefix="/api/chatbot",
    tags=["Chatbot"],
)


def get_subject_for_current_user(
    db: Session,
    subject_id: int,
    user_id: int,
) -> Subject:
    subject = db.scalar(
        select(Subject).where(
            Subject.id == subject_id,
            Subject.user_id == user_id,
        )
    )

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy môn học của bạn.",
        )

    return subject


def get_documents_for_subject(
    db: Session,
    subject_id: int,
    user_id: int,
) -> list[Document]:
    documents = db.scalars(
        select(Document)
        .join(Subject, Document.subject_id == Subject.id)
        .where(
            Document.subject_id == subject_id,
            Subject.user_id == user_id,
            Document.processing_status == "DA_XU_LY",
        )
        .order_by(Document.created_at.desc())
    ).all()

    return list(documents)


def get_document_for_current_user(
    db: Session,
    document_id: int,
    subject_id: int,
    user_id: int,
) -> Document:
    document = db.scalar(
        select(Document)
        .join(Subject, Document.subject_id == Subject.id)
        .where(
            Document.id == document_id,
            Document.subject_id == subject_id,
            Subject.user_id == user_id,
        )
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy tài liệu.",
        )

    return document


def build_combined_content(documents: list[Document]) -> str:
    return "\n\n".join(
        [
            f"{document.title}\n{document.content}"
            for document in documents
            if document.content
        ]
    )


@router.post("/ask", response_model=ChatAskResponse)
def ask_chatbot(
    data: ChatAskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subject = get_subject_for_current_user(
        db=db,
        subject_id=data.subject_id,
        user_id=current_user.id,
    )

    documents = get_documents_for_subject(
        db=db,
        subject_id=subject.id,
        user_id=current_user.id,
    )

    if not documents:
        return ChatAskResponse(
            subject_id=subject.id,
            subject_name=subject.name,
            question=data.question,
            answer=(
                "Môn học này chưa có tài liệu học tập nào. "
                "Bạn hãy thêm tài liệu trước để chatbot có thể trả lời dựa trên dữ liệu của bạn."
            ),
            confidence=0,
            related_chunks=[],
            algorithm="TF-IDF + Cosine Similarity",
        )

    chunks = prepare_document_chunks(documents)

    ranked_chunks = rank_chunks_by_similarity(
        question=data.question,
        chunks=chunks,
        top_k=data.top_k,
    )

    answer, confidence = build_learning_answer(
        question=data.question,
        ranked_chunks=ranked_chunks,
    )

    return ChatAskResponse(
        subject_id=subject.id,
        subject_name=subject.name,
        question=data.question,
        answer=answer,
        confidence=confidence,
        related_chunks=[
            RelatedChunkResponse(
                document_id=chunk.document_id,
                document_title=chunk.document_title,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                similarity_score=chunk.similarity_score,
            )
            for chunk in ranked_chunks
        ],
        algorithm="TF-IDF + Cosine Similarity",
    )


@router.post("/summarize", response_model=ChatSummarizeResponse)
def summarize_document(
    data: ChatSummarizeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subject = get_subject_for_current_user(
        db=db,
        subject_id=data.subject_id,
        user_id=current_user.id,
    )

    selected_document: Document | None = None

    if data.document_id:
        selected_document = get_document_for_current_user(
            db=db,
            document_id=data.document_id,
            subject_id=subject.id,
            user_id=current_user.id,
        )

        content = selected_document.content
    else:
        documents = get_documents_for_subject(
            db=db,
            subject_id=subject.id,
            user_id=current_user.id,
        )

        if not documents:
            return ChatSummarizeResponse(
                subject_id=subject.id,
                subject_name=subject.name,
                document_id=None,
                document_title=None,
                summary="Môn học này chưa có tài liệu để tóm tắt.",
                important_keywords=[],
                algorithm="TF-IDF Sentence Scoring",
            )

        content = build_combined_content(documents)

    summary, keywords = summarize_by_tfidf(
        content=content,
        max_sentences=data.max_sentences,
    )

    return ChatSummarizeResponse(
        subject_id=subject.id,
        subject_name=subject.name,
        document_id=selected_document.id if selected_document else None,
        document_title=selected_document.title if selected_document else None,
        summary=summary,
        important_keywords=keywords,
        algorithm="TF-IDF Sentence Scoring",
    )


@router.post("/generate-quiz", response_model=QuizGenerateResponse)
def generate_quiz(
    data: QuizGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subject = get_subject_for_current_user(
        db=db,
        subject_id=data.subject_id,
        user_id=current_user.id,
    )

    selected_document: Document | None = None

    if data.document_id:
        selected_document = get_document_for_current_user(
            db=db,
            document_id=data.document_id,
            subject_id=subject.id,
            user_id=current_user.id,
        )

        content = selected_document.content
    else:
        documents = get_documents_for_subject(
            db=db,
            subject_id=subject.id,
            user_id=current_user.id,
        )

        if not documents:
            return QuizGenerateResponse(
                subject_id=subject.id,
                subject_name=subject.name,
                document_id=None,
                document_title=None,
                questions=[],
                algorithm="TF-IDF Keyword Extraction + Distractor Generation",
            )

        content = build_combined_content(documents)

    raw_questions = build_quiz_questions(
        content=content,
        number_of_questions=data.number_of_questions,
    )

    return QuizGenerateResponse(
        subject_id=subject.id,
        subject_name=subject.name,
        document_id=selected_document.id if selected_document else None,
        document_title=selected_document.title if selected_document else None,
        questions=[
            QuizQuestionResponse(
                question=item["question"],
                options=[
                    QuizOptionResponse(
                        label=option["label"],
                        content=option["content"],
                    )
                    for option in item["options"]
                ],
                correct_answer=item["correct_answer"],
                explanation=item["explanation"],
                source_sentence=item["source_sentence"],
            )
            for item in raw_questions
        ],
        algorithm="TF-IDF Keyword Extraction + Distractor Generation",
    )
    
@router.post("/search-documents", response_model=SearchDocumentsResponse)
async def search_recommended_documents(
    data: SearchDocumentsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subject = get_subject_for_current_user(
        db=db,
        subject_id=data.subject_id,
        user_id=current_user.id,
    )

    documents = get_documents_for_subject(
        db=db,
        subject_id=subject.id,
        user_id=current_user.id,
    )

    suggested_query, keywords = build_search_query(
        subject_name=subject.name,
        topic=data.topic,
        documents=documents,
    )

    try:
        search_items = await call_google_search_api(
            query=suggested_query,
            max_results=data.max_results,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
    
    except httpx.HTTPStatusError as error:
        try:
            error_detail = error.response.json()
        except Exception:
            error_detail = error.response.text

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "message": "Không thể lấy kết quả tìm kiếm từ Search API.",
                "status_code": error.response.status_code,
                "google_error": error_detail,
            },
        )
    
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Kết nối Search API thất bại. Vui lòng thử lại.",
        )

    ranked_results = rank_search_results(
        subject_name=subject.name,
        topic=data.topic,
        documents=documents,
        search_items=search_items,
        keywords=keywords,
    )

    return SearchDocumentsResponse(
        subject_id=subject.id,
        subject_name=subject.name,
        topic=data.topic,
        suggested_query=suggested_query,
        results=[
            RecommendedDocumentResponse(
                title=item["title"],
                snippet=item["snippet"],
                link=item["link"],
                display_link=item["display_link"],
                relevance_score=item["relevance_score"],
                matched_keywords=item["matched_keywords"],
            )
            for item in ranked_results
        ],
    )


@router.post("/save-recommended-document")
def save_recommended_document(
    data: SaveRecommendedDocumentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subject = get_subject_for_current_user(
        db=db,
        subject_id=data.subject_id,
        user_id=current_user.id,
    )

    document = Document(
        subject_id=subject.id,
        title=data.title.strip(),
        source_type="WEB",
        file_name=None,
        file_path=None,
        source_url=data.link.strip(),
        content=data.content.strip(),
        summary=data.snippet.strip() if data.snippet else None,
        keywords=", ".join(data.keywords) if data.keywords else None,
        relevance_score=data.relevance_score,
        processing_status="DA_XU_LY",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return {
        "message": "Đã thêm tài liệu vào kho học tập.",
        "document_id": document.id,
        "title": document.title,
    }