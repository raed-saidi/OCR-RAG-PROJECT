import "./globals.css";
import AppProviders from "../providers/ChakraProvider";

export const metadata = {
  title: "OCR RAG Demo",
  description: "Interface RAG + OCR",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
