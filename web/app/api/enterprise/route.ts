import { NextRequest, NextResponse } from "next/server";

import { enterpriseData } from "@/lib/server-data";

export const runtime = "nodejs";

export async function GET(request: NextRequest) {
  try {
    return NextResponse.json(enterpriseData(request.nextUrl.searchParams));
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Não foi possível carregar o empreendimento." },
      { status: 400 },
    );
  }
}
