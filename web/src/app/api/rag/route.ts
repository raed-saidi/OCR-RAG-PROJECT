import { NextRequest, NextResponse } from "next/server";
import { spawn } from "child_process";
import path from "path";
import fs from "fs";

export async function POST(req: NextRequest) {
  try {
    const { query } = await req.json();

    if (!query || !query.trim()) {
      return NextResponse.json(
        { success: false, error: "Query manquante ou vide" },
        { status: 400 }
      );
    }

    const projectRoot = path.resolve(process.cwd(), ".."); 
    const scriptPath = path.join(projectRoot, "src", "ocr", "call_rag.py");

    if (!fs.existsSync(scriptPath)) {
      return NextResponse.json(
        { success: false, error: `Script Python introuvable: ${scriptPath}` },
        { status: 500 }
      );
    }

    let pythonPath = path.join(projectRoot, ".venv", "Scripts", "python.exe");

    if (!fs.existsSync(pythonPath)) {
      console.warn("[WARN] Python dans .venv introuvable, utilisation du Python global");
      pythonPath = "python"; 
    }

    console.log("[INFO] Python utilisé:", pythonPath);
    console.log("[INFO] Script:", scriptPath);
    console.log("[INFO] Question:", query);

    const pythonProcess = spawn(pythonPath, [scriptPath, query], { cwd: projectRoot });

    let stdoutData = "";
    let stderrData = "";

    pythonProcess.stdout.on("data", (chunk) => {
      stdoutData += chunk.toString();
    });

    pythonProcess.stderr.on("data", (chunk) => {
      stderrData += chunk.toString();
    });

    await new Promise((resolve, reject) => {
      pythonProcess.on("close", (code) => {
        if (code === 0) resolve(code);
        else
          reject(
            new Error(
              `Python exited with code ${code}\nStderr: ${stderrData}\nStdout: ${stdoutData}`
            )
          );
      });
    });

    const data = JSON.parse(stdoutData);

    if (!data.success) {
      return NextResponse.json(
        { success: false, error: data.error || "Erreur inconnue du backend Python" },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      answer: data.answer,
      documents: data.documents,
    });

  } catch (err: any) {
    console.error("[API Error]:", err);
    return NextResponse.json(
      { success: false, error: err.message || "Erreur interne du serveur" },
      { status: 500 }
    );
  }
}
