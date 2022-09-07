import DocumentModal from "@/components/sources/DocumentModal";
import { styled } from "@mui/material/styles";
import { AnchorHTMLAttributes, FC, MouseEventHandler, ReactNode, useState } from "react";

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

interface PdfLinkProps {
  elementProps: AnchorHTMLAttributes<unknown> & { "data-id"?: string };
  children: ReactNode | string;
}

/**
 * PdfLink is used to style and add event listeners to links to doc details.
 * Document data is fetched when PdfLink is hovered/clicked, and a DocumentModal is
 * opened on click.
 *
 * @param elementProps - attributes of the underlying anchor element.
 * @param children - the text or react node inside the anchor element.
 * @constructor
 */
const PdfLink: FC<PdfLinkProps> = ({ elementProps, children }) => {
  const docHref = elementProps.href || "";
  const [url, pageNumber] = docHref.split("#page=");
  const [modalOpen, setModalOpen] = useState(false);
  const title = elementProps.title;
  const { target, ...elementPropsWithoutTarget } = elementProps;

  const handleClick: MouseEventHandler = (event) => {
    event.preventDefault();
    setModalOpen(true);
  };

  return (
    <>
      <DocumentModal
        url={url}
        initialPageNumber={pageNumber}
        header={title}
        setOpen={setModalOpen}
        open={modalOpen}
      />
      <StyledSpan onClick={handleClick}>
        <a {...elementPropsWithoutTarget} onClick={(event) => event.preventDefault()}>
          {children}
        </a>
      </StyledSpan>
    </>
  );
};

export default PdfLink;
