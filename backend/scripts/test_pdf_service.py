import asyncio
from pathlib import Path

from fastapi import UploadFile

from app.services.pdf_service import PDFService


async def main():
    pdf_path = input("Enter PDF path: ").strip()

    path = Path(pdf_path)

    if not path.exists():
        print("❌ PDF file not found.")
        return

    pdf_service = PDFService()

    with open(path, "rb") as f:
        upload_file = UploadFile(
            file=f,
            filename=path.name
        )

        try:
            pages = await pdf_service.extract_pages(upload_file)

            print("\n" + "=" * 60)
            print("PDF Extraction Successful")
            print("=" * 60)

            print(f"Total Pages Extracted: {len(pages)}")
            total_chars = sum(len(p["text"]) for p in pages)
            print(f"Total Characters     : {total_chars}")

            print("\nPage-by-Page Summary:")
            for p in pages:
                print(f"  Page {p['page_number']}: {len(p['text'])} chars")

            print("\nFirst 1000 Characters of Page 1:\n")
            if pages:
                print(pages[0]["text"][:1000])

        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    asyncio.run(main())