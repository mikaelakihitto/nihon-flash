"use client";

const STORAGE_KEY = "nf_mock_auth";

export function mockLogin() {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEY, "true");
}

export function mockLogout() {
  if (typeof window === "undefined") return;
  localStorage.removeItem(STORAGE_KEY);
}

export function isLoggedIn(): boolean {
  if (typeof window === "undefined") return false;
  return localStorage.getItem(STORAGE_KEY) === "true";
}

export function useAuthGuard(router: { replace: (path: string) => void }) {
  const ready = typeof window !== "undefined";
  if (ready && !isLoggedIn()) {
    router.replace("/login");
  }
  return { ready };
}
