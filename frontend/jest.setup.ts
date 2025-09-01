import '@testing-library/jest-dom';

// Mock import.meta for tests
(globalThis as typeof globalThis & { importMeta: { env: Record<string, string> } }).importMeta = {
  env: {
    VITE_API_BASE_URL: 'http://localhost:8000'
  }
};

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock ResizeObserver
(globalThis as typeof globalThis & { ResizeObserver: jest.Mock }).ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
})); 