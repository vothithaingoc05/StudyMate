<template>
	<div class="documents-page">
		<div class="page-header">
			<div>
				<h2>Tài liệu học tập</h2>
				<p>Lưu trữ tài liệu theo từng môn học để dễ học, ôn tập và tra cứu.</p>
			</div>

			<button class="primary-btn" @click="openAddModal">
				<i class="bi bi-plus-lg"></i>
				Thêm tài liệu
			</button>
		</div>

		<div class="row g-4 mb-4">
			<div class="col-xl-3 col-md-6">
				<div class="summary-card">
					<div class="summary-icon total">
						<i class="bi bi-file-earmark-text-fill"></i>
					</div>
					<div>
						<p>Tổng tài liệu</p>
						<h3>{{ documents.length }}</h3>
					</div>
				</div>
			</div>

			<div class="col-xl-3 col-md-6">
				<div class="summary-card">
					<div class="summary-icon subject">
						<i class="bi bi-book-half"></i>
					</div>
					<div>
						<p>Môn có tài liệu</p>
						<h3>{{ subjectsWithDocuments }}</h3>
					</div>
				</div>
			</div>

			<div class="col-xl-3 col-md-6">
				<div class="summary-card">
					<div class="summary-icon chunks">
						<i class="bi bi-diagram-3-fill"></i>
					</div>
					<div>
						<p>Đoạn đã xử lý</p>
						<h3>{{ totalChunks }}</h3>
					</div>
				</div>
			</div>

			<div class="col-xl-3 col-md-6">
				<div class="summary-card">
					<div class="summary-icon ready">
						<i class="bi bi-check-circle-fill"></i>
					</div>
					<div>
						<p>Sẵn sàng ôn tập</p>
						<h3>{{ processedDocuments }}</h3>
					</div>
				</div>
			</div>
		</div>

		<div class="row g-4">
			<div class="col-xl-8">
				<div class="content-card">
					<div class="toolbar">
						<div>
							<h5>Kho tài liệu của bạn</h5>
						</div>

						<div class="filters">
							<div class="search-box">
								<i class="bi bi-search"></i>
								<input v-model="searchKeyword" type="text" placeholder="Tìm tài liệu..." />
							</div>

							<select v-model="selectedSubject">
								<option value="">Tất cả môn học</option>
								<option v-for="subject in subjects" :key="subject.id" :value="String(subject.id)">
									{{ subject.name }}
								</option>
							</select>
						</div>
					</div>

					<div v-if="isLoading" class="loading-state">
						<span class="loading-spinner"></span>
						<p>Đang tải tài liệu học tập...</p>
					</div>

					<div v-else-if="apiError" class="api-error-state">
						<div class="error-api-icon">
							<i class="bi bi-exclamation-circle"></i>
						</div>
						<h5>Không thể tải dữ liệu</h5>
						<p>{{ apiError }}</p>
						<button class="retry-btn" @click="loadInitialData">
							<i class="bi bi-arrow-clockwise"></i>
							Thử lại
						</button>
					</div>

					<div v-else-if="filteredDocuments.length === 0" class="empty-state">
						<div class="empty-icon">
							<i class="bi bi-file-earmark-x"></i>
						</div>
						<h5>Chưa có tài liệu phù hợp</h5>
						<p>Hãy thêm tài liệu để bắt đầu học tập và ôn tập dễ dàng hơn.</p>
						<button class="primary-btn" @click="openAddModal">
							<i class="bi bi-plus-lg"></i>
							Thêm tài liệu
						</button>
					</div>

					<div v-else class="document-list">
						<div v-for="document in filteredDocuments" :key="document.id" class="document-card">
							<div class="document-icon">
								<i :class="getDocumentIcon(document.sourceType)"></i>
							</div>

							<div class="document-main">
								<div class="document-heading">
									<div>
										<div class="title-row">
											<h4>{{ document.title }}</h4>
											<span class="status-badge" :class="document.processingStatus.toLowerCase()">
												{{ getProcessingText(document.processingStatus) }}
											</span>
										</div>

										<p class="document-subject">
											<i class="bi bi-book"></i>
											{{ document.subjectName }}

											<span class="separator">•</span>

											<i class="bi bi-calendar3"></i>
											{{ formatDate(document.createdAt) }}
										</p>
									</div>

									<div class="action-group">
										<button class="action-btn view" title="Xem chi tiết"
											@click="openDetailModal(document)">
											<i class="bi bi-eye"></i>
										</button>

										<button class="action-btn edit" title="Sửa tài liệu"
											@click="openEditModal(document)">
											<i class="bi bi-pencil-square"></i>
										</button>

										<button class="action-btn delete" title="Xóa tài liệu"
											@click="confirmDelete(document)">
											<i class="bi bi-trash3"></i>
										</button>
									</div>
								</div>

								<p class="content-preview">
									{{ getContentPreview(document.content) }}
								</p>

								<div class="document-footer">
									<span class="meta-badge">
										<i class="bi bi-layers-fill"></i>
										{{ document.chunks.length }} đoạn
									</span>

									<span class="meta-badge">
										<i class="bi bi-fonts"></i>
										{{ document.wordCount }} từ
									</span>

									<span class="meta-badge source">
										<i class="bi bi-database-fill-check"></i>
										{{ getSourceText(document.sourceType) }}
									</span>

									<span v-if="document.fileName" class="meta-badge file">
										<i class="bi bi-paperclip"></i>
										{{ document.fileName }}
									</span>

									<span v-if="document.sourceUrl" class="meta-badge web">
										<i class="bi bi-link-45deg"></i>
										Nguồn web
									</span>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- Right panel -->
			<div class="col-xl-4">


				<div class="subject-doc-card">
					<h5>Tài liệu theo môn học</h5>

					<div v-for="subject in subjects" :key="subject.id" class="subject-document-item">
						<div class="subject-color" :style="{ backgroundColor: subject.color || '#B9824C' }"></div>

						<div>
							<p>{{ subject.name }}</p>
							<small>{{ getDocumentCountBySubject(subject.id) }} tài liệu</small>
						</div>

						<strong>{{ getDocumentCountBySubject(subject.id) }}</strong>
					</div>
				</div>
			</div>
		</div>

		<!-- Add/Edit Modal -->
		<div v-if="isModalOpen" class="modal-overlay" @click.self="closeModal">
			<div class="modal-card">
				<div class="modal-header-custom">
					<div>
						<h4>{{ isEditing ? 'Cập nhật tài liệu' : 'Thêm tài liệu học tập' }}</h4>
						<p>Lưu nội dung để sử dụng trong quá trình học và ôn tập.</p>
					</div>

					<button class="close-btn" @click="closeModal">
						<i class="bi bi-x-lg"></i>
					</button>
				</div>

				<form @submit.prevent="saveDocument">
					<div class="form-group">
						<label>Tiêu đề tài liệu <span>*</span></label>
						<input v-model.trim="form.title" type="text" placeholder="Ví dụ: Vòng lặp trong Python"
							:class="{ invalid: errors.title }" />
						<small v-if="errors.title" class="error-text">{{ errors.title }}</small>
					</div>

					<div class="form-group">
						<label>Môn học <span>*</span></label>
						<select v-model="form.subjectId" :class="{ invalid: errors.subjectId }">
							<option value="">Chọn môn học</option>
							<option v-for="subject in subjects" :key="subject.id" :value="String(subject.id)">
								{{ subject.name }}
							</option>
						</select>
						<small v-if="errors.subjectId" class="error-text">
							{{ errors.subjectId }}
						</small>
					</div>

					<div class="source-type-box">
						<label class="source-option" :class="{ active: form.sourceType === 'TEXT' }">
							<input v-model="form.sourceType" type="radio" value="TEXT" />
							<i class="bi bi-pencil-square"></i>
							<div>
								<strong>Nhập văn bản</strong>
								<small>Gõ hoặc dán nội dung bài học</small>
							</div>
						</label>

						<label class="source-option" :class="{ active: form.sourceType === 'FILE' }">
							<input v-model="form.sourceType" type="radio" value="FILE" />
							<i class="bi bi-file-earmark-arrow-up"></i>
							<div>
								<strong>Tải file</strong>
								<small>Đọc nội dung file văn bản</small>
							</div>
						</label>

						<label class="source-option" :class="{ active: form.sourceType === 'WEB' }">
							<input v-model="form.sourceType" type="radio" value="WEB" />
							<i class="bi bi-globe2"></i>
							<div>
								<strong>Nguồn web</strong>
								<small>Lưu tài liệu từ link ngoài</small>
							</div>
						</label>
					</div>

					<div v-if="form.sourceType === 'FILE'" class="upload-area">
						<input ref="fileInput" type="file" accept=".txt,.pdf,.doc,.docx" @change="handleFileUpload" />

						<div class="upload-content">
							<i class="bi bi-cloud-arrow-up-fill"></i>
							<p>{{ form.fileName || 'Chọn file TXT, PDF hoặc DOCX' }}</p>
							<small>Hỗ trợ TXT, PDF, DOCX. File .doc cũ nên chuyển sang .docx.</small>
						</div>
					</div>

					<div v-if="form.sourceType === 'WEB'" class="form-group">
						<label>Link nguồn tài liệu</label>
						<input v-model.trim="form.sourceUrl" type="text" placeholder="https://..." />
					</div>

					<div class="form-group">
						<label>Nội dung tài liệu <span>*</span></label>
						<textarea v-model.trim="form.content" rows="9"
							placeholder="Nhập hoặc dán nội dung tài liệu tại đây..."
							:class="{ invalid: errors.content }"></textarea>

						<div class="content-counter">
							<small v-if="errors.content" class="error-text">
								{{ errors.content }}
							</small>
							<small v-else>
								{{ countWords(form.content) }} từ ·
								{{ previewChunks.length }} đoạn dự kiến
							</small>
						</div>
					</div>

					<div class="form-group">
						<label>Từ khóa</label>
						<input v-model.trim="form.keywords" type="text"
							placeholder="Ví dụ: Python, vòng lặp, for, while" />
					</div>

					<div class="form-group">
						<label>Tóm tắt ngắn</label>
						<textarea v-model.trim="form.summary" rows="3"
							placeholder="Tóm tắt ngắn nội dung tài liệu..."></textarea>
					</div>

					<div v-if="previewChunks.length > 0" class="chunk-preview-box">
						<div class="chunk-preview-header">
							<h5>Xem trước đoạn nội dung</h5>
							<span>{{ previewChunks.length }} đoạn</span>
						</div>

						<div v-for="(chunk, index) in previewChunks.slice(0, 3)" :key="index"
							class="chunk-preview-item">
							<strong>Đoạn {{ index + 1 }}</strong>
							<p>{{ chunk }}</p>
						</div>

						<small v-if="previewChunks.length > 3" class="more-chunks">
							Và {{ previewChunks.length - 3 }} đoạn khác...
						</small>
					</div>

					<div class="modal-footer-custom">
						<button type="button" class="cancel-btn" @click="closeModal">
							Hủy
						</button>

						<button type="submit" class="save-btn" :disabled="isSaving">
							<template v-if="!isSaving">
								<i class="bi bi-check-lg"></i>
								{{ isEditing ? 'Lưu thay đổi' : 'Lưu tài liệu' }}
							</template>

							<template v-else>
								<span class="button-spinner"></span>
								Đang lưu...
							</template>
						</button>
					</div>
				</form>
			</div>
		</div>

		<!-- Detail Modal -->
		<div v-if="selectedDocument" class="modal-overlay" @click.self="selectedDocument = null">
			<div class="detail-modal">
				<div class="modal-header-custom">
					<div>
						<h4>{{ selectedDocument.title }}</h4>
						<p>
							{{ selectedDocument.subjectName }} ·
							{{ selectedDocument.chunks.length }} đoạn nội dung
						</p>
					</div>

					<button class="close-btn" @click="selectedDocument = null">
						<i class="bi bi-x-lg"></i>
					</button>
				</div>

				<div v-if="selectedDocument.sourceUrl" class="source-link-box">
					<i class="bi bi-link-45deg"></i>
					<span>{{ selectedDocument.sourceUrl }}</span>
				</div>

				<div v-if="selectedDocument.summary" class="full-content">
					<h5>Tóm tắt</h5>
					<p>{{ selectedDocument.summary }}</p>
				</div>

				<div class="full-content">
					<h5>Nội dung tài liệu</h5>
					<p>{{ selectedDocument.content }}</p>
				</div>

				<div class="chunks-detail">
					<div class="detail-title">
						<h5>Nội dung đã chia nhỏ</h5>
						<span>{{ selectedDocument.chunks.length }} đoạn</span>
					</div>

					<div v-for="(chunk, index) in selectedDocument.chunks" :key="index" class="chunk-detail-item">
						<div class="chunk-number">{{ index + 1 }}</div>
						<p>{{ chunk }}</p>
					</div>
				</div>
			</div>
		</div>

		<!-- Delete Modal -->
		<div v-if="documentToDelete" class="modal-overlay" @click.self="documentToDelete = null">
			<div class="delete-modal">
				<div class="delete-icon">
					<i class="bi bi-trash3"></i>
				</div>

				<h4>Xóa tài liệu?</h4>
				<p>
					Bạn có chắc muốn xóa tài liệu
					<strong>{{ documentToDelete.title }}</strong> không?
				</p>

				<div class="delete-actions">
					<button class="cancel-btn" @click="documentToDelete = null">
						Hủy
					</button>

					<button class="confirm-delete-btn" :disabled="isDeleting" @click="deleteDocument">
						{{ isDeleting ? 'Đang xóa...' : 'Xóa tài liệu' }}
					</button>
				</div>
			</div>
		</div>

		<div v-if="toast.message" class="toast-message" :class="toast.type">
			<i class="bi" :class="toast.type === 'success' ? 'bi-check-circle-fill' : 'bi-exclamation-circle-fill'"></i>
			{{ toast.message }}
		</div>
	</div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()

const documents = ref([])
const subjects = ref([])

const searchKeyword = ref('')
const selectedSubject = ref('')

const isLoading = ref(false)
const isSaving = ref(false)
const isDeleting = ref(false)
const apiError = ref('')

const isModalOpen = ref(false)
const isEditing = ref(false)
const editingId = ref(null)

const selectedDocument = ref(null)
const documentToDelete = ref(null)
const fileInput = ref(null)

const toast = ref({
	message: '',
	type: 'success',
})

const form = ref({
	subjectId: '',
	title: '',
	sourceType: 'TEXT',
	fileName: '',
	filePath: '',
	sourceUrl: '',
	content: '',
	summary: '',
	keywords: '',
	uploadFile: null,
})

const errors = ref({
	title: '',
	subjectId: '',
	content: '',
})

const previewChunks = computed(() => buildChunks(form.value.content))

const totalChunks = computed(() => {
	return documents.value.reduce(
		(total, document) => total + document.chunks.length,
		0,
	)
})

const processedDocuments = computed(() => {
	return documents.value.filter(
		(document) => document.processingStatus === 'DA_XU_LY',
	).length
})

const subjectsWithDocuments = computed(() => {
	return new Set(documents.value.map((document) => String(document.subjectId))).size
})

const filteredDocuments = computed(() => {
	const keyword = searchKeyword.value.trim().toLowerCase()

	return [...documents.value]
		.filter((document) => {
			const matchesKeyword =
				document.title.toLowerCase().includes(keyword) ||
				document.content.toLowerCase().includes(keyword) ||
				document.subjectName.toLowerCase().includes(keyword) ||
				(document.keywords || '').toLowerCase().includes(keyword)

			const matchesSubject =
				!selectedSubject.value ||
				String(document.subjectId) === String(selectedSubject.value)

			return matchesKeyword && matchesSubject
		})
		.sort(
			(first, second) =>
				new Date(second.createdAt).getTime() - new Date(first.createdAt).getTime(),
		)
})

const mapSubjectFromApi = (subject) => ({
	id: subject.id,
	name: subject.name,
	color: subject.color || '#B9824C',
})

const mapDocumentFromApi = (document) => ({
	id: document.id,
	subjectId: document.subject_id,
	subjectName: document.subject_name,
	title: document.title,
	sourceType: document.source_type,
	fileName: document.file_name || '',
	filePath: document.file_path || '',
	sourceUrl: document.source_url || '',
	content: document.content || '',
	summary: document.summary || '',
	keywords: document.keywords || '',
	relevanceScore: document.relevance_score,
	processingStatus: document.processing_status || 'DA_XU_LY',
	chunks: document.chunks || [],
	wordCount: document.word_count || countWords(document.content || ''),
	createdAt: document.created_at,
	updatedAt: document.updated_at,
})

const showToast = (message, type = 'success') => {
	toast.value = { message, type }

	setTimeout(() => {
		toast.value.message = ''
	}, 2800)
}

const handleApiError = (error, fallbackMessage) => {
	if (error.response?.status === 401) {
		router.push('/dang-nhap')
		return 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.'
	}

	return error.response?.data?.detail || fallbackMessage
}

const fetchSubjects = async () => {
	const response = await api.get('/subjects')
	subjects.value = response.data.map(mapSubjectFromApi)
}

const fetchDocuments = async () => {
	const response = await api.get('/documents')
	documents.value = response.data.map(mapDocumentFromApi)
}

const loadInitialData = async () => {
	isLoading.value = true
	apiError.value = ''

	try {
		await Promise.all([fetchSubjects(), fetchDocuments()])
	} catch (error) {
		apiError.value = handleApiError(
			error,
			'Không thể kết nối hệ thống. Vui lòng thử lại.',
		)
	} finally {
		isLoading.value = false
	}
}

const emptyForm = () => ({
	subjectId: subjects.value[0]?.id ? String(subjects.value[0].id) : '',
	title: '',
	sourceType: 'TEXT',
	fileName: '',
	filePath: '',
	sourceUrl: '',
	content: '',
	summary: '',
	keywords: '',
	uploadFile: null,
})

const resetErrors = () => {
	errors.value = {
		title: '',
		subjectId: '',
		content: '',
	}
}

const openAddModal = () => {
	isEditing.value = false
	editingId.value = null
	form.value = emptyForm()
	resetErrors()
	isModalOpen.value = true
}

const openEditModal = (document) => {
	isEditing.value = true
	editingId.value = document.id


	form.value = {
		subjectId: String(document.subjectId),
		title: document.title,
		sourceType: document.sourceType || 'TEXT',
		fileName: document.fileName || '',
		filePath: document.filePath || '',
		sourceUrl: document.sourceUrl || '',
		content: document.content || '',
		summary: document.summary || '',
		keywords: document.keywords || '',
		uploadFile: null,
	}

	resetErrors()
	isModalOpen.value = true


}

const closeModal = () => {
	if (isSaving.value) return

	isModalOpen.value = false
	resetErrors()

	if (fileInput.value) {
		fileInput.value.value = ''
	}
}

const openDetailModal = (document) => {
	selectedDocument.value = document
}

const validateForm = () => {
	resetErrors()
	let valid = true

	if (!form.value.title.trim()) {
		errors.value.title = 'Vui lòng nhập tiêu đề tài liệu.'
		valid = false
	}

	if (!form.value.subjectId) {
		errors.value.subjectId = 'Vui lòng chọn môn học.'
		valid = false
	}

	if (
		!form.value.content.trim() &&
		!(form.value.sourceType === 'FILE' && form.value.uploadFile)
	) {
		errors.value.content = 'Vui lòng nhập nội dung tài liệu hoặc chọn file tải lên.'
		valid = false
	}

	return valid
}

const buildPayload = () => ({
	subject_id: Number(form.value.subjectId),
	title: form.value.title.trim(),
	source_type: form.value.sourceType,
	file_name: form.value.fileName.trim() || null,
	file_path: form.value.filePath.trim() || null,
	source_url: form.value.sourceUrl.trim() || null,
	content: form.value.content.trim(),
	summary: form.value.summary.trim() || null,
	keywords: form.value.keywords.trim() || null,
	relevance_score: null,
})

const uploadDocumentFile = async () => {
	if (!form.value.uploadFile) {
		showToast('Vui lòng chọn file trước khi lưu.', 'error')
		return
	}

	const formData = new FormData()

	formData.append('subject_id', String(form.value.subjectId))
	formData.append('title', form.value.title.trim())
	formData.append('file', form.value.uploadFile, form.value.uploadFile.name)

	const response = await api.post('/documents/upload', formData, {
		headers: {
			'Content-Type': 'multipart/form-data',
		},
	})

	documents.value.unshift(mapDocumentFromApi(response.data))
}

const saveDocument = async () => {
	if (!validateForm()) return

	isSaving.value = true

	try {
		if (!isEditing.value && form.value.sourceType === 'FILE' && form.value.uploadFile) {
			await uploadDocumentFile()
			showToast('Tải file và thêm tài liệu thành công.')
			closeModal()
			return
		}

		if (isEditing.value) {
			const response = await api.put(
				`/documents/${editingId.value}`,
				buildPayload(),
			)

			const updatedDocument = mapDocumentFromApi(response.data)
			const index = documents.value.findIndex(
				(document) => document.id === editingId.value,
			)

			if (index !== -1) {
				documents.value[index] = updatedDocument
			}

			showToast('Cập nhật tài liệu thành công.')
		} else {
			const response = await api.post('/documents', buildPayload())
			documents.value.unshift(mapDocumentFromApi(response.data))
			showToast('Thêm tài liệu thành công.')
		}

		closeModal()
	} catch (error) {
		showToast(
			handleApiError(error, 'Không thể lưu tài liệu. Vui lòng thử lại.'),
			'error',
		)
	} finally {
		isSaving.value = false
	}
}

const confirmDelete = (document) => {
	documentToDelete.value = document
}

const deleteDocument = async () => {
	if (!documentToDelete.value) return

	isDeleting.value = true

	try {
		await api.delete(`/documents/${documentToDelete.value.id}`)

		documents.value = documents.value.filter(
			(document) => document.id !== documentToDelete.value.id,
		)

		documentToDelete.value = null
		showToast('Đã xóa tài liệu.')
	} catch (error) {
		showToast(
			handleApiError(error, 'Không thể xóa tài liệu.'),
			'error',
		)
	} finally {
		isDeleting.value = false
	}
}

const handleFileUpload = (event) => {
	const file = event.target.files[0]

	if (!file) return

	const lowerFileName = file.name.toLowerCase()

	const isAllowedFile =
		lowerFileName.endsWith('.txt') ||
		lowerFileName.endsWith('.pdf') ||
		lowerFileName.endsWith('.doc') ||
		lowerFileName.endsWith('.docx')

	if (!isAllowedFile) {
		showToast('Chỉ hỗ trợ file .txt, .pdf, .doc hoặc .docx.', 'error')
		event.target.value = ''
		return
	}

	form.value.uploadFile = file
	form.value.fileName = file.name

	if (!form.value.title) {
		form.value.title = file.name.replace(/\.(txt|pdf|doc|docx)$/i, '')
	}

	if (lowerFileName.endsWith('.txt')) {
		const reader = new FileReader()

		reader.onload = (readerEvent) => {
			form.value.content = readerEvent.target.result
		}

		reader.readAsText(file, 'UTF-8')
	} else {
		form.value.content = ''
	}
}

const getDocumentCountBySubject = (subjectId) => {
	return documents.value.filter(
		(document) => String(document.subjectId) === String(subjectId),
	).length
}

const countWords = (content) => {
	if (!content || !content.trim()) return 0
	return content.trim().split(/\s+/).length
}

const buildChunks = (content, maxLength = 450) => {
	if (!content || !content.trim()) return []

	const cleanContent = content.replace(/\s+/g, ' ').trim()
	const sentences = cleanContent
		.split(/(?<=[.!?。！？])\s+/)
		.filter((sentence) => sentence.trim())

	const chunks = []
	let currentChunk = ''

	sentences.forEach((sentence) => {
		const candidate = currentChunk ? `${currentChunk} ${sentence}` : sentence

		if (candidate.length > maxLength && currentChunk) {
			chunks.push(currentChunk.trim())
			currentChunk = sentence
		} else {
			currentChunk = candidate
		}
	})

	if (currentChunk) {
		chunks.push(currentChunk.trim())
	}

	return chunks.length > 0 ? chunks : [cleanContent]
}

const getContentPreview = (content) => {
	if (!content) return ''
	if (content.length <= 180) return content
	return `${content.slice(0, 180)}...`
}

const formatDate = (dateValue) => {
	if (!dateValue) return '---'

	return new Date(dateValue).toLocaleDateString('vi-VN', {
		day: '2-digit',
		month: '2-digit',
		year: 'numeric',
	})
}

const getProcessingText = (status) => {
	const statusText = {
		CHO_XU_LY: 'Chờ xử lý',
		DA_XU_LY: 'Đã xử lý',
		LOI: 'Lỗi',
	}

	return statusText[status] || status
}

const getSourceText = (sourceType) => {
	const sourceText = {
		TEXT: 'Văn bản',
		FILE: 'File tải lên',
		WEB: 'Web',
	}

	return sourceText[sourceType] || sourceType
}

const getDocumentIcon = (sourceType) => {
	if (sourceType === 'FILE') return 'bi bi-file-earmark-arrow-up-fill'
	if (sourceType === 'WEB') return 'bi bi-globe2'
	return 'bi bi-file-earmark-text-fill'
}

onMounted(() => {
	loadInitialData()
})
</script>

<style scoped>
.documents-page {
	position: relative;
}

.page-header {
	margin-bottom: 25px;
	display: flex;
	align-items: center;
	justify-content: space-between;
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

.primary-btn {
	height: 47px;
	padding: 0 20px;
	border: none;
	border-radius: 12px;
	color: white;
	background: linear-gradient(135deg, var(--sm-primary), var(--sm-accent));
	box-shadow: 0 10px 22px rgba(185, 130, 76, 0.2);
	font-weight: 600;
	display: inline-flex;
	align-items: center;
	gap: 9px;
}

.summary-card {
	height: 110px;
	padding: 22px;
	border: 1px solid var(--sm-border);
	border-radius: 18px;
	background: var(--sm-card);
	box-shadow: var(--sm-shadow-sm);
	display: flex;
	align-items: center;
	gap: 18px;
}

.summary-icon {
	width: 56px;
	height: 56px;
	border-radius: 15px;
	font-size: 25px;
	display: flex;
	justify-content: center;
	align-items: center;
}

.summary-icon.total,
.summary-icon.subject {
	color: var(--sm-primary);
	background: var(--sm-primary-soft);
}

.summary-icon.chunks {
	color: var(--sm-success);
	background: var(--sm-success-bg);
}

.summary-icon.ready {
	color: var(--sm-warning);
	background: var(--sm-warning-bg);
}

.summary-card p {
	margin: 0 0 6px;
	color: var(--sm-text-soft);
	font-size: 14px;
}

.summary-card h3 {
	margin: 0;
	color: var(--sm-text);
	font-size: 28px;
	font-weight: 700;
}

.content-card,
.subject-doc-card {
	padding: 24px;
	border: 1px solid var(--sm-border);
	border-radius: 19px;
	background: var(--sm-card);
	box-shadow: var(--sm-shadow-sm);
}

.toolbar {
	margin-bottom: 24px;
	display: flex;
	justify-content: space-between;
	gap: 18px;
}

.toolbar h5,
.subject-doc-card h5 {
	margin: 0 0 5px;
	color: var(--sm-text);
	font-weight: 700;
}

.toolbar p {
	margin: 0;
	color: var(--sm-text-soft);
	font-size: 14px;
}

.filters {
	display: flex;
	gap: 9px;
}

.search-box {
	width: 225px;
	height: 43px;
	padding: 0 13px;
	border: 1px solid var(--sm-border);
	border-radius: 11px;
	color: var(--sm-text-soft);
	background: #fffdfa;
	display: flex;
	align-items: center;
	gap: 8px;
}

.search-box input {
	width: 100%;
	border: none;
	outline: none;
	color: var(--sm-text);
	background: transparent;
}

.filters select {
	height: 43px;
	min-width: 160px;
	padding: 0 11px;
	border: 1px solid var(--sm-border);
	border-radius: 11px;
	color: var(--sm-text);
	background: #fffdfa;
}

.loading-state,
.api-error-state,
.empty-state {
	padding: 56px 20px;
	text-align: center;
}

.loading-spinner {
	width: 39px;
	height: 39px;
	margin: 0 auto;
	border: 4px solid #ead8c3;
	border-top-color: var(--sm-primary);
	border-radius: 50%;
	display: block;
	animation: spin 0.75s linear infinite;
}

.loading-state p,
.api-error-state p,
.empty-state p {
	margin-top: 16px;
	color: var(--sm-text-soft);
}

.empty-icon,
.error-api-icon {
	width: 68px;
	height: 68px;
	margin: 0 auto 18px;
	border-radius: 50%;
	font-size: 31px;
	display: flex;
	justify-content: center;
	align-items: center;
}

.empty-icon {
	color: var(--sm-primary);
	background: var(--sm-primary-soft);
}

.error-api-icon {
	color: var(--sm-danger);
	background: var(--sm-danger-bg);
}

.empty-state h5,
.api-error-state h5 {
	color: var(--sm-text);
	font-weight: 700;
}

.retry-btn {
	height: 45px;
	padding: 0 18px;
	border: 1px solid var(--sm-border-strong);
	border-radius: 11px;
	color: var(--sm-primary-dark);
	background: var(--sm-primary-soft);
	font-weight: 600;
}

.document-list {
	display: flex;
	flex-direction: column;
	gap: 15px;
}

.document-card {
	padding: 19px;
	border: 1px solid var(--sm-border);
	border-left: 5px solid var(--sm-primary);
	border-radius: 16px;
	background: #fffdfa;
	display: flex;
	gap: 17px;
	transition: 0.2s;
}

.document-card:hover {
	border-color: var(--sm-border-strong);
	box-shadow: var(--sm-shadow-sm);
}

.document-icon {
	width: 55px;
	height: 55px;
	flex-shrink: 0;
	border-radius: 14px;
	color: var(--sm-primary);
	background: var(--sm-primary-soft);
	font-size: 25px;
	display: flex;
	justify-content: center;
	align-items: center;
}

.document-main {
	flex: 1;
}

.document-heading {
	display: flex;
	justify-content: space-between;
	gap: 14px;
}

.title-row {
	display: flex;
	align-items: center;
	gap: 9px;
	flex-wrap: wrap;
}

.title-row h4 {
	margin: 0;
	color: var(--sm-text);
	font-size: 17px;
	font-weight: 700;
}

.status-badge {
	padding: 5px 10px;
	border-radius: 20px;
	font-size: 11px;
	font-weight: 700;
}

.status-badge.da_xu_ly {
	color: var(--sm-success);
	background: var(--sm-success-bg);
}

.status-badge.cho_xu_ly {
	color: var(--sm-warning);
	background: var(--sm-warning-bg);
}

.status-badge.loi {
	color: var(--sm-danger);
	background: var(--sm-danger-bg);
}

.document-subject {
	margin: 8px 0 0;
	color: var(--sm-text-soft);
	font-size: 13px;
	display: flex;
	align-items: center;
	gap: 7px;
	flex-wrap: wrap;
}

.action-group {
	display: flex;
	gap: 7px;
}

.action-btn {
	width: 36px;
	height: 36px;
	border: none;
	border-radius: 9px;
}

.action-btn.view {
	color: var(--sm-primary-dark);
	background: var(--sm-primary-soft);
}

.action-btn.edit {
	color: var(--sm-warning);
	background: var(--sm-warning-bg);
}

.action-btn.delete {
	color: var(--sm-danger);
	background: var(--sm-danger-bg);
}

.content-preview {
	margin: 14px 0;
	color: var(--sm-text-soft);
	font-size: 14px;
	line-height: 1.6;
}

.document-footer {
	display: flex;
	flex-wrap: wrap;
	gap: 8px;
}

.meta-badge {
	padding: 6px 11px;
	border-radius: 20px;
	color: var(--sm-primary-dark);
	background: var(--sm-primary-soft);
	font-size: 12px;
	font-weight: 600;
	display: inline-flex;
	align-items: center;
	gap: 6px;
}

.meta-badge.file,
.meta-badge.web {
	color: var(--sm-success);
	background: var(--sm-success-bg);
}


.subject-doc-card h5 {
	margin-bottom: 18px;
}

.subject-document-item {
	padding: 12px 0;
	border-bottom: 1px solid #f2e8dd;
	display: flex;
	align-items: center;
	gap: 11px;
}

.subject-document-item:last-child {
	border-bottom: none;
}

.subject-color {
	width: 8px;
	height: 39px;
	border-radius: 20px;
}

.subject-document-item div:nth-child(2) {
	flex: 1;
}

.subject-document-item p {
	margin: 0 0 3px;
	color: var(--sm-text);
	font-size: 14px;
	font-weight: 600;
}

.subject-document-item small {
	color: var(--sm-text-soft);
}

.subject-document-item strong {
	color: var(--sm-primary-dark);
	font-size: 18px;
}

.modal-overlay {
	position: fixed;
	inset: 0;
	z-index: 300;
	padding: 22px;
	background: rgba(48, 40, 33, 0.48);
	backdrop-filter: blur(3px);
	display: flex;
	justify-content: center;
	align-items: center;
}

.modal-card,
.detail-modal {
	width: 720px;
	max-width: 100%;
	max-height: 94vh;
	overflow-y: auto;
	padding: 27px;
	border: 1px solid var(--sm-border);
	border-radius: 20px;
	background: var(--sm-card);
	box-shadow: var(--sm-shadow-md);
}

.modal-header-custom {
	margin-bottom: 23px;
	display: flex;
	justify-content: space-between;
}

.modal-header-custom h4 {
	margin: 0 0 6px;
	color: var(--sm-text);
	font-weight: 700;
}

.modal-header-custom p {
	margin: 0;
	color: var(--sm-text-soft);
	font-size: 14px;
}

.close-btn {
	width: 38px;
	height: 38px;
	border: none;
	border-radius: 9px;
	color: var(--sm-text);
	background: var(--sm-accent-soft);
}

.form-group {
	margin-bottom: 18px;
}

.form-group label {
	display: block;
	margin-bottom: 8px;
	color: var(--sm-text);
	font-size: 14px;
	font-weight: 600;
}

.form-group label span {
	color: var(--sm-danger);
}

.form-group input,
.form-group select,
.form-group textarea {
	width: 100%;
	padding: 12px 13px;
	border: 1px solid var(--sm-border);
	border-radius: 11px;
	outline: none;
	color: var(--sm-text);
	background: #fffdfa;
}

.form-group textarea {
	resize: vertical;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
	border-color: #d8b992;
	box-shadow: 0 0 0 3px var(--sm-primary-soft);
}

.form-group .invalid {
	border-color: var(--sm-danger);
}

.error-text {
	display: block;
	color: var(--sm-danger);
	font-size: 12px;
}

.source-type-box {
	margin-bottom: 18px;
	display: grid;
	grid-template-columns: repeat(3, 1fr);
	gap: 13px;
}

.source-option {
	padding: 15px;
	border: 1px solid var(--sm-border);
	border-radius: 13px;
	cursor: pointer;
	background: #fffdfa;
	display: flex;
	align-items: center;
	gap: 12px;
}

.source-option.active {
	border-color: var(--sm-primary);
	background: var(--sm-primary-soft);
}

.source-option input {
	display: none;
}

.source-option i {
	color: var(--sm-primary);
	font-size: 24px;
}

.source-option strong {
	display: block;
	color: var(--sm-text);
	font-size: 14px;
}

.source-option small {
	color: var(--sm-text-soft);
	font-size: 12px;
}

.upload-area {
	position: relative;
	margin-bottom: 18px;
	padding: 22px;
	border: 2px dashed var(--sm-border-strong);
	border-radius: 14px;
	background: var(--sm-accent-soft);
	text-align: center;
}

.upload-area input {
	position: absolute;
	inset: 0;
	opacity: 0;
	cursor: pointer;
}

.upload-content i {
	color: var(--sm-primary);
	font-size: 33px;
}

.upload-content p {
	margin: 8px 0 4px;
	color: var(--sm-text);
	font-weight: 600;
}

.upload-content small,
.content-counter {
	color: var(--sm-text-soft);
	font-size: 12px;
}

.chunk-preview-box {
	margin-bottom: 23px;
	padding: 16px;
	border: 1px solid var(--sm-border-strong);
	border-radius: 13px;
	background: var(--sm-accent-soft);
}

.chunk-preview-header,
.detail-title {
	margin-bottom: 13px;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.chunk-preview-header h5,
.detail-title h5 {
	margin: 0;
	color: var(--sm-text);
	font-size: 15px;
	font-weight: 700;
}

.chunk-preview-header span,
.detail-title span {
	padding: 5px 10px;
	border-radius: 20px;
	color: var(--sm-primary-dark);
	background: var(--sm-primary-soft);
	font-size: 11px;
	font-weight: 700;
}

.chunk-preview-item {
	margin-bottom: 9px;
	padding: 11px;
	border-radius: 9px;
	background: #fffdfa;
}

.chunk-preview-item strong {
	color: var(--sm-primary-dark);
	font-size: 12px;
}

.chunk-preview-item p {
	margin: 5px 0 0;
	color: var(--sm-text-soft);
	font-size: 13px;
}

.more-chunks {
	color: var(--sm-text-soft);
}

.source-link-box,
.full-content {
	margin-bottom: 22px;
	padding: 17px;
	border-radius: 13px;
	background: var(--sm-accent-soft);
}

.source-link-box {
	color: var(--sm-primary-dark);
	display: flex;
	gap: 8px;
	word-break: break-all;
}

.full-content h5 {
	margin: 0 0 10px;
	color: var(--sm-text);
	font-weight: 700;
	font-size: 15px;
}

.full-content p {
	margin: 0;
	color: var(--sm-text-soft);
	line-height: 1.7;
	white-space: pre-wrap;
}

.chunk-detail-item {
	margin-bottom: 10px;
	padding: 13px;
	border: 1px solid var(--sm-border);
	border-radius: 11px;
	background: #fffdfa;
	display: flex;
	gap: 12px;
}

.chunk-number {
	width: 28px;
	height: 28px;
	flex-shrink: 0;
	border-radius: 50%;
	color: white;
	background: var(--sm-primary);
	display: flex;
	justify-content: center;
	align-items: center;
	font-size: 12px;
	font-weight: 700;
}

.chunk-detail-item p {
	margin: 3px 0 0;
	color: var(--sm-text-soft);
	font-size: 14px;
}

.modal-footer-custom,
.delete-actions {
	display: flex;
	justify-content: flex-end;
	gap: 11px;
}

.cancel-btn,
.save-btn,
.confirm-delete-btn {
	height: 45px;
	padding: 0 19px;
	border-radius: 11px;
	font-weight: 600;
}

.cancel-btn {
	border: 1px solid var(--sm-border);
	color: var(--sm-text);
	background: #fffdfa;
}

.save-btn {
	border: none;
	color: white;
	background: linear-gradient(135deg, var(--sm-primary), var(--sm-accent));
	display: flex;
	align-items: center;
	gap: 7px;
}

.save-btn:disabled,
.confirm-delete-btn:disabled {
	cursor: not-allowed;
	opacity: 0.7;
}

.button-spinner {
	width: 17px;
	height: 17px;
	border: 2px solid rgba(255, 255, 255, 0.45);
	border-top-color: white;
	border-radius: 50%;
	display: inline-block;
	animation: spin 0.7s linear infinite;
}

.delete-modal {
	width: 420px;
	max-width: 100%;
	padding: 31px;
	border: 1px solid var(--sm-border);
	border-radius: 20px;
	background: var(--sm-card);
	box-shadow: var(--sm-shadow-md);
	text-align: center;
}

.delete-icon {
	width: 62px;
	height: 62px;
	margin: 0 auto 18px;
	border-radius: 50%;
	color: var(--sm-danger);
	background: var(--sm-danger-bg);
	font-size: 27px;
	display: flex;
	justify-content: center;
	align-items: center;
}

.delete-modal h4 {
	color: var(--sm-text);
	font-weight: 700;
}

.delete-modal p {
	margin: 12px 0 25px;
	color: var(--sm-text-soft);
}

.confirm-delete-btn {
	border: none;
	color: white;
	background: var(--sm-danger);
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

@keyframes spin {
	to {
		transform: rotate(360deg);
	}
}

@media (max-width: 1200px) {
	.toolbar {
		flex-direction: column;
	}

	.filters {
		flex-wrap: wrap;
	}
}

@media (max-width: 768px) {

	.page-header,
	.filters,
	.document-heading {
		flex-direction: column;
		align-items: flex-start;
	}

	.filters,
	.search-box,
	.filters select {
		width: 100%;
	}

	.document-card {
		flex-direction: column;
	}

	.source-type-box {
		grid-template-columns: 1fr;
	}
}
</style>