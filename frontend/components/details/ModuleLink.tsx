import ModuleModal from "@/components/details/ModuleModal";
import { ModuleUnion } from "@/types/modules";
import { styled } from "@mui/material/styles";
import axios from "axios";
import Link from "next/link";
import { useRouter } from "next/router";
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
  anchorProps: AnchorHTMLAttributes<any> & { "data-id"?: string };
  anchorChildren: ReactNode;
}

/**
 * ModuleLink is used to style and add event listeners to links to module details.
 * Module data is fetched when ModuleLink is hovered/clicked, and a ModuleModal is
 * opened on click.
 *
 * @param anchorProps - attributes of the underlying anchor element.
 * @param anchorChildren - the text or react node inside the anchor element.
 * @constructor
 */
const ModuleLink: FC<ModuleLinkProps> = ({ anchorProps, anchorChildren }) => {
  const router = useRouter();
  const [modalOpen, setModalOpen] = useState(false);

  const [module, setModule] = useState<ModuleUnion>();
  const requestRef = useRef<Promise<any>>();
  const [isFailure, setIsFailure] = useState(false);

  // TODO: add "data-model" attribute to anchor tags in our database HTML.
  const model = anchorProps.href?.split("/").filter(Boolean)[0] || "";
  const id = anchorProps["data-id"];

  // under failure conditions, revert to rendering a normal anchor element
  if (!anchorProps.href || !allowedModels.has(model) || isFailure) {
    return <a {...anchorProps}>{anchorChildren}</a>;
  }

  const { target, ...anchorPropsWithoutTarget } = anchorProps;

  // if we are not on the search page, use Next link instead of ModuleModal
  if (router.pathname !== "/search") {
    return (
      <StyledSpan>
        <Link href={anchorProps.href}>
          <a {...anchorPropsWithoutTarget}>{anchorChildren}</a>
        </Link>
      </StyledSpan>
    );
  }

  const fetchModule = () => {
    // only send request if we have not already sent one
    if (!module && !requestRef.current) {
      requestRef.current = axios
        .get(`/api/${model}/${id}/`)
        .then(({ data }) => {
          setModule(data);
        })
        .catch((error) => {
          console.error(error);
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
        <a {...anchorPropsWithoutTarget} onClick={(event) => event.preventDefault()}>
          {anchorChildren}
        </a>
      </StyledSpan>
    </>
  );
};

export default ModuleLink;
