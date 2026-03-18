from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AnalysisNotFoundError(Exception):
    def __init__(self, job_id: str):
        self.job_id = job_id


class AnalysisNotReadyError(Exception):
    def __init__(self, job_id: str, stage: str):
        self.job_id = job_id
        self.stage = stage


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(AnalysisNotFoundError)
    async def analysis_not_found_handler(
        request: Request, exc: AnalysisNotFoundError
    ):
        return JSONResponse(
            status_code=404,
            content={"detail": f"Analysis {exc.job_id} not found"},
        )

    @app.exception_handler(AnalysisNotReadyError)
    async def analysis_not_ready_handler(
        request: Request, exc: AnalysisNotReadyError
    ):
        return JSONResponse(
            status_code=202,
            content={
                "detail": f"Analysis {exc.job_id} is still in progress",
                "stage": exc.stage,
            },
        )
