import Modal from "@material-ui/core/Modal";
import { makeStyles } from "@material-ui/styles";
import React, { FC, useState } from "react";

const useStyles = makeStyles({
  root: {},
});

interface IssueModalProps {
  open: boolean;
}

const IssueModal: FC<IssueModalProps> = ({ open }: IssueModalProps) => {
  const classes = useStyles();
  const [modalOpen, setModalOpen] = useState(open);
  const handleClose = () => {
    setModalOpen(false);
  };
  return (
    <Modal
      open={modalOpen}
      onClose={handleClose}
      aria-labelledby="simple-modal-title"
      aria-describedby="simple-modal-description"
    >
      <div className={classes.root}>
        <h2 id="simple-modal-title">Text in a modal</h2>
        <p id="simple-modal-description">
          Duis mollis, est non commodo luctus, nisi erat porttitor ligula.
        </p>
      </div>
    </Modal>
  );
};

export default IssueModal;
