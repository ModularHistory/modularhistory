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
import { Dispatch, FC, SetStateAction } from "react";
import Pdf from "./Pdf";

const CloseButton = styled(IconButton)(({ theme }) => ({
  position: "absolute",
  right: theme.spacing(1),
  top: theme.spacing(1),
  color: theme.palette.grey[500],
}));

interface DocumentModalProps extends DialogProps {
  url: string | null;
  initialPageNumber: string | undefined;
  header?: string | undefined;
  setOpen: Dispatch<SetStateAction<boolean>>;
}

const DocumentModal: FC<DocumentModalProps> = (props: DocumentModalProps) => {
  const { url, initialPageNumber, header, open, setOpen, ...dialogProps } = props;
  const close = () => setOpen(false);
  // modal is fullscreen when the viewport is small
  const fullScreen = useMediaQuery<GlobalTheme>((theme) => theme.breakpoints.down("sm"));
  return (
    <Dialog
      open={open}
      onClose={close}
      maxWidth="lg"
      fullWidth={true}
      fullScreen={fullScreen}
      {...dialogProps}
    >
      <DialogTitle>
        {header ?? (url ? url.replace("/media/sources/", "") : undefined) ?? (
          <Skeleton width={"80%"} />
        )}
        <CloseButton aria-label="close" onClick={close}>
          <CloseIcon />
        </CloseButton>
      </DialogTitle>
      <DialogContent dividers style={{ padding: "0 1px 1px" }}>
        {url ? (
          <Pdf url={url} initialPageNumber={initialPageNumber} />
        ) : (
          <Skeleton
            variant={"rectangular"}
            sx={{ width: "inherit", minWidth: "50vw", height: "40vw" }}
          />
        )}
      </DialogContent>
      <DialogActions>
        <Button component={"a"} href={`${url}`} target={"_blank"} disabled={!url}>
          Open in new tab
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DocumentModal;
