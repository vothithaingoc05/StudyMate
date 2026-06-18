import { reactive } from 'vue'
import api from '../services/api'

const state = reactive({
  user: null,
  initialized: false,
  loading: false,
})

const loadCurrentUser = async () => {
  state.loading = true

  try {
    const response = await api.get('/auth/me')
    state.user = response.data
  } catch (error) {
    state.user = null
  } finally {
    state.initialized = true
    state.loading = false
  }
}

const setUser = (user) => {
  state.user = user
  state.initialized = true
}

const logout = async () => {
  try {
    await api.post('/auth/logout')
  } finally {
    state.user = null
    state.initialized = true
  }
}

export const authStore = {
  state,
  loadCurrentUser,
  setUser,
  logout,
}