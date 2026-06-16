from sec_edgar_downloader import Downloader


def download_filings(ticker, limit=1):
    print(f"Downloading {ticker} filings...")
    dl = Downloader(
        "Praveen Kumar",
        "praveen.b@mycvhire.com",
        "data/raw"
    )
    dl.get(
        "10-K",
        ticker,
        limit=limit
    )
    print(f"Download complete for {ticker}")


if __name__ == "__main__":
    import sys
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    download_filings(ticker, limit=1)