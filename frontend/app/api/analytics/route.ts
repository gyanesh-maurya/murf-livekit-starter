import { exec } from "child_process";
import { promisify } from "util";
import path from "path";
import { NextResponse } from "next/server";

const execAsync = promisify(exec);

export async function GET() {
  try {
    const backendPath = path.resolve(process.cwd(), "..", "backend");
    const { stdout } = await execAsync(
      `uv run python -c "from db import get_analytics_summary; import json; print(json.dumps(get_analytics_summary()))"`,
      { cwd: backendPath }
    );
    const data = JSON.parse(stdout.trim());
    return NextResponse.json(data);
  } catch (error: any) {
    return NextResponse.json(
      {
        total_calls: 0,
        successful_calls: 0,
        failed_calls: 0,
        success_rate: 0,
        recent_calls: [],
        error: error?.message || "Failed to fetch analytics",
      },
      { status: 200 }
    );
  }
}
