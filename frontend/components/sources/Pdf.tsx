import { Skeleton } from "@mui/material";
import { Viewer, Worker } from "@react-pdf-viewer/core";
import { defaultLayoutPlugin, ToolbarProps, ToolbarSlot } from "@react-pdf-viewer/default-layout";
import { FC, ReactElement } from "react";

// pdfJsVersion must match the version of pdfjs-dist specified in frontend/package.json
const pdfJsVersion = "2.10.377";
const workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfJsVersion}/pdf.worker.js`;

export interface PdfProps {
  url: string | null;
  initialPageNumber: string | undefined;
}

const renderToolbar = (Toolbar: (props: ToolbarProps) => ReactElement) => (
  <Toolbar>
    {(slots: ToolbarSlot) => {
      const {
        CurrentPageInput,
        Download,
        EnterFullScreen,
        GoToNextPage,
        GoToPreviousPage,
        NumberOfPages,
        Print,
        ShowSearchPopover,
        Zoom,
        ZoomIn,
        ZoomOut,
      } = slots;
      return (
        <div
          style={{
            alignItems: "center",
            display: "flex",
          }}
        >
          <div style={{ padding: "0px 2px" }}>
            <ShowSearchPopover />
          </div>
          <div style={{ padding: "0px 2px" }}>
            <ZoomOut />
          </div>
          <div style={{ padding: "0px 2px" }}>
            <Zoom />
          </div>
          <div style={{ padding: "0px 2px" }}>
            <ZoomIn />
          </div>
          <div style={{ padding: "0px 2px", marginLeft: "auto" }}>
            <GoToPreviousPage />
          </div>
          <div style={{ padding: "0px 2px" }}>
            <CurrentPageInput /> / <NumberOfPages />
          </div>
          <div style={{ padding: "0px 2px" }}>
            <GoToNextPage />
          </div>
          <div style={{ padding: "0px 2px", marginLeft: "auto" }}>
            <EnterFullScreen />
          </div>
          <div style={{ padding: "0px 2px" }}>
            <Download />
          </div>
          <div style={{ padding: "0px 2px" }}>
            <Print />
          </div>
        </div>
      );
    }}
  </Toolbar>
);

const Pdf: FC<PdfProps> = (props: PdfProps) => {
  const { url, initialPageNumber } = props;
  const defaultLayoutPluginInstance = defaultLayoutPlugin({
    sidebarTabs: (defaultTabs) => [
      // Remove the attachments tab (\`defaultTabs[2]\`)
      defaultTabs[0], // Bookmarks tab
      defaultTabs[1], // Thumbnails tab
    ],
    renderToolbar,
  });
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
