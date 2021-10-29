import { Skeleton } from "@mui/material";
import { Viewer, Worker } from "@react-pdf-viewer/core";
import { defaultLayoutPlugin, ToolbarProps, ToolbarSlot } from "@react-pdf-viewer/default-layout";
import Head from "next/head";
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
        <div className="rpv-toolbar" role="toolbar" aria-orientation="horizontal">
          <div className="rpv-toolbar__left">
            <div className="rpv-toolbar__item">
              <ShowSearchPopover />
            </div>
            <div className="rpv-toolbar__item">
              <GoToPreviousPage />
            </div>
            <div className="rpv-toolbar__item">
              <CurrentPageInput /> / <NumberOfPages />
            </div>
            <div className="rpv-toolbar__item">
              <GoToNextPage />
            </div>
          </div>
          <div className="rpv-toolbar__center">
            <div className="rpv-toolbar__item">
              <ZoomOut />
            </div>
            <div className="rpv-toolbar__item">
              <Zoom />
            </div>
            <div className="rpv-toolbar__item">
              <ZoomIn />
            </div>
          </div>
          <div className="rpv-toolbar__right">
            <div className="rpv-toolbar__item">
              <EnterFullScreen />
            </div>
            <div className="rpv-toolbar__item">
              <Download />
            </div>
            <div className="rpv-toolbar__item">
              <Print />
            </div>
          </div>
        </div>
      );
    }}
  </Toolbar>
);

const Pdf: FC<PdfProps> = (props: PdfProps) => {
  const { url, initialPageNumber } = props;
  const defaultLayoutPluginInstance = defaultLayoutPlugin({
    // https://react-pdf-viewer.dev/examples/remove-a-tab-from-the-sidebar/
    sidebarTabs: (defaultTabs) => [
      // Remove the attachments tab (\`defaultTabs[2]\`)
      defaultTabs[0], // Bookmarks tab
      defaultTabs[1], // Thumbnails tab
    ],
    renderToolbar,
  });
  return (
    <div>
      <Head>
        <style></style>
      </Head>
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
