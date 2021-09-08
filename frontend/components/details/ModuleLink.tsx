import ModuleModal from "@/components/details/ModuleModal";
import { ModuleUnion } from "@/types/modules";
import { styled } from "@material-ui/core/styles";
import axios from "axios";
import Link from "next/link";
import { useRouter } from "next/router";
import {
  AnchorHTMLAttributes,
  FC,
  ForwardRefExoticComponent,
  MouseEventHandler,
  RefAttributes,
  useRef,
  useState,
} from "react";

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
  Anchor: ForwardRefExoticComponent<RefAttributes<HTMLAnchorElement> & AnchorHTMLAttributes<any>>;
  anchorProps: AnchorHTMLAttributes<any> & { "data-id"?: string };
}

/**
 * ModuleLink is used to style and add event listeners to links to module details.
 * Module data is fetched when ModuleLink is hovered/clicked, and a ModuleModal is
 * opened on click.
 *
 * @param Anchor - a function component that renders the underlying anchor element,
 *                 including its props and children.
 * @param anchorProps - attributes of the underlying anchor element.
 * @constructor
 */
const ModuleLink: FC<ModuleLinkProps> = ({ Anchor, anchorProps }) => {
  const router = useRouter();
  const [modalOpen, setModalOpen] = useState(false);

  const [module, setModule] = useState<ModuleUnion>();
  const requestRef = useRef<Promise<any>>();
  const [isFailure, setIsFailure] = useState(false);

  const model = anchorProps.href?.split("/").filter(Boolean)[0] || "";
  const id = anchorProps["data-id"];

  if (!anchorProps.href || !allowedModels.has(model) || isFailure) {
    return <Anchor {...anchorProps} />;
  }

  const { target, ...anchorPropsWithoutTarget } = anchorProps;

  if (router.pathname !== "/search") {
    return (
      <StyledSpan>
        <Link href={anchorProps.href} passHref={true}>
          <Anchor {...anchorPropsWithoutTarget} />
        </Link>
      </StyledSpan>
    );
  }

  const fetchModule = () => {
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
        <Anchor onClick={(event) => event.preventDefault()} />
      </StyledSpan>
    </>
  );
};
export default ModuleLink;
