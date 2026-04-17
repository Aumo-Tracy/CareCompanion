import { writable } from 'svelte/store';

export const user     = writable(null);
export const token    = writable('');
export const alerts   = writable([]);
export const loading  = writable(false);
export const error    = writable('');

export function setUser(userData, userToken) {
  user.set(userData);
  token.set(userToken);
  localStorage.setItem('cc_token',    userToken);
  localStorage.setItem('cc_user',     JSON.stringify(userData));
}

export function clearUser() {
  user.set(null);
  token.set('');
  localStorage.removeItem('cc_token');
  localStorage.removeItem('cc_user');
}

export function loadStoredUser() {
  const storedToken = localStorage.getItem('cc_token');
  const storedUser  = localStorage.getItem('cc_user');
  if (storedToken && storedUser) {
    token.set(storedToken);
    user.set(JSON.parse(storedUser));
    return true;
  }
  return false;
}