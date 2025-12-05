"use client";

import { FormEvent, useState } from "react";
import { apiFetch, getApiBaseUrl } from "../../../lib/api";

type LoginResponse = { access_token: string; token_type: string };

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [result, setResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const data = await apiFetch<LoginResponse>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password })
      });
      setResult(`Token: ${data.access_token}`);
    } catch (err: any) {
      setResult(err?.message ?? "Erro ao autenticar");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="space-y-4 max-w-md">
      <div>
        <h2 className="text-2xl font-semibold">Login</h2>
        <p className="text-slate-700">API: {getApiBaseUrl()}</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="space-y-1">
          <label className="block text-sm font-medium text-slate-700">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded border border-slate-300 px-3 py-2"
            required
          />
        </div>
        <div className="space-y-1">
          <label className="block text-sm font-medium text-slate-700">Senha</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded border border-slate-300 px-3 py-2"
            required
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="rounded bg-indigo-600 px-4 py-2 text-white disabled:opacity-60"
        >
          {loading ? "Autenticando..." : "Entrar"}
        </button>
      </form>

      {result && (
        <div className="rounded border border-slate-200 bg-white p-3 text-sm text-slate-800">
          {result}
        </div>
      )}
    </section>
  );
}
