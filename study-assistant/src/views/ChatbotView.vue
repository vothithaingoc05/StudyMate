<template>
	<div class="chatbot-page">
		<div class="page-header">
			<div>
				<h2>Trợ lý học tập</h2>
				<p>Hỏi đáp, tóm tắt tài liệu và tạo câu hỏi ôn tập theo môn học.</p>
			</div>

			<div class="header-actions">
				<select v-model="selectedSubjectId" class="subject-select">
					<option value="">Chọn môn học</option>
					<option v-for="subject in subjects" :key="subject.id" :value="String(subject.id)">
						{{ subject.name }}
					</option>
				</select>
			</div>
		</div>

		<div class="chat-layout">
			<aside class="chat-sidebar">
				<button class="mode-btn" :class="{ active: activeMode === 'ASK' }" @click="activeMode = 'ASK'">
					<i class="bi bi-chat-dots-fill"></i>
					<div>
						<strong>Hỏi đáp</strong>
						<span>Đặt câu hỏi theo tài liệu</span>
					</div>
				</button>

				<button class="mode-btn" :class="{ active: activeMode === 'SUMMARY' }" @click="activeMode = 'SUMMARY'">
					<i class="bi bi-card-text"></i>
					<div>
						<strong>Tóm tắt</strong>
						<span>Rút gọn nội dung cần học</span>
					</div>
				</button>

				<button class="mode-btn" :class="{ active: activeMode === 'QUIZ' }" @click="activeMode = 'QUIZ'">
					<i class="bi bi-ui-checks-grid"></i>
					<div>
						<strong>Tạo trắc nghiệm</strong>
						<span>Luyện tập nhanh từ tài liệu</span>
					</div>
				</button>

				<button class="mode-btn" :class="{ active: activeMode === 'SEARCH' }" @click="activeMode = 'SEARCH'">
					<i class="bi bi-search-heart-fill"></i>
					<div>
						<strong>Tìm tài liệu</strong>
						<span>Gợi ý thêm nguồn học phù hợp</span>
					</div>
				</button>

				<div class="subject-card">
					<h5>Tài liệu môn học</h5>

					<div v-if="selectedSubjectDocuments.length === 0" class="small-empty">
						Chưa có tài liệu cho môn này.
					</div>

					<div v-for="document in selectedSubjectDocuments.slice(0, 5)" :key="document.id"
						class="doc-mini-item">
						<div class="doc-mini-icon">
							<i class="bi bi-file-earmark-text"></i>
						</div>

						<div>
							<p>{{ document.title }}</p>
							<small>{{ document.wordCount }} từ</small>
						</div>
					</div>
				</div>
			</aside>

			<main class="chat-main">
				<div class="chat-card">
					<div class="chat-card-header">
						<div>
							<h4>{{ modeTitle }}</h4>
							<p>{{ modeDescription }}</p>
						</div>

						<button class="clear-btn" @click="clearMessages">
							<i class="bi bi-trash3"></i>
							Xóa hội thoại
						</button>
					</div>

					<div ref="messagesContainer" class="messages-area">
						<div v-if="messages.length === 0" class="welcome-box">
							<div class="welcome-icon">
								<i class="bi bi-stars"></i>
							</div>

							<h5>Xin chào, mình có thể hỗ trợ bạn học tập.</h5>
							<p>
								Hãy chọn môn học, chọn chức năng và nhập yêu cầu của bạn.
							</p>

							<div class="suggestion-list">
								<button @click="useSuggestion('Vòng lặp for trong Python dùng để làm gì?')">
									Vòng lặp for trong Python dùng để làm gì?
								</button>

								<button @click="switchModeWithSuggestion('SUMMARY')">
									Tóm tắt tài liệu môn này
								</button>

								<button @click="switchModeWithSuggestion('QUIZ')">
									Tạo 5 câu hỏi trắc nghiệm để ôn tập
								</button>

								<button @click="switchModeWithSuggestion('SEARCH')">
									Tìm thêm tài liệu học tập cho môn này
								</button>
							</div>
						</div>

						<div v-for="message in messages" :key="message.id" class="message-row" :class="message.role">
							<div class="message-avatar">
								<i class="bi" :class="message.role === 'user' ? 'bi-person-fill' : 'bi-robot'"></i>
							</div>

							<div class="message-bubble">
								<div class="message-content" v-html="formatMessage(message.content)"></div>

								<div v-if="message.relatedChunks?.length" class="reference-box">
									<button class="reference-toggle"
										@click="message.showReferences = !message.showReferences">
										<i class="bi bi-journal-text"></i>
										{{ message.showReferences ? 'Ẩn nội dung liên quan' : 'Xem nội dung liên quan'
										}}
									</button>

									<div v-if="message.showReferences" class="reference-list">
										<div v-for="chunk in message.relatedChunks"
											:key="`${chunk.document_id}-${chunk.chunk_index}`" class="reference-item">
											<strong>{{ chunk.document_title }}</strong>
											<p>{{ chunk.content }}</p>
										</div>
									</div>
								</div>

								<div v-if="message.quiz?.length" class="quiz-list">
									<div v-for="(question, index) in message.quiz" :key="index" class="quiz-card">
										<h5>Câu {{ index + 1 }}: {{ question.question }}</h5>

										<div class="quiz-options">
											<div v-for="option in question.options" :key="option.label"
												class="quiz-option">
												<span>{{ option.label }}</span>
												<p>{{ option.content }}</p>
											</div>
										</div>

										<details>
											<summary>Xem đáp án</summary>
											<p>
												<strong>Đáp án đúng:</strong>
												{{ question.correct_answer }}
											</p>
											<p>{{ question.explanation }}</p>
										</details>
									</div>
								</div>

								<div v-if="message.recommendations?.length" class="recommendation-list">
									<div v-for="(item, index) in message.recommendations" :key="`${item.link}-${index}`"
										class="recommendation-card">
										<div class="recommendation-top">
											<div>
												<h5>{{ item.title }}</h5>
												<small>{{ item.display_link || 'Nguồn tài liệu' }}</small>
											</div>

											<span>{{ Math.round(item.relevance_score) }}%</span>
										</div>

										<p>{{ item.snippet }}</p>

										<div v-if="item.matched_keywords?.length" class="keyword-row">
											<span v-for="keyword in item.matched_keywords.slice(0, 5)" :key="keyword">
												{{ keyword }}
											</span>
										</div>

										<div class="recommendation-actions">
											<a :href="item.link" target="_blank" rel="noopener noreferrer">
												<i class="bi bi-box-arrow-up-right"></i>
												Xem nguồn
											</a>

											<button @click="saveRecommendedDocument(item)">
												<i class="bi bi-plus-circle"></i>
												Thêm vào tài liệu học tập
											</button>
										</div>
									</div>
								</div>

								<small class="message-time">{{ message.time }}</small>
							</div>
						</div>

						<div v-if="isLoading" class="message-row bot">
							<div class="message-avatar">
								<i class="bi bi-robot"></i>
							</div>

							<div class="message-bubble typing">
								<span></span>
								<span></span>
								<span></span>
							</div>
						</div>
					</div>

					<form class="input-area" @submit.prevent="submitMessage">
						<textarea v-model.trim="userInput" rows="2" :placeholder="inputPlaceholder"
							@keydown.enter.exact.prevent="submitMessage"></textarea>

						<button type="submit" :disabled="isLoading || !canSubmit">
							<i class="bi bi-send-fill"></i>
						</button>
					</form>
				</div>
			</main>
		</div>

		<div v-if="toast.message" class="toast-message" :class="toast.type">
			<i class="bi" :class="toast.type === 'success' ? 'bi-check-circle-fill' : 'bi-exclamation-circle-fill'"></i>
			{{ toast.message }}
		</div>
	</div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()

const subjects = ref([])
const documents = ref([])
const selectedSubjectId = ref('')
const activeMode = ref('ASK')
const userInput = ref('')
const messages = ref([])
const isLoading = ref(false)
const messagesContainer = ref(null)

const toast = ref({
	message: '',
	type: 'success',
})

const modeTitle = computed(() => {
	if (activeMode.value === 'SUMMARY') return 'Tóm tắt tài liệu'
	if (activeMode.value === 'QUIZ') return 'Tạo câu hỏi trắc nghiệm'
	if (activeMode.value === 'SEARCH') return 'Tìm thêm tài liệu'
	return 'Hỏi đáp học tập'
})

const modeDescription = computed(() => {
	if (activeMode.value === 'SUMMARY') {
		return 'Tạo bản tóm tắt ngắn gọn từ tài liệu của môn học.'
	}

	if (activeMode.value === 'QUIZ') {
		return 'Tạo câu hỏi trắc nghiệm để bạn luyện tập và kiểm tra kiến thức.'
	}

	if (activeMode.value === 'SEARCH') {
		return 'Tìm thêm tài liệu học tập phù hợp với môn học bạn đang chọn.'
	}

	return 'Đặt câu hỏi và nhận câu trả lời dựa trên tài liệu học tập đã lưu.'
})

const inputPlaceholder = computed(() => {
	if (activeMode.value === 'SUMMARY') {
		return 'Ví dụ: Tóm tắt tài liệu môn này thành các ý chính...'
	}

	if (activeMode.value === 'QUIZ') {
		return 'Ví dụ: Tạo 5 câu hỏi trắc nghiệm từ tài liệu môn này...'
	}

	if (activeMode.value === 'SEARCH') {
		return 'Ví dụ: Tìm thêm tài liệu về FastAPI, vòng lặp Python, REST API...'
	}

	return 'Nhập câu hỏi của bạn...'
})

const selectedSubjectDocuments = computed(() => {
	if (!selectedSubjectId.value) return []

	return documents.value.filter(
		(document) => String(document.subjectId) === String(selectedSubjectId.value),
	)
})

const canSubmit = computed(() => {
	return Boolean(selectedSubjectId.value && userInput.value.trim())
})

const selectedSubject = computed(() => {
	return subjects.value.find(
		(subject) => String(subject.id) === String(selectedSubjectId.value),
	)
})

const mapSubjectFromApi = (subject) => ({
	id: subject.id,
	name: subject.name,
})

const mapDocumentFromApi = (document) => ({
	id: document.id,
	subjectId: document.subject_id,
	title: document.title,
	content: document.content || '',
	wordCount: document.word_count || 0,
})

const showToast = (message, type = 'success') => {
	toast.value = { message, type }

	setTimeout(() => {
		toast.value.message = ''
	}, 2600)
}

const handleApiError = (error, fallbackMessage) => {
	if (error.response?.status === 401) {
		router.push('/dang-nhap')
		return 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.'
	}

	return error.response?.data?.detail || fallbackMessage
}

const loadData = async () => {
	try {
		const [subjectsResponse, documentsResponse] = await Promise.all([
			api.get('/subjects'),
			api.get('/documents'),
		])

		subjects.value = subjectsResponse.data.map(mapSubjectFromApi)
		documents.value = documentsResponse.data.map(mapDocumentFromApi)

		if (!selectedSubjectId.value && subjects.value.length > 0) {
			selectedSubjectId.value = String(subjects.value[0].id)
		}
	} catch (error) {
		showToast(
			handleApiError(error, 'Không thể tải dữ liệu. Vui lòng thử lại.'),
			'error',
		)
	}
}

const addMessage = (role, content, extra = {}) => {
	messages.value.push({
		id: Date.now() + Math.random(),
		role,
		content,
		time: new Date().toLocaleTimeString('vi-VN', {
			hour: '2-digit',
			minute: '2-digit',
		}),
		showReferences: false,
		...extra,
	})

	scrollToBottom()
}

const scrollToBottom = async () => {
	await nextTick()

	if (messagesContainer.value) {
		messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
	}
}

const clearMessages = () => {
	messages.value = []
}

const useSuggestion = (text) => {
	activeMode.value = 'ASK'
	userInput.value = text
}

const switchModeWithSuggestion = (mode) => {
	activeMode.value = mode

	if (mode === 'SUMMARY') {
		userInput.value = 'Tóm tắt tài liệu môn này thành các ý chính.'
	}

	if (mode === 'QUIZ') {
		userInput.value = 'Tạo 5 câu hỏi trắc nghiệm để ôn tập.'
	}

	if (mode === 'SEARCH') {
		userInput.value = 'Tìm thêm tài liệu học tập phù hợp cho môn này.'
	}
}

const submitMessage = async () => {
	if (!selectedSubjectId.value) {
		showToast('Vui lòng chọn môn học trước.', 'error')
		return
	}

	if (!userInput.value.trim()) {
		return
	}

	if (activeMode.value !== 'SEARCH' && selectedSubjectDocuments.value.length === 0) {
		showToast('Môn học này chưa có tài liệu. Vui lòng thêm tài liệu trước.', 'error')
		return
	}

	const currentInput = userInput.value.trim()
	addMessage('user', currentInput)
	userInput.value = ''
	isLoading.value = true

	try {
		if (activeMode.value === 'ASK') {
			await askQuestion(currentInput)
		}

		if (activeMode.value === 'SUMMARY') {
			await summarizeDocuments()
		}

		if (activeMode.value === 'QUIZ') {
			await generateQuiz()
		}

		if (activeMode.value === 'SEARCH') {
			await searchDocuments(currentInput)
		}
	} catch (error) {
		addMessage(
			'bot',
			handleApiError(error, 'Mình chưa thể xử lý yêu cầu này. Bạn thử lại nhé.'),
		)
	} finally {
		isLoading.value = false
	}
}

const askQuestion = async (question) => {
	const response = await api.post('/chatbot/ask', {
		subject_id: Number(selectedSubjectId.value),
		question,
		top_k: 3,
	})

	addMessage('bot', response.data.answer, {
		relatedChunks: response.data.related_chunks || [],
	})
}

const summarizeDocuments = async () => {
	const response = await api.post('/chatbot/summarize', {
		subject_id: Number(selectedSubjectId.value),
		document_id: null,
		max_sentences: 5,
	})

	const keywords = response.data.important_keywords || []

	let content = `Mình đã tóm tắt tài liệu môn ${response.data.subject_name}:\n\n${response.data.summary}`

	if (keywords.length > 0) {
		content += `\n\nMột số ý chính cần chú ý:\n${keywords
			.slice(0, 8)
			.map((keyword) => `- ${keyword}`)
			.join('\n')}`
	}

	addMessage('bot', content)
}

const generateQuiz = async () => {
	const response = await api.post('/chatbot/generate-quiz', {
		subject_id: Number(selectedSubjectId.value),
		document_id: null,
		number_of_questions: 5,
	})

	const questions = response.data.questions || []

	if (questions.length === 0) {
		addMessage(
			'bot',
			'Mình chưa tạo được câu hỏi từ tài liệu hiện tại. Bạn có thể bổ sung thêm nội dung chi tiết hơn cho môn học này.',
		)
		return
	}

	addMessage('bot', 'Mình đã tạo bộ câu hỏi trắc nghiệm để bạn ôn tập:', {
		quiz: questions,
	})
}

const searchDocuments = async (topic) => {
	const response = await api.post('/chatbot/search-documents', {
		subject_id: Number(selectedSubjectId.value),
		topic,
		max_results: 5,
	})

	const results = response.data.results || []

	if (results.length === 0) {
		addMessage(
			'bot',
			'Mình chưa tìm thấy tài liệu phù hợp. Bạn thử nhập chủ đề cụ thể hơn nhé.',
		)
		return
	}

	addMessage('bot', 'Mình tìm được một số tài liệu có thể hữu ích cho bạn:', {
		recommendations: results,
	})
}

const saveRecommendedDocument = async (item) => {
	if (!selectedSubjectId.value) {
		showToast('Vui lòng chọn môn học trước.', 'error')
		return
	}

	try {
		await api.post('/chatbot/save-recommended-document', {
			subject_id: Number(selectedSubjectId.value),
			title: item.title,
			snippet: item.snippet,
			link: item.link,
			content: `${item.title}\n\n${item.snippet}\n\nNguồn: ${item.link}`,
			keywords: item.matched_keywords || [],
			relevance_score: item.relevance_score || null,
		})

		showToast('Đã thêm tài liệu vào kho học tập.')
		await loadData()
	} catch (error) {
		showToast(
			handleApiError(error, 'Không thể thêm tài liệu. Vui lòng thử lại.'),
			'error',
		)
	}
}

const formatMessage = (content) => {
	if (!content) return ''

	return content
		.replace(/&/g, '&amp;')
		.replace(/</g, '&lt;')
		.replace(/>/g, '&gt;')
		.replace(/\n/g, '<br />')
}

watch(activeMode, () => {
	userInput.value = ''
})

onMounted(() => {
	loadData()
})
</script>

<style scoped>
.chatbot-page {
	position: relative;
}

.page-header {
	margin-bottom: 25px;
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 18px;
}

.page-header h2 {
	margin: 0 0 7px;
	color: var(--sm-text);
	font-size: 27px;
	font-weight: 700;
}

.page-header p {
	margin: 0;
	color: var(--sm-text-soft);
}

.subject-select {
	min-width: 230px;
	height: 45px;
	padding: 0 14px;
	border: 1px solid var(--sm-border);
	border-radius: 12px;
	color: var(--sm-text);
	background: #fffdfa;
	outline: none;
}

.subject-select:focus {
	border-color: var(--sm-primary);
	box-shadow: 0 0 0 3px var(--sm-primary-soft);
}

.chat-layout {
	display: grid;
	grid-template-columns: 310px 1fr;
	gap: 22px;
}

.chat-sidebar {
	display: flex;
	flex-direction: column;
	gap: 14px;
}

.mode-btn {
	width: 100%;
	padding: 17px;
	border: 1px solid var(--sm-border);
	border-radius: 17px;
	color: var(--sm-text);
	background: var(--sm-card);
	box-shadow: var(--sm-shadow-sm);
	display: flex;
	align-items: center;
	gap: 14px;
	text-align: left;
}

.mode-btn i {
	width: 44px;
	height: 44px;
	flex-shrink: 0;
	border-radius: 13px;
	color: var(--sm-primary);
	background: var(--sm-primary-soft);
	font-size: 22px;
	display: flex;
	align-items: center;
	justify-content: center;
}

.mode-btn strong {
	display: block;
	margin-bottom: 4px;
	font-size: 15px;
}

.mode-btn span {
	color: var(--sm-text-soft);
	font-size: 13px;
}

.mode-btn.active {
	border-color: var(--sm-primary);
	background: linear-gradient(135deg, #fffaf4, var(--sm-accent-soft));
}

.mode-btn.active i {
	color: white;
	background: linear-gradient(135deg, var(--sm-primary), var(--sm-accent));
}

.subject-card {
	margin-top: 6px;
	padding: 20px;
	border: 1px solid var(--sm-border);
	border-radius: 18px;
	background: var(--sm-card);
	box-shadow: var(--sm-shadow-sm);
}

.subject-card h5 {
	margin: 0 0 15px;
	color: var(--sm-text);
	font-weight: 700;
}

.small-empty {
	color: var(--sm-text-soft);
	font-size: 14px;
}

.doc-mini-item {
	padding: 12px 0;
	border-bottom: 1px solid #f2e8dd;
	display: flex;
	align-items: center;
	gap: 12px;
}

.doc-mini-item:last-child {
	border-bottom: none;
}

.doc-mini-icon {
	width: 38px;
	height: 38px;
	border-radius: 11px;
	color: var(--sm-primary);
	background: var(--sm-primary-soft);
	display: flex;
	align-items: center;
	justify-content: center;
}

.doc-mini-item p {
	margin: 0 0 3px;
	color: var(--sm-text);
	font-size: 14px;
	font-weight: 600;
}

.doc-mini-item small {
	color: var(--sm-text-soft);
}

.chat-card {
	height: calc(100vh - 175px);
	min-height: 650px;
	border: 1px solid var(--sm-border);
	border-radius: 22px;
	background: var(--sm-card);
	box-shadow: var(--sm-shadow-sm);
	display: flex;
	flex-direction: column;
	overflow: hidden;
}

.chat-card-header {
	padding: 21px 24px;
	border-bottom: 1px solid var(--sm-border);
	display: flex;
	align-items: center;
	justify-content: space-between;
}

.chat-card-header h4 {
	margin: 0 0 5px;
	color: var(--sm-text);
	font-weight: 700;
}

.chat-card-header p {
	margin: 0;
	color: var(--sm-text-soft);
	font-size: 14px;
}

.clear-btn {
	height: 39px;
	padding: 0 13px;
	border: 1px solid var(--sm-border);
	border-radius: 10px;
	color: var(--sm-text-soft);
	background: #fffdfa;
	font-size: 13px;
	display: inline-flex;
	align-items: center;
	gap: 7px;
}

.messages-area {
	flex: 1;
	padding: 24px;
	overflow-y: auto;
	background:
		radial-gradient(circle at 12% 0%, rgba(217, 174, 118, 0.12), transparent 24%),
		#fffaf4;
}

.welcome-box {
	max-width: 520px;
	margin: 70px auto;
	padding: 30px;
	border: 1px solid var(--sm-border);
	border-radius: 22px;
	background: rgba(255, 253, 250, 0.88);
	text-align: center;
}

.welcome-icon {
	width: 70px;
	height: 70px;
	margin: 0 auto 18px;
	border-radius: 50%;
	color: white;
	background: linear-gradient(135deg, var(--sm-primary), var(--sm-accent));
	font-size: 32px;
	display: flex;
	align-items: center;
	justify-content: center;
}

.welcome-box h5 {
	margin: 0 0 9px;
	color: var(--sm-text);
	font-weight: 700;
}

.welcome-box p {
	margin: 0 0 18px;
	color: var(--sm-text-soft);
}

.suggestion-list {
	display: flex;
	flex-direction: column;
	gap: 9px;
}

.suggestion-list button {
	padding: 11px 14px;
	border: 1px solid var(--sm-border);
	border-radius: 12px;
	color: var(--sm-text);
	background: #fffdfa;
	text-align: left;
}

.message-row {
	margin-bottom: 18px;
	display: flex;
	align-items: flex-start;
	gap: 12px;
}

.message-row.user {
	flex-direction: row-reverse;
}

.message-avatar {
	width: 39px;
	height: 39px;
	flex-shrink: 0;
	border-radius: 50%;
	color: white;
	background: linear-gradient(135deg, var(--sm-primary), var(--sm-accent));
	display: flex;
	align-items: center;
	justify-content: center;
}

.message-row.bot .message-avatar {
	background: #3b2f2a;
}

.message-bubble {
	max-width: 76%;
	padding: 15px 17px;
	border-radius: 17px;
	color: var(--sm-text);
	background: #fffdfa;
	box-shadow: 0 8px 22px rgba(83, 56, 36, 0.08);
}

.message-row.user .message-bubble {
	color: white;
	background: linear-gradient(135deg, var(--sm-primary), var(--sm-accent));
}

.message-content {
	line-height: 1.7;
	font-size: 14px;
}

.message-time {
	display: block;
	margin-top: 9px;
	color: rgba(48, 40, 33, 0.5);
	font-size: 11px;
}

.message-row.user .message-time {
	color: rgba(255, 255, 255, 0.75);
}

.reference-box {
	margin-top: 14px;
}

.reference-toggle {
	padding: 8px 11px;
	border: 1px solid var(--sm-border);
	border-radius: 10px;
	color: var(--sm-primary-dark);
	background: var(--sm-primary-soft);
	font-size: 13px;
	font-weight: 600;
}

.reference-list {
	margin-top: 10px;
	display: flex;
	flex-direction: column;
	gap: 9px;
}

.reference-item {
	padding: 12px;
	border-radius: 11px;
	background: var(--sm-accent-soft);
}

.reference-item strong {
	color: var(--sm-text);
	font-size: 13px;
}

.reference-item p {
	margin: 6px 0 0;
	color: var(--sm-text-soft);
	font-size: 13px;
	line-height: 1.6;
}

.quiz-list {
	margin-top: 14px;
	display: flex;
	flex-direction: column;
	gap: 14px;
}

.quiz-card {
	padding: 15px;
	border: 1px solid var(--sm-border);
	border-radius: 14px;
	background: #fffaf4;
}

.quiz-card h5 {
	margin: 0 0 12px;
	color: var(--sm-text);
	font-size: 15px;
	font-weight: 700;
	line-height: 1.5;
}

.quiz-options {
	display: grid;
	gap: 8px;
}

.quiz-option {
	padding: 9px 10px;
	border-radius: 10px;
	background: #fffdfa;
	display: flex;
	align-items: center;
	gap: 9px;
}

.quiz-option span {
	width: 26px;
	height: 26px;
	flex-shrink: 0;
	border-radius: 50%;
	color: white;
	background: var(--sm-primary);
	font-size: 12px;
	font-weight: 700;
	display: flex;
	align-items: center;
	justify-content: center;
}

.quiz-option p {
	margin: 0;
	color: var(--sm-text);
	font-size: 14px;
}

.quiz-card details {
	margin-top: 12px;
}

.quiz-card summary {
	cursor: pointer;
	color: var(--sm-primary-dark);
	font-weight: 700;
}

.quiz-card details p {
	margin: 8px 0 0;
	color: var(--sm-text-soft);
	line-height: 1.6;
}

.typing {
	width: 78px;
	display: flex;
	gap: 5px;
}

.typing span {
	width: 8px;
	height: 8px;
	border-radius: 50%;
	background: var(--sm-primary);
	animation: typing 1s infinite ease-in-out;
}

.typing span:nth-child(2) {
	animation-delay: 0.15s;
}

.typing span:nth-child(3) {
	animation-delay: 0.3s;
}

.input-area {
	padding: 18px;
	border-top: 1px solid var(--sm-border);
	background: var(--sm-card);
	display: flex;
	gap: 12px;
}

.input-area textarea {
	flex: 1;
	padding: 13px 15px;
	border: 1px solid var(--sm-border);
	border-radius: 14px;
	outline: none;
	color: var(--sm-text);
	background: #fffdfa;
	resize: none;
}

.input-area textarea:focus {
	border-color: var(--sm-primary);
	box-shadow: 0 0 0 3px var(--sm-primary-soft);
}

.input-area button {
	width: 52px;
	border: none;
	border-radius: 14px;
	color: white;
	background: linear-gradient(135deg, var(--sm-primary), var(--sm-accent));
	font-size: 20px;
}

.input-area button:disabled {
	cursor: not-allowed;
	opacity: 0.55;
}

.toast-message {
	position: fixed;
	z-index: 500;
	top: 94px;
	right: 28px;
	padding: 14px 18px;
	border-radius: 11px;
	color: white;
	box-shadow: 0 10px 30px rgba(67, 45, 30, 0.16);
	display: flex;
	align-items: center;
	gap: 9px;
}

.toast-message.success {
	background: var(--sm-success);
}

.toast-message.error {
	background: var(--sm-danger);
}

.recommendation-list {
	margin-top: 14px;
	display: flex;
	flex-direction: column;
	gap: 14px;
}

.recommendation-card {
	padding: 15px;
	border: 1px solid var(--sm-border);
	border-radius: 14px;
	background: #fffaf4;
}

.recommendation-top {
	margin-bottom: 10px;
	display: flex;
	justify-content: space-between;
	gap: 14px;
}

.recommendation-top h5 {
	margin: 0 0 4px;
	color: var(--sm-text);
	font-size: 15px;
	font-weight: 700;
	line-height: 1.4;
}

.recommendation-top small {
	color: var(--sm-text-soft);
}

.recommendation-top span {
	min-width: 54px;
	height: 32px;
	padding: 0 10px;
	border-radius: 20px;
	color: white;
	background: linear-gradient(135deg, var(--sm-primary), var(--sm-accent));
	font-size: 13px;
	font-weight: 700;
	display: flex;
	align-items: center;
	justify-content: center;
}

.recommendation-card>p {
	margin: 0 0 12px;
	color: var(--sm-text-soft);
	font-size: 14px;
	line-height: 1.6;
}

.keyword-row {
	margin-bottom: 13px;
	display: flex;
	flex-wrap: wrap;
	gap: 7px;
}

.keyword-row span {
	padding: 5px 9px;
	border-radius: 20px;
	color: var(--sm-primary-dark);
	background: var(--sm-primary-soft);
	font-size: 12px;
	font-weight: 600;
}

.recommendation-actions {
	display: flex;
	flex-wrap: wrap;
	gap: 9px;
}

.recommendation-actions a,
.recommendation-actions button {
	height: 37px;
	padding: 0 13px;
	border-radius: 10px;
	font-size: 13px;
	font-weight: 700;
	display: inline-flex;
	align-items: center;
	gap: 7px;
	text-decoration: none;
}

.recommendation-actions a {
	border: 1px solid var(--sm-border);
	color: var(--sm-text);
	background: #fffdfa;
}

.recommendation-actions button {
	border: none;
	color: white;
	background: linear-gradient(135deg, var(--sm-primary), var(--sm-accent));
}

@keyframes typing {

	0%,
	80%,
	100% {
		transform: translateY(0);
		opacity: 0.4;
	}

	40% {
		transform: translateY(-4px);
		opacity: 1;
	}
}

@media (max-width: 1200px) {
	.chat-layout {
		grid-template-columns: 1fr;
	}

	.chat-sidebar {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
	}

	.subject-card {
		grid-column: 1 / -1;
	}
}

@media (max-width: 768px) {

	.page-header,
	.chat-card-header {
		flex-direction: column;
		align-items: flex-start;
	}

	.subject-select {
		width: 100%;
	}

	.chat-sidebar {
		grid-template-columns: 1fr;
	}

	.chat-card {
		height: auto;
		min-height: 680px;
	}

	.message-bubble {
		max-width: 88%;
	}
}
</style>