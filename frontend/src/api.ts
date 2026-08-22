const BASE_URL: string =
  (import.meta as any).env?.VITE_API_URL ?? "http://127.0.0.1:8000";

export interface Profile {
  id: number;
  display_name: string;
  email: string;
  avatar: string | null;
}

export function resolveAvatarUrl(avatarPath: string | null | undefined): string | null {
  if (!avatarPath) return null;

  const lower = avatarPath.toLowerCase();
  if (
    lower.includes("random.jpg") ||
    lower.includes("placeholder") ||
    lower.includes("default.png") ||
    lower.includes("default.jpg") ||
    lower.includes("default.webp")
  ) {
    return null;
  }

  if (avatarPath.startsWith("http://") || avatarPath.startsWith("https://")) {
    return avatarPath;
  }
  const cleanBase = BASE_URL.replace(/\/+$/, "");
  const cleanPath = avatarPath.startsWith("/") ? avatarPath : `/${avatarPath}`;
  return `${cleanBase}${cleanPath}`;
}



export interface TokenResponse {
  token: string;
}

export class ApiError extends Error {
  status: number;
  body: unknown;

  constructor(status: number, message: string, body: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

function getToken(): string | null {
  return localStorage.getItem("auth_token");
}

export function setToken(token: string): void {
  localStorage.setItem("auth_token", token);
}

export function clearToken(): void {
  localStorage.removeItem("auth_token");
}

export function isAuthenticated(): boolean {
  return getToken() !== null;
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {};

  if (token) {
    headers["Authorization"] = `Token ${token}`;
  }

  if (
    options.body &&
    typeof options.body === "string"
  ) {
    headers["Content-Type"] = "application/json";
  }

  const mergedHeaders: Record<string, string> = {
    ...headers,
    ...(options.headers as Record<string, string> | undefined),
  };

  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: mergedHeaders,
  });

  if (res.status === 401) {
    clearToken();
    throw new ApiError(401, "Unauthorized", null);
  }

  if (!res.ok) {
    let body: unknown;
    try {
      body = await res.json();
    } catch {
      body = null;
    }
    throw new ApiError(res.status, `Request failed: ${res.status}`, body);
  }

  if (res.status === 204) {
    return undefined as T;
  }

  return res.json();
}

export async function login(
  username: string,
  password: string
): Promise<TokenResponse> {
  return request<TokenResponse>("/api/token/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
}

export interface RegisterResponse {
  token: string;
  display_name: string;
  email: string;
}

export async function register(
  username: string,
  email: string,
  password: string,
  display_name?: string
): Promise<RegisterResponse> {
  return request<RegisterResponse>("/api/profile/register/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email, password, display_name }),
  });
}

export async function getProfile(): Promise<Profile> {
  return request<Profile>("/api/profile/me/", { method: "GET" });
}

export async function updateProfile(
  display_name: string
): Promise<Profile> {
  return request<Profile>("/api/profile/me/", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ display_name }),
  });
}

export async function uploadAvatar(
  file: File
): Promise<Profile> {
  const formData = new FormData();
  formData.append("avatar", file);

  return request<Profile>("/api/profile/avatar/", {
    method: "POST",
    body: formData,
  });
}

export function validateAvatarFile(file: File): string | null {
  const allowedTypes = ["image/jpeg", "image/png", "image/webp"];
  if (!allowedTypes.includes(file.type)) {
    return "Only JPEG, PNG, or WEBP files are allowed.";
  }
  if (file.size > 5 * 1024 * 1024) {
    return "File is too large. Maximum size is 5MB.";
  }
  return null;
}

