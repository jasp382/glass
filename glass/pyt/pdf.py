"""
Tools for PDF
"""

def merge_pdf(inputPdf, outPdf):
    """
    Merge several PDF's in the same file
    """
    
    from PyPDF2 import PdfFileWriter, PdfFileReader
    
    pdf_writer = PdfFileWriter()
    
    for _pdf in inputPdf:
        pdf_reader = PdfFileReader(_pdf)
        for page in range(pdf_reader.getNumPages()):
            pdf_writer.addPage(pdf_reader.getPage(page))
    
    with open(outPdf, 'wb') as fh:
        pdf_writer.write(fh)
    
    return outPdf

