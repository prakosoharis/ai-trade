import "./globals.css";
import Link from "next/link";

export const metadata = {
  title: "AI Institutional Market Research Workbench",
  description: "Pre-MVP institutional market research workbench"
};

export const viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  themeColor: "#070a0f"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <nav className="nav">
          <div className="container nav-inner">
            <Link href="/" className="brand">
              <div className="logo">↗</div>
              <div>
                <div className="brand-title">Deluwang</div>
                <div className="brand-subtitle">Institutional Market Research Workbench</div>
              </div>
            </Link>
            <div className="nav-links">
              <Link className="nav-link" href="/analysis">Analysis</Link>
              <Link className="nav-link" href="/history">History</Link>
              <Link className="nav-link" href="/intelligence">Intelligence</Link>
            </div>
          </div>
        </nav>
        {children}
      </body>
    </html>
  );
}
