import { Skeleton } from "@mui/material";
import { Viewer, Worker } from "@react-pdf-viewer/core";
import { defaultLayoutPlugin } from "@react-pdf-viewer/default-layout";
import { FC } from "react";

// pdfJsVersion must match the version of pdfjs-dist specified in frontend/package.json
const pdfJsVersion = "2.10.377";
const workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfJsVersion}/pdf.worker.js`;

export interface PdfProps {
  url: string | null;
  initialPageNumber: string | undefined;
}

const Pdf: FC<PdfProps> = (props: PdfProps) => {
  const { url, initialPageNumber } = props;
  const defaultLayoutPluginInstance = defaultLayoutPlugin();
  return (
    <div>
      {url ? (
        <Worker workerUrl={workerSrc}>
          <div>
            <Viewer
              fileUrl={url}
              initialPage={parseInt(initialPageNumber || "1")}
              plugins={[defaultLayoutPluginInstance]}
            />
          </div>
        </Worker>
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
