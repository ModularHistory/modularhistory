import ModuleDetail from "@/components/details/ModuleDetail";
import { ModuleUnion } from "@/types/modules";
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogProps,
  DialogTitle,
  IconButton,
  useMediaQuery,
  useTheme,
} from "@material-ui/core";
import { styled } from "@material-ui/core/styles";
import CloseIcon from "@material-ui/icons/Close";
import { Dispatch, FC, SetStateAction } from "react";

const CloseButton = styled(IconButton)(({ theme }) => ({
  position: "absolute",
  right: theme.spacing(1),
  top: theme.spacing(1),
  color: theme.palette.grey[500],
}));

interface ModuleModalProps extends DialogProps {
  module: ModuleUnion;
  setOpen: Dispatch<SetStateAction<boolean>>;
}

const ModuleModal: FC<ModuleModalProps> = (props: ModuleModalProps) => {
  const { module, open, setOpen, ...dialogProps } = props;
  const close = () => setOpen(false);

  // modal is fullscreen when the viewport is small
  const theme = useTheme();
  const fullScreen = useMediaQuery(theme.breakpoints.down("xs"));

  // TODO: add logic for selecting title based on module type
  const title = module["title"];

  return (
    <Dialog open={open} onClose={close} fullScreen={fullScreen} {...dialogProps}>
      <DialogTitle>
        {title}
        <CloseButton aria-label="close" onClick={close}>
          <CloseIcon />
        </CloseButton>
      </DialogTitle>
      <DialogContent dividers>
        <ModuleDetail module={module} />
      </DialogContent>
      <DialogActions>
        <Button component={"a"} href={`${module.absoluteUrl}`} target={"_blank"}>
          Open in new tab
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ModuleModal;
