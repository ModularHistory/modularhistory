import ModuleModal from "@/components/details/ModuleModal";
import { ModuleUnion } from "@/types/modules";
import { Box } from "@material-ui/core";
import axios from "axios";
import { FC, MouseEventHandler, ReactElement, useState } from "react";

const allowedModels = new Set([
  "propositions",
  "entities",
  "images",
  "quotes",
  "sources",
  "topics",
]);

interface ModuleLinkProps {
  Anchor: (props: { onClick?: MouseEventHandler }) => ReactElement;
  model: string;
  id: string;
}

const ModuleLink: FC<ModuleLinkProps> = ({ Anchor, model, id }) => {
  const [modalOpen, setModalOpen] = useState(false);
  const [module, setModule] = useState<ModuleUnion>();
  const [isFailure, setIsFailure] = useState(false);

  if (!allowedModels.has(model) || isFailure) {
    return <Anchor />;
  }

  const handleClick: MouseEventHandler = (event) => {
    event.preventDefault();
    setModalOpen(true);
    axios
      .get(`/api/${model}/${id}/`)
      .then(({ data }) => {
        setModule(data);
      })
      .catch((error) => {
        console.error(error);
        setIsFailure(true);
      });
  };

  return (
    <Box
      component={"span"}
      sx={{
        lineHeight: "16px",
        padding: "1px 0.24em 2px",
        display: "inline",
        borderRadius: "3px",
        color: "rgb(0, 82, 204)",
        backgroundColor: "white",
        boxShadow: "rgb(9 30 66 / 25%) 0px 1px 1px, rgb(9 30 66 / 13%) 0px 0px 1px 1px",
        cursor: "pointer",
        userSelect: "text",
        transition: "all 0.1s ease-in-out 0s",
      }}
    >
      <ModuleModal module={module} setOpen={setModalOpen} open={modalOpen} />
      <Anchor onClick={handleClick} />
    </Box>
  );
};

export default ModuleLink;
