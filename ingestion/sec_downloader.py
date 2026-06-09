from sec_edgar_downloader import Downloader


def download_filings():

    print("Downloading Apple filings...")

    dl = Downloader(
        "Praveen Kumar",
        "praveenkumarbotta999@gmail.com",
        "data/raw"
    )

    dl.get(
        "10-K",
        "AAPL",
        limit=2
    )

    print("Download complete")


if __name__ == "__main__":
    download_filings()