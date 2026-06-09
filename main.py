from ingestion.sec_downloader import download_filings

print("=" * 50)
print("STARTING PIPELINE")
print("=" * 50)

download_filings()

print("=" * 50)
print("PIPELINE FINISHED")
print("=" * 50)