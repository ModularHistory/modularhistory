import ModuleDetail from "@/components/details/ModuleDetail";
import { GlobalTheme } from "@/pages/_app.page";
import { ModuleUnion } from "@/types/models";
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

const CloseButton = styled(IconButton)(({ theme }) => ({
  position: "absolute",
  right: theme.spacing(1),
  top: theme.spacing(1),
  color: theme.palette.grey[500],
}));

interface ModuleModalProps extends DialogProps {
  module: ModuleUnion | undefined;
  setOpen: Dispatch<SetStateAction<boolean>>;
}

const ModuleModal: FC<ModuleModalProps> = (props: ModuleModalProps) => {
  const { module, open, setOpen, ...dialogProps } = props;
  const close = () => setOpen(false);

  // modal is fullscreen when the viewport is small
  const fullScreen = useMediaQuery<GlobalTheme>((theme) => theme.breakpoints.down("sm"));

  return (
    <Dialog open={open} onClose={close} fullScreen={fullScreen} {...dialogProps}>
      <DialogTitle>
        {module?.title ?? <Skeleton width={"80%"} />}
        <CloseButton aria-label="close" onClick={close}>
          <CloseIcon />
        </CloseButton>
      </DialogTitle>
      <DialogContent dividers>
        {module ? (
          <ModuleDetail module={module} />
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
          href={`${module?.absoluteUrl}`}
          target={"_blank"}
          disabled={!module?.absoluteUrl}
        >
          Open in new tab
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ModuleModal;
