<template>
	<aside class="sidebar" :class="{ open: props.isOpen }">
		<!-- Brand -->
		<div class="brand">
			<div class="brand-icon">
				<i class="bi bi-mortarboard-fill"></i>
			</div>

			<div class="brand-content">
				<h5>StudyMate</h5>
				<p>AI Study Assistant</p>
			</div>

			<button class="close-sidebar-btn" @click="emit('close')">
				<i class="bi bi-x-lg"></i>
			</button>
		</div>

		<!-- Main Menu -->
		<nav class="menu">
			<p class="menu-title">TỔNG QUAN</p>

			<RouterLink to="/dashboard" class="menu-item" @click="emit('close')">
				<i class="bi bi-grid-1x2-fill"></i>
				<span>Dashboard</span>
			</RouterLink>

			<p class="menu-title">HỌC TẬP</p>

			<RouterLink to="/mon-hoc" class="menu-item" @click="emit('close')">
				<i class="bi bi-book-fill"></i>
				<span>Môn học</span>
			</RouterLink>

			<RouterLink to="/bai-tap" class="menu-item" @click="emit('close')">
				<i class="bi bi-check2-square"></i>
				<span>Bài tập</span>
			</RouterLink>

			<RouterLink to="/lich-thi" class="menu-item" @click="emit('close')">
				<i class="bi bi-calendar-event"></i>
				<span>Lịch thi</span>
			</RouterLink>

			<RouterLink to="/ke-hoach-on-tap" class="menu-item" @click="emit('close')">
				<i class="bi bi-calendar-check"></i>
				<span>Kế hoạch ôn tập</span>
			</RouterLink>

			<p class="menu-title">TRỢ LÝ AI</p>

			<RouterLink to="/tai-lieu" class="menu-item" @click="emit('close')">
				<i class="bi bi-file-earmark-text-fill"></i>
				<span>Tài liệu học tập</span>
			</RouterLink>

			<RouterLink to="/chatbot" class="menu-item" @click="emit('close')">
				<i class="bi bi-robot"></i>
				<span>Chatbot hỏi đáp</span>
			</RouterLink>

			<RouterLink to="/nhac-nho-email" class="menu-item" @click="emit('close')">
				<i class="bi bi-bell-fill"></i>
				<span>Nhắc nhở Email</span>
				<span v-if="pendingReminders > 0" class="menu-count">
					{{ pendingReminders > 9 ? '9+' : pendingReminders }}
				</span>
			</RouterLink>
		</nav>

		<!-- AI Notice -->
		<div class="ai-box">
			<div class="ai-box-icon">
				<i class="bi bi-stars"></i>
			</div>

			<div>
				<strong>StudyMate AI</strong>
				<p>{{ documentCount }} tài liệu sẵn sàng hỏi đáp</p>
			</div>
		</div>

		<!-- Student Info -->
		<div class="student-box">
			<div class="avatar">{{ userInitial }}</div>

			<div class="student-info">
				<p class="student-name">{{ shortUserName }}</p>
				<span>{{ currentUser.role }}</span>
			</div>

			<button class="logout-btn" title="Đăng xuất" @click="logout">
				<i class="bi bi-box-arrow-right"></i>
			</button>
		</div>
	</aside>
</template>

<script setup>
import { computed, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { authStore } from '../../stores/auth'

const props = defineProps({
	isOpen: {
		type: Boolean,
		default: false,
	},
})

const emit = defineEmits(['close'])
const router = useRouter()

/*
  Tạm để 0 cho đến khi nối API reminders và documents.
  Không đọc localStorage nữa.
*/
const pendingReminders = ref(0)
const documentCount = ref(0)

const currentUser = computed(() => {
	const user = authStore.state.user

	return {
		fullName: user?.full_name || 'Sinh viên',
		email: user?.email || '',
		role: user?.role || 'Sinh viên',
	}
})

const userInitial = computed(() => {
	const parts = currentUser.value.fullName.trim().split(' ')
	return parts[parts.length - 1].charAt(0).toUpperCase()
})

const shortUserName = computed(() => {
	const parts = currentUser.value.fullName.trim().split(' ')
	return parts.slice(-2).join(' ')
})

const logout = async () => {
	await authStore.logout()
	emit('close')
	router.push('/dang-nhap')
}
</script>

<style scoped>
.sidebar {
	position: fixed;
	top: 0;
	left: 0;
	z-index: 200;
	width: 265px;
	height: 100vh;
	padding: 20px 15px 17px;
	color: #e9dfd4;
	background:
		radial-gradient(circle at 14% 7%, rgba(217, 174, 118, 0.19), transparent 25%),
		linear-gradient(180deg, #332720 0%, #2d231e 100%);
	display: flex;
	flex-direction: column;
	overflow-y: auto;
}

.brand {
	position: relative;
	padding: 0 8px 21px;
	border-bottom: 1px solid rgba(242, 223, 199, 0.12);
	display: flex;
	align-items: center;
	gap: 12px;
}

.brand-icon {
	width: 46px;
	height: 46px;
	flex-shrink: 0;
	border-radius: 14px;
	color: #fffaf4;
	background: linear-gradient(140deg, #b9824c, #d9ae76);
	box-shadow: 0 10px 21px rgba(185, 130, 76, 0.28);
	font-size: 23px;
	display: flex;
	align-items: center;
	justify-content: center;
}

.brand-content h5 {
	margin: 0;
	color: #fffaf4;
	font-size: 19px;
	font-weight: 700;
}

.brand-content p {
	margin: 3px 0 0;
	color: #bfae9f;
	font-size: 12px;
}

.close-sidebar-btn {
	display: none;
}

.menu {
	flex: 1;
	padding-top: 15px;
}

.menu-title {
	margin: 18px 12px 9px;
	color: #a48e7b;
	font-size: 11px;
	font-weight: 700;
	letter-spacing: 1px;
}

.menu-title:first-child {
	margin-top: 4px;
}

.menu-item {
	position: relative;
	height: 47px;
	margin-bottom: 4px;
	padding: 0 13px;
	border-radius: 12px;
	color: #ddd0c3;
	text-decoration: none;
	font-size: 14px;
	font-weight: 500;
	display: flex;
	align-items: center;
	gap: 12px;
	transition: all 0.2s ease;
}

.menu-item i {
	width: 22px;
	color: #c8ac8c;
	font-size: 18px;
	text-align: center;
	transition: color 0.2s ease;
}

.menu-item:hover {
	color: #fffaf4;
	background: rgba(243, 230, 214, 0.09);
}

.menu-item:hover i {
	color: #ebca9c;
}

.menu-item.router-link-active {
	color: #fffaf4;
	background: linear-gradient(135deg, #ad7643, #c9955c);
	box-shadow: 0 9px 22px rgba(126, 78, 39, 0.34);
}

.menu-item.router-link-active i {
	color: #fffaf4;
}

.menu-count {
	margin-left: auto;
	min-width: 21px;
	height: 21px;
	padding: 0 6px;
	border-radius: 20px;
	color: #fffaf4;
	background: #b55a49;
	font-size: 11px;
	font-weight: 700;
	display: inline-flex;
	align-items: center;
	justify-content: center;
}

.ai-box {
	margin: 14px 0;
	padding: 13px;
	border: 1px solid rgba(217, 174, 118, 0.2);
	border-radius: 15px;
	background:
		linear-gradient(135deg, rgba(185, 130, 76, 0.17), rgba(217, 174, 118, 0.07));
	display: flex;
	align-items: center;
	gap: 10px;
}

.ai-box-icon {
	width: 39px;
	height: 39px;
	flex-shrink: 0;
	border-radius: 11px;
	color: #f3d8ad;
	background: rgba(217, 174, 118, 0.17);
	display: flex;
	align-items: center;
	justify-content: center;
}

.ai-box strong {
	display: block;
	color: #fffaf4;
	font-size: 13px;
}

.ai-box p {
	margin: 3px 0 0;
	color: #bfae9f;
	font-size: 11px;
}

.student-box {
	padding: 11px;
	border: 1px solid rgba(242, 223, 199, 0.08);
	border-radius: 14px;
	background: rgba(255, 250, 244, 0.06);
	display: flex;
	align-items: center;
	gap: 10px;
}

.avatar {
	width: 40px;
	height: 40px;
	flex-shrink: 0;
	border-radius: 12px;
	color: #83542f;
	background: #f1ddc4;
	font-weight: 700;
	display: flex;
	align-items: center;
	justify-content: center;
}

.student-info {
	min-width: 0;
	flex: 1;
}

.student-name {
	max-width: 112px;
	margin: 0 0 3px;
	overflow: hidden;
	color: #fffaf4;
	font-size: 13px;
	font-weight: 600;
	text-overflow: ellipsis;
	white-space: nowrap;
}

.student-info span {
	color: #ad9a8b;
	font-size: 11px;
}

.logout-btn {
	width: 35px;
	height: 35px;
	flex-shrink: 0;
	border: none;
	border-radius: 10px;
	color: #dbcbbb;
	background: rgba(255, 250, 244, 0.07);
	font-size: 17px;
}

.logout-btn:hover {
	color: #fffaf4;
	background: #b55a49;
}

@media (max-width: 900px) {
	.sidebar {
		transform: translateX(-100%);
		transition: transform 0.25s ease;
	}

	.sidebar.open {
		transform: translateX(0);
	}

	.close-sidebar-btn {
		width: 36px;
		height: 36px;
		margin-left: auto;
		border: none;
		border-radius: 10px;
		color: #e7d9ca;
		background: rgba(255, 250, 244, 0.08);
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.close-sidebar-btn:hover {
		color: #fffaf4;
		background: rgba(255, 250, 244, 0.14);
	}
}
</style>