import "./globals.css";
import type { ReactNode } from "react";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Nihon Flash",
  description: "SRS para Hiragana, Katakana, Kanji e gramatica."
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <main className="min-h-screen px-6 py-10">
          {children}
        </main>
      </body>
    </html>
  );
}
