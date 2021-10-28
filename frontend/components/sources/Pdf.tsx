import { Skeleton } from "@mui/material";
import { FC, useState } from "react";
import { pdfjs } from "react-pdf";
import { Document, Page } from "react-pdf/dist/esm/entry.webpack";

pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.js`;

export interface PdfProps {
  url: string | null;
  initialPageNumber: string | undefined;
}

const Pdf: FC<PdfProps> = (props: PdfProps) => {
  const { url, initialPageNumber } = props;
  const [pageNumber, setPageNumber] = useState(initialPageNumber ? parseInt(initialPageNumber) : 1);
  const [numPages, setNumPages] = useState<number | null>(null);

  interface onDocumentLoadSuccessProps {
    numPages: number;
  }
  function onDocumentLoadSuccess({ numPages }: onDocumentLoadSuccessProps) {
    setNumPages(numPages);
  }

  function changePage(offset: number) {
    setPageNumber((prevPageNumber) => prevPageNumber + offset);
  }

  function previousPage() {
    changePage(-1);
  }

  function nextPage() {
    changePage(1);
  }

  return (
    <div>
      {url ? (
        <div>
          <Document
            file={url}
            onLoadSuccess={onDocumentLoadSuccess}
            loading={<Skeleton width="100%" />}
          >
            <Page pageNumber={pageNumber} />
          </Document>
          {numPages && (
            <div>
              <p>
                Page {pageNumber} of {numPages}
              </p>
              <button type="button" disabled={pageNumber <= 1} onClick={previousPage}>
                Previous
              </button>
              <button type="button" disabled={pageNumber >= numPages} onClick={nextPage}>
                Next
              </button>
            </div>
          )}
        </div>
      ) : (
        <Skeleton
          variant={"rectangular"}
          sx={{ width: "inherit", minWidth: "50vw", height: "40vw" }}
        />
      )}
    </div>
  );
};

export default Pdf;
