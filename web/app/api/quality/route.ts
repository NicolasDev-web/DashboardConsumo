import { NextRequest, NextResponse } from "next/server";

import { qualityRows } from "@/lib/server-data";

export const runtime = "nodejs";

export async function GET(request: NextRequest) {
  try {
    return NextResponse.json(qualityRows(request.nextUrl.searchParams));
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Não foi possível carregar os alertas." },
      { status: 500 },
    );
  }
}
