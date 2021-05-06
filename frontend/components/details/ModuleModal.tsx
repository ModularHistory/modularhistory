import {
  Button,
  Dialog,
  DialogProps,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  makeStyles,
  useTheme,
  useMediaQuery,
} from "@material-ui/core";
import CloseIcon from "@material-ui/icons/Close";
import { FC, SetStateAction, Dispatch } from "react";
import ModuleDetail from "@/components/details/ModuleDetail";
import { ModuleUnion } from "@/interfaces";

const useStyles = makeStyles((theme) => ({
  root: {
    margin: 0,
    padding: theme.spacing(2),
  },
  closeButton: {
    position: "absolute",
    right: theme.spacing(1),
    top: theme.spacing(1),
    color: theme.palette.grey[500],
  },
}));

interface ModuleModalProps extends DialogProps {
  module: ModuleUnion;
  setOpen: Dispatch<SetStateAction<boolean>>;
}

const ModuleModal: FC<ModuleModalProps> = (props: ModuleModalProps) => {
  const { module, open, setOpen, ...dialogProps } = props;
  const classes = useStyles();
  const close = () => setOpen(false);

  // modal is fullscreen when the viewport is small
  const theme = useTheme();
  const fullScreen = useMediaQuery(theme.breakpoints.down("xs"));

  // TODO: add logic for selecting title based on module type
  const title = module["title"] || module["name"] || "";

  return (
    <Dialog open={open} onClose={close} fullScreen={fullScreen} {...dialogProps}>
      <DialogTitle>
        {title}
        <IconButton aria-label="close" className={classes.closeButton} onClick={close}>
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      <DialogContent dividers>
        <ModuleDetail module={module} />
      </DialogContent>
      <DialogActions>
        <Button color="primary" component={"a"} href={`/${module.absoluteUrl}`} target={"_blank"}>
          Open in new tab
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ModuleModal;
