# PDF Signer

PDF Signer is a small Streamlit app for placing a signature image onto a PDF, previewing the result, and downloading the signed document.

## Features

- Upload a PDF and a signature image.
- Automatically suggest a signature location when the word Signature is found.
- Manually adjust page, position, and signature size.
- Preview the signed PDF before downloading it.
- Generate a demo output from the bundled sample files.

## Project Layout

```
pdf-signer/
├── app.py
├── demo.py
├── requirements.txt
├── sample/
├── src/
│   ├── detector.py
│   └── pdf_signer.py
└── tests/
    └── test_pdf_signer.py
```

## Setup

1. Create and activate a virtual environment.
2. Install the dependencies:

```bash
pip install -r requirements.txt
```

## Run The App

```bash
streamlit run app.py
```

## Run The Demo

Use the bundled sample files to produce a final signed PDF:

```bash
python demo.py
```

The script writes the result to `output/signed_demo.pdf`.

## Run Tests

```bash
pytest
```

## Notes

- JPEG and PNG signature uploads are supported.
- If the automatic detector cannot find the word Signature, the app falls back to manual coordinates.
- The signature position is measured using the PDF page coordinate system, so you may still need to fine-tune placement for each document.

## Sample Assets

- `sample/sample.pdf` is the demo document.
- `sample/download.png` is the bundled signature image used by `demo.py`.
