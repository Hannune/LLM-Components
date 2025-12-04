import os
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from gpt_researcher import GPTResearcher
import uvicorn


# Directory to store session files
SESSION_FILES_DIR = Path("session-files")
SESSION_FILES_DIR.mkdir(exist_ok=True)

# Session cleanup configuration
SESSION_MAX_AGE_HOURS = 24  # Remove sessions older than 24 hours


async def cleanup_old_sessions():
    """Remove session directories older than SESSION_MAX_AGE_HOURS"""
    if not SESSION_FILES_DIR.exists():
        return

    cutoff_time = datetime.now() - timedelta(hours=SESSION_MAX_AGE_HOURS)

    for session_dir in SESSION_FILES_DIR.iterdir():
        if session_dir.is_dir():
            # Check directory modification time
            dir_mtime = datetime.fromtimestamp(session_dir.stat().st_mtime)
            if dir_mtime < cutoff_time:
                try:
                    shutil.rmtree(session_dir)
                    print(f"Cleaned up old session: {session_dir.name}")
                except Exception as e:
                    print(f"Error cleaning up session {session_dir.name}: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: cleanup old sessions
    await cleanup_old_sessions()
    yield
    # Shutdown: nothing to do


app = FastAPI(
    title="GPT Researcher Wrapper",
    description="FastAPI wrapper for GPT Researcher with file upload support",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "GPT Researcher Wrapper",
        "version": "1.0.0"
    }


@app.post("/research")
async def research(
    background_tasks: BackgroundTasks,
    session_id: str = Form(...),
    query: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    report_type: str = Form("research_report"),
    tone: str = Form("Objective")
):
    """
    Perform research using GPT Researcher

    Args:
        session_id: Unique identifier for the research session
        query: Research query/question
        files: Optional list of files to upload for context
        report_type: Type of report (research_report, outline_report, etc.)
        tone: Tone of the report (Objective, Formal, Analytical, etc.)

    Returns:
        JSON response with research results
    """
    try:
        # Create session directory
        session_dir = SESSION_FILES_DIR / session_id
        session_dir.mkdir(exist_ok=True)

        # Save uploaded files if any
        uploaded_files = []
        if files:
            for file in files:
                if file.filename:
                    file_path = session_dir / file.filename
                    with open(file_path, "wb") as f:
                        content = await file.read()
                        f.write(content)
                    uploaded_files.append(str(file_path))

        # Set the local file path for gpt-researcher
        os.environ["DOC_PATH"] = str(session_dir)

        # Initialize GPT Researcher
        researcher = GPTResearcher(
            query=query,
            report_type=report_type,
            tone=tone
        )

        # Conduct research
        await researcher.conduct_research()

        # Generate report
        report = await researcher.write_report()

        # Schedule cleanup of this session in background
        background_tasks.add_task(schedule_session_cleanup, session_id)

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "session_id": session_id,
                "query": query,
                "report": report,
                "uploaded_files": uploaded_files,
                "report_type": report_type,
                "tone": tone
            }
        )

    except Exception as e:
        # Clean up session directory on error
        if session_dir.exists():
            shutil.rmtree(session_dir)

        raise HTTPException(
            status_code=500,
            detail=f"Research failed: {str(e)}"
        )


async def schedule_session_cleanup(session_id: str, delay_hours: int = 1):
    """
    Schedule cleanup of a session directory after a delay

    Args:
        session_id: Session ID to clean up
        delay_hours: Hours to wait before cleanup (default: 1 hour)
    """
    import asyncio
    await asyncio.sleep(delay_hours * 3600)

    session_dir = SESSION_FILES_DIR / session_id
    if session_dir.exists():
        try:
            shutil.rmtree(session_dir)
            print(f"Cleaned up session: {session_id}")
        except Exception as e:
            print(f"Error cleaning up session {session_id}: {e}")


@app.post("/cleanup")
async def manual_cleanup():
    """Manually trigger cleanup of old sessions"""
    await cleanup_old_sessions()
    return {"status": "ok", "message": "Cleanup completed"}


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """
    Manually delete a specific session

    Args:
        session_id: Session ID to delete
    """
    session_dir = SESSION_FILES_DIR / session_id

    if not session_dir.exists():
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        shutil.rmtree(session_dir)
        return {"status": "ok", "message": f"Session {session_id} deleted"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete session: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
