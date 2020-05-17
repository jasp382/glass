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


def unsecure(pdfs, out_res):
    """
    Unsecure PDF's using qpdf

    Requirements: qpdf must be installed
    """

    import os
    from glass.pys  import execmd

    if os.path.isdir(pdfs):
        from glass.pys .oss import lst_ff

        pdfs = lst_ff(pdfs, file_format='.pdf')
    
    else:
        from glass.pys  import obj_to_lst

        pdfs = obj_to_lst(pdfs)
    
    for pdf in pdfs:
        execmd("qpdf --decrypt {} {}".format(pdf, os.path.join(
            out_res, os.path.basename(pdf)
        )))
    
    return out_res
