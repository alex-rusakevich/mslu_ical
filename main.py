import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "mslu_ical:app", host="0.0.0.0", port=5000, reload=True, log_level="debug"
    )
