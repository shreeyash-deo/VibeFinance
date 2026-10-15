import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'VibeFinance - Autonomous Multi-Agent Financial Intelligence',
  description: 'Explainable, Personalized Financial Intelligence for Indian Retail Investors (Nifty 50)',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#090d16] text-slate-100 min-h-screen antialiased selection:bg-blue-600 selection:text-white">
        {children}
      </body>
    </html>
  );
}

