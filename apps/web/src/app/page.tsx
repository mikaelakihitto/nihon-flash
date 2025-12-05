import Link from "next/link";

export default function HomePage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 px-4">
      <div className="w-full max-w-3xl rounded-2xl bg-white p-10 shadow-xl">
        <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div className="space-y-2">
            <p className="text-sm uppercase tracking-[0.2em] text-indigo-600">SRS Japonês</p>
            <h1 className="text-3xl font-semibold text-slate-900">Nihon Flash</h1>
            <p className="text-slate-600">
              Fluxo inspirado no WaniKani para revisar Hiragana e Katakana via flashcards.
            </p>
          </div>
          <div className="flex flex-col gap-3 md:w-56">
            <Link
              href="/login"
              className="w-full rounded-lg bg-indigo-600 px-4 py-3 text-center text-white shadow hover:bg-indigo-700"
            >
              Ir para o login
            </Link>
            <Link
              href="/dashboard"
              className="w-full rounded-lg border border-slate-300 px-4 py-3 text-center text-slate-800 hover:bg-slate-100"
            >
              Ver dashboard (mock)
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
