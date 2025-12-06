"use client";

import Link from "next/link";
import { useState } from "react";

export default function ProfilePage() {
  const [name, setName] = useState("Usuário Nihon Flash");
  const [email, setEmail] = useState("email@example.com");
  const [newCards, setNewCards] = useState(10);
  const [showRomaji, setShowRomaji] = useState(true);

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-8">
      <div className="mx-auto max-w-4xl space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-slate-900">Perfil & Preferências</h1>
            <p className="text-slate-600">Ajuste suas informações e preferências de estudo.</p>
          </div>
          <Link
            href="/dashboard"
            className="inline-flex items-center rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-800 hover:bg-slate-100"
          >
            Voltar ao dashboard
          </Link>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900">Dados pessoais</h2>
            <div className="mt-4 space-y-3">
              <div className="space-y-1">
                <label className="text-sm font-medium text-slate-700">Nome</label>
                <input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full rounded-lg border border-slate-200 px-3 py-2 focus:border-indigo-500 focus:outline-none"
                />
              </div>
              <div className="space-y-1">
                <label className="text-sm font-medium text-slate-700">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full rounded-lg border border-slate-200 px-3 py-2 focus:border-indigo-500 focus:outline-none"
                />
              </div>
              <button className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow hover:bg-indigo-700">
                Salvar (mock)
              </button>
            </div>
          </div>

          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900">Preferências de estudo</h2>
            <div className="mt-4 space-y-4">
              <div className="space-y-1">
                <label className="text-sm font-medium text-slate-700">Novos cards por dia</label>
                <input
                  type="number"
                  min={0}
                  max={50}
                  value={newCards}
                  onChange={(e) => setNewCards(Number(e.target.value))}
                  className="w-full rounded-lg border border-slate-200 px-3 py-2 focus:border-indigo-500 focus:outline-none"
                />
                <p className="text-xs text-slate-500">Defina quantos novos cards você quer ver por dia.</p>
              </div>
              <div className="flex items-center justify-between rounded-lg border border-slate-200 bg-slate-50 px-3 py-2">
                <div>
                  <p className="text-sm font-medium text-slate-800">Mostrar romaji</p>
                  <p className="text-xs text-slate-500">Ocultar romaji deixa o estudo mais desafiador.</p>
                </div>
                <input
                  type="checkbox"
                  checked={showRomaji}
                  onChange={(e) => setShowRomaji(e.target.checked)}
                  className="h-4 w-4 accent-indigo-600"
                />
              </div>
              <button className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-800 hover:bg-slate-100">
                Salvar preferências (mock)
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
