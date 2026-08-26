// Application constants and configuration.

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const ROUTES = {
  HOME: '/',
  SEARCH: '/search',
  CASE_DETAIL: '/cases/:caseId',
  UPLOAD: '/upload',
};

export const BREAKPOINTS = {
  MOBILE: 640,
  TABLET: 1024,
  DESKTOP: 1024,
};

export const PAGINATION = {
  PAGE_SIZE: 10,
  MAX_PAGE_SIZE: 100,
};
