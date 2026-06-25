import { createRouter, createWebHistory } from 'vue-router'
import StudentLayout from '../layouts/StudentLayout.vue'
import { authStore } from '../stores/auth'

const routes = [
	{
		path: '/dang-nhap',
		name: 'login',
		component: () => import('../views/LoginView.vue'),
		meta: { guestOnly: true },
	},
	{
		path: '/dang-ky',
		name: 'register',
		component: () => import('../views/RegisterView.vue'),
		meta: { guestOnly: true },
	},
	{
		path: '/kiem-tra-email',
		name: 'check-email',
		component: () => import('../views/CheckEmailView.vue'),
	},
	{
		path: '/xac-thuc-email',
		name: 'verify-email',
		component: () => import('../views/VerifyEmailView.vue'),
	},
	
	{
		path: '/',
		component: StudentLayout,
		redirect: '/dashboard',
		meta: { requiresAuth: true },
		children: [
			{
				path: 'dashboard',
				name: 'dashboard',
				component: () => import('../views/DashboardView.vue'),
			},
			{
				path: 'mon-hoc',
				name: 'subjects',
				component: () => import('../views/SubjectsView.vue'),
			},
			{
				path: 'bai-tap',
				name: 'tasks',
				component: () => import('../views/TasksView.vue'),
			},
			{
				path: 'lich-thi',
				name: 'exams',
				component: () => import('../views/ExamsView.vue'),
			},
			{
				path: 'ke-hoach-on-tap',
				name: 'study-plan',
				component: () => import('../views/StudyPlanView.vue'),
			},
			{
				path: 'tai-lieu',
				name: 'documents',
				component: () => import('../views/DocumentsView.vue'),
			},
			{
				path: 'chatbot',
				name: 'chatbot',
				component: () => import('../views/ChatbotView.vue'),
			},
			{
				path: 'nhac-nho-email',
				name: 'email-reminder',
				component: () => import('../views/EmailReminderView.vue'),
			},
		],
	},
	{
		path: '/:pathMatch(.*)*',
		redirect: '/dashboard',
	},
]

const router = createRouter({
	history: createWebHistory(),
	routes,
})

router.beforeEach(async (to) => {
	if (!authStore.state.initialized) {
		await authStore.loadCurrentUser()
	}

	const isAuthenticated = Boolean(authStore.state.user)
	const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)
	const guestOnly = to.matched.some((record) => record.meta.guestOnly)

	if (requiresAuth && !isAuthenticated) {
		return '/dang-nhap'
	}

	if (guestOnly && isAuthenticated) {
		return '/dashboard'
	}

	return true
})

export default router