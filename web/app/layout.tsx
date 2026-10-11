import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "Consumo e estoque imobiliário",
  description: "Acompanhamento de vendas por empreendimento, bloco, prumada e andar.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
