for %%f in ("input_filepath\*") DO ("program_filepath\Tesseract-OCR\tesseract.exe" %%f "output_filepath\%%~nf" -l eng --psm  1 --oem 1 hocr)
