import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { getProfile } from '../services/api';

interface AuthState {
  isLoggedIn: boolean;
  loading: boolean;
}

const initialState: AuthState = {
  isLoggedIn: false,
  loading: true,
};

export const checkAuth = createAsyncThunk('auth/checkAuth', async () => {
  const data = await getProfile();
  return data.user_id ? true : false;
});

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setLoggedIn: (state, action) => {
      state.isLoggedIn = action.payload;
    },
    logout: (state) => {
      state.isLoggedIn = false;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(checkAuth.pending, (state) => {
        state.loading = true;
      })
      .addCase(checkAuth.fulfilled, (state, action) => {
        state.isLoggedIn = action.payload;
        state.loading = false;
      })
      .addCase(checkAuth.rejected, (state) => {
        state.isLoggedIn = false;
        state.loading = false;
      });
  },
});

export const { setLoggedIn, logout } = authSlice.actions;
export default authSlice.reducer;