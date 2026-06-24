import re
from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


VIETNAMESE_STOPWORDS = {
    "là", "và", "của", "có", "cho", "trong", "với", "một", "các", "những",
    "được", "khi", "thì", "để", "này", "đó", "từ", "về", "theo", "ra",
    "vào", "trên", "dưới", "nếu", "như", "hay", "hoặc", "tại", "bởi",
    "em", "tôi", "bạn", "mình", "hãy", "giúp", "nêu", "cho", "biết",
}


@dataclass
class DocumentChunk:
    document_id: int
    document_title: str
    chunk_index: int
    content: str


@dataclass
class RankedChunk:
    document_id: int
    document_title: str
    chunk_index: int
    content: str
    similarity_score: float


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\sÀ-ỹ]", " ", text)
    return text.strip()


def tokenize_keywords(text: str) -> list[str]:
    normalized_text = normalize_text(text)
    words = normalized_text.split()

    return [
        word
        for word in words
        if len(word) >= 2 and word not in VIETNAMESE_STOPWORDS
    ]


def build_chunks(content: str, max_length: int = 450) -> list[str]:
    if not content or not content.strip():
        return []

    clean_content = re.sub(r"\s+", " ", content).strip()

    sentences = re.split(r"(?<=[.!?。！？])\s+", clean_content)
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    chunks: list[str] = []
    current_chunk = ""

    for sentence in sentences:
        candidate = f"{current_chunk} {sentence}".strip() if current_chunk else sentence

        if len(candidate) > max_length and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk = candidate

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks if chunks else [clean_content]


def prepare_document_chunks(documents) -> list[DocumentChunk]:
    all_chunks: list[DocumentChunk] = []

    for document in documents:
        chunks = build_chunks(document.content)

        for index, chunk in enumerate(chunks, start=1):
            all_chunks.append(
                DocumentChunk(
                    document_id=document.id,
                    document_title=document.title,
                    chunk_index=index,
                    content=chunk,
                )
            )

    return all_chunks


def rank_chunks_by_similarity(
    question: str,
    chunks: list[DocumentChunk],
    top_k: int = 3,
) -> list[RankedChunk]:
    if not chunks:
        return []

    corpus = [chunk.content for chunk in chunks]
    corpus.append(question)

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        token_pattern=r"(?u)\b\w+\b",
    )

    tfidf_matrix = vectorizer.fit_transform(corpus)

    question_vector = tfidf_matrix[-1]
    chunk_vectors = tfidf_matrix[:-1]

    scores = cosine_similarity(question_vector, chunk_vectors).flatten()
    ranked_indexes = scores.argsort()[::-1][:top_k]

    ranked_chunks: list[RankedChunk] = []

    for index in ranked_indexes:
        chunk = chunks[index]
        score = float(scores[index])

        ranked_chunks.append(
            RankedChunk(
                document_id=chunk.document_id,
                document_title=chunk.document_title,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                similarity_score=round(score, 4),
            )
        )

    return ranked_chunks


def build_learning_answer(
    question: str,
    ranked_chunks: list[RankedChunk],
) -> tuple[str, float]:
    if not ranked_chunks:
        return (
            "Hiện tại mình chưa tìm thấy tài liệu phù hợp để trả lời câu hỏi này. "
            "Bạn có thể thêm tài liệu học tập cho môn học trước, sau đó hỏi lại nhé.",
            0,
        )

    best_chunk = ranked_chunks[0]
    confidence = round(best_chunk.similarity_score * 100, 2)

    if best_chunk.similarity_score < 0.05:
        answer = (
            "Mình chưa tìm thấy nội dung thật sự liên quan trong tài liệu hiện có. "
            "Bạn nên bổ sung thêm tài liệu cho môn học này hoặc thử đặt câu hỏi cụ thể hơn.\n\n"
            "Nội dung gần nhất mình tìm được:\n"
            f"{best_chunk.content}"
        )

        return answer, confidence

    keywords = tokenize_keywords(question)
    keyword_text = ", ".join(keywords[:8]) if keywords else "chưa xác định"

    related_text = "\n\n".join(
        [
            f"- {chunk.content}"
            for chunk in ranked_chunks
            if chunk.similarity_score > 0
        ]
    )

    answer = (
        f"Dựa trên tài liệu học tập, mình tìm thấy nội dung phù hợp nhất trong tài liệu "
        f"“{best_chunk.document_title}”.\n\n"
        f"Câu trả lời:\n"
        f"{best_chunk.content}\n\n"
        f"Từ khóa liên quan:\n"
        f"{keyword_text}\n\n"
        f"Các đoạn tài liệu liên quan:\n"
        f"{related_text}\n\n"
        f"Gợi ý ôn tập:\n"
        f"Bạn nên đọc lại các đoạn trên, ghi chú những khái niệm chính và tự đặt thêm ví dụ "
        f"để hiểu rõ hơn nội dung này."
    )

    return answer, confidence


def split_sentences(content: str) -> list[str]:
    if not content or not content.strip():
        return []

    clean_content = re.sub(r"\s+", " ", content).strip()

    sentences = re.split(r"(?<=[.!?。！？])\s+", clean_content)

    return [
        sentence.strip()
        for sentence in sentences
        if len(sentence.strip()) >= 30
    ]


def extract_keywords_by_tfidf(
    texts: list[str],
    top_n: int = 10,
) -> list[str]:
    if not texts:
        return []

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        token_pattern=r"(?u)\b\w+\b",
    )

    tfidf_matrix = vectorizer.fit_transform(texts)
    feature_names = vectorizer.get_feature_names_out()

    scores = tfidf_matrix.sum(axis=0).A1
    ranked_indexes = scores.argsort()[::-1]

    keywords: list[str] = []

    for index in ranked_indexes:
        keyword = feature_names[index].strip()

        if len(keyword) < 2:
            continue

        if keyword in VIETNAMESE_STOPWORDS:
            continue

        if keyword not in keywords:
            keywords.append(keyword)

        if len(keywords) >= top_n:
            break

    return keywords


def summarize_by_tfidf(
    content: str,
    max_sentences: int = 5,
) -> tuple[str, list[str]]:
    sentences = split_sentences(content)

    if not sentences:
        return "Tài liệu chưa đủ nội dung để tóm tắt.", []

    if len(sentences) <= max_sentences:
        keywords = extract_keywords_by_tfidf(sentences, top_n=10)
        return " ".join(sentences), keywords

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        token_pattern=r"(?u)\b\w+\b",
    )

    tfidf_matrix = vectorizer.fit_transform(sentences)
    sentence_scores = tfidf_matrix.sum(axis=1).A1

    ranked_indexes = sentence_scores.argsort()[::-1][:max_sentences]
    ranked_indexes = sorted(ranked_indexes)

    selected_sentences = [
        sentences[index]
        for index in ranked_indexes
    ]

    keywords = extract_keywords_by_tfidf(sentences, top_n=10)
    summary = " ".join(selected_sentences)

    return summary, keywords


def choose_answer_keyword(sentence: str, keywords: list[str]) -> str | None:
    sentence_lower = sentence.lower()

    for keyword in keywords:
        if keyword.lower() in sentence_lower and len(keyword.split()) <= 3:
            return keyword

    words = tokenize_keywords(sentence)

    if not words:
        return None

    words = sorted(words, key=len, reverse=True)

    return words[0]


def generate_distractors(
    correct_answer: str,
    all_keywords: list[str],
    max_options: int = 3,
) -> list[str]:
    distractors: list[str] = []

    for keyword in all_keywords:
        if keyword.lower() == correct_answer.lower():
            continue

        if keyword.lower() in correct_answer.lower():
            continue

        if correct_answer.lower() in keyword.lower():
            continue

        if keyword not in distractors:
            distractors.append(keyword)

        if len(distractors) >= max_options:
            break

    fallback_options = [
        "biến",
        "hàm",
        "vòng lặp",
        "điều kiện",
        "danh sách",
        "chuỗi",
        "đối tượng",
        "tham số",
    ]

    for option in fallback_options:
        if option.lower() == correct_answer.lower():
            continue

        if option not in distractors:
            distractors.append(option)

        if len(distractors) >= max_options:
            break

    return distractors[:max_options]


def build_quiz_questions(
    content: str,
    number_of_questions: int = 5,
) -> list[dict]:
    sentences = split_sentences(content)

    if not sentences:
        return []

    summary, keywords = summarize_by_tfidf(
        content=content,
        max_sentences=min(number_of_questions * 2, 10),
    )

    candidate_sentences = split_sentences(summary)

    if not candidate_sentences:
        candidate_sentences = sentences

    questions: list[dict] = []
    labels = ["A", "B", "C", "D"]

    for sentence in candidate_sentences:
        if len(questions) >= number_of_questions:
            break

        correct_answer = choose_answer_keyword(sentence, keywords)

        if not correct_answer:
            continue

        question_text = sentence.replace(correct_answer, "_____")

        if question_text == sentence:
            continue

        distractors = generate_distractors(correct_answer, keywords, max_options=3)
        options = [correct_answer] + distractors

        options = sorted(options, key=lambda item: (len(item), item.lower()))

        correct_label = labels[options.index(correct_answer)]

        questions.append(
            {
                "question": f"Điền từ/cụm từ phù hợp vào chỗ trống: {question_text}",
                "options": [
                    {
                        "label": labels[index],
                        "content": option,
                    }
                    for index, option in enumerate(options)
                ],
                "correct_answer": correct_label,
                "explanation": (
                    f"Đáp án đúng là {correct_label}. "
                    f"Theo tài liệu, nội dung liên quan là: {sentence}"
                ),
                "source_sentence": sentence,
            }
        )

    return questions