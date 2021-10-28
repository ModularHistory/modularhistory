import { GlobalTheme } from "@/pages/_app.page";
import CloseIcon from "@mui/icons-material/Close";
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogProps,
  DialogTitle,
  IconButton,
  Skeleton,
  styled,
  useMediaQuery,
} from "@mui/material";
import { Dispatch, FC, SetStateAction, useState } from "react";
import { Document, Page } from "react-pdf/dist/esm/entry.webpack";

const CloseButton = styled(IconButton)(({ theme }) => ({
  position: "absolute",
  right: theme.spacing(1),
  top: theme.spacing(1),
  color: theme.palette.grey[500],
}));

interface DocumentModalProps extends DialogProps {
  url: string | null;
  initialPageNumber: string | undefined;
  setOpen: Dispatch<SetStateAction<boolean>>;
}

const DocumentModal: FC<DocumentModalProps> = (props: DocumentModalProps) => {
  const { url, initialPageNumber, open, setOpen, ...dialogProps } = props;
  const close = () => setOpen(false);
  const [pageNumber, setPageNumber] = useState(initialPageNumber ? parseInt(initialPageNumber) : 1);
  const [numPages, setNumPages] = useState(null);

  // modal is fullscreen when the viewport is small
  const fullScreen = useMediaQuery<GlobalTheme>((theme) => theme.breakpoints.down("sm"));

  function onDocumentLoadSuccess({ numPages }) {
    setNumPages(numPages);
  }

  return (
    <Dialog open={open} onClose={close} fullScreen={fullScreen} {...dialogProps}>
      <DialogTitle>
        {url ?? <Skeleton width={"80%"} />}
        <CloseButton aria-label="close" onClick={close}>
          <CloseIcon />
        </CloseButton>
      </DialogTitle>
      <DialogContent dividers>
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
              <p>
                Page {pageNumber} of {numPages}
              </p>
            )}
          </div>
        ) : (
          <Skeleton
            variant={"rectangular"}
            sx={{ width: "inherit", minWidth: "50vw", height: "40vw" }}
          />
        )}
      </DialogContent>
      <DialogActions>
        <Button
          component={"a"}
          // href={`${url}`}
          target={"_blank"}
          disabled={!url}
        >
          Open in new tab
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DocumentModal;
