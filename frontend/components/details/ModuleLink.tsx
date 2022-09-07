import ModuleModal from "@/components/details/ModuleModal";
import { ModuleUnion } from "@/types/modules";
import { styled } from "@mui/material/styles";
import axios from "axios";
import { AnchorHTMLAttributes, FC, MouseEventHandler, ReactNode, useRef, useState } from "react";

const StyledSpan = styled("span")({
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
});

const allowedModels = new Set([
  "propositions",
  "entities",
  "images",
  "quotes",
  "sources",
  "topics",
]);

interface ModuleLinkProps {
  elementProps: AnchorHTMLAttributes<unknown> & { "data-id"?: string };
  children: ReactNode | string;
}

/**
 * ModuleLink is used to style and add event listeners to links to module details.
 * Module data is fetched when ModuleLink is hovered/clicked, and a ModuleModal is
 * opened on click.
 *
 * @param elementProps - attributes of the underlying anchor element.
 * @param children - the text or react node inside the anchor element.
 * @constructor
 */
const ModuleLink: FC<ModuleLinkProps> = ({ elementProps, children }) => {
  const [modalOpen, setModalOpen] = useState(false);

  const [module, setModule] = useState<ModuleUnion>();
  const requestRef = useRef<Promise<unknown>>();
  const [isFailure, setIsFailure] = useState(false);

  // TODO: add "data-model" attribute to anchor tags in our database HTML.
  const model = elementProps.href?.split("/").filter(Boolean)[0] || "";
  const id = elementProps["data-id"];

  // Under failure conditions, revert to rendering a normal anchor element.
  if (!elementProps.href || !allowedModels.has(model) || isFailure) {
    return <a {...elementProps}>{children}</a>;
  }

  const { target, ...elementPropsWithoutTarget } = elementProps;

  const fetchModule = () => {
    // only send request if we have not already sent one
    if (!module && !requestRef.current) {
      requestRef.current = axios
        .get(`/api/${model}/${id}/`)
        .then(({ data }) => {
          setModule(data);
        })
        .catch((error) => {
          alert(error); // TODO
          setIsFailure(true);
        });
    }
  };

  const handleClick: MouseEventHandler = (event) => {
    event.preventDefault();
    setModalOpen(true);
    fetchModule();
  };

  return (
    <>
      <ModuleModal module={module} setOpen={setModalOpen} open={modalOpen} />
      <StyledSpan onMouseEnter={fetchModule} onClick={handleClick}>
        <a {...elementPropsWithoutTarget} onClick={(event) => event.preventDefault()}>
          {children}
        </a>
      </StyledSpan>
    </>
  );
};

export default ModuleLink;
