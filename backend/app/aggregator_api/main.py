"""FastAPI application entry point for the Sezonski Rad aggregator."""

import logging
from fastapi import FastAPI
from .api import router as aggregator_router
from .database import init_db, SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sezonski.main")

app = FastAPI(
    title="Sezonski rad Srbija — Aggregator API",
    description="Source-agnostic seasonal work lead aggregator, runtime agent, and intake layer.",
    version="0.2.1",
)

# Core aggregator API (004B)
app.include_router(aggregator_router)

# Runtime agent API (005A)
try:
    from ..runtime_agent.api import router as runtime_router
    app.include_router(runtime_router)
except ImportError:
    pass

# Runtime intake API (005B)
try:
    from ..runtime_intake.manual_paste_api import router as intake_router
    app.include_router(intake_router)
except ImportError:
    pass

# Account worker API (005C)
try:
    from ..account_worker.worker_api import router as worker_router
    app.include_router(worker_router)
except ImportError:
    pass


@app.on_event("startup")
def on_startup():
    init_db()

    # Start Telegram approval bot if configured
    try:
        from ..runtime_agent.agent_core import RuntimeAgent
        from ..telegram_bot.bot import start_bot, set_runtime_agent

        db = SessionLocal()
        agent = RuntimeAgent(db)
        set_runtime_agent(agent)
        app.state.runtime_agent = agent

        bot = start_bot()
        if bot:
            app.state.telegram_bot = bot
            logger.info("Telegram bot started in polling mode")
        else:
            logger.info("Telegram bot not started (token/chat_id not configured)")
    except Exception as e:
        logger.warning(f"Telegram bot init skipped: {e}")


@app.on_event("shutdown")
def on_shutdown():
    try:
        from ..telegram_bot.bot import stop_bot
        stop_bot()
    except ImportError:
        pass


if __name__ == "__main__":
    import uvicorn
    init_db()
    uvicorn.run(app, host="0.0.0.0", port=8000)
