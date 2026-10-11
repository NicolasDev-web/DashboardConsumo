import { NextResponse } from "next/server";

import { velocityData } from "@/lib/server-data";

export const runtime = "nodejs";

export async function GET() {
  try {
    return NextResponse.json(velocityData());
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Não foi possível carregar a velocidade." },
      { status: 500 },
    );
  }
}
