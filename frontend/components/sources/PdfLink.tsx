import DocumentModal from "@/components/sources/DocumentModal";
import { styled } from "@mui/material/styles";
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

interface PdfLinkProps {
  anchorProps: AnchorHTMLAttributes<any> & { "data-id"?: string };
  anchorChildren: ReactNode;
}

/**
 * PdfLink is used to style and add event listeners to links to doc details.
 * Document data is fetched when PdfLink is hovered/clicked, and a DocumentModal is
 * opened on click.
 *
 * @param anchorProps - attributes of the underlying anchor element.
 * @param anchorChildren - the text or react node inside the anchor element.
 * @constructor
 */
const PdfLink: FC<PdfLinkProps> = ({ anchorProps, anchorChildren }) => {
  const docHref = anchorProps.href || "";
  const [url, pageNumber] = docHref.split("#page=");
  const [modalOpen, setModalOpen] = useState(false);
  const requestRef = useRef<Promise<any>>();
  const [isFailure, setIsFailure] = useState(false);

  // Under failure conditions, revert to rendering a normal anchor element.
  if (!anchorProps.href || isFailure) {
    return <a {...anchorProps}>{anchorChildren}</a>;
  }

  const title = anchorProps.title;
  const { target, ...anchorPropsWithoutTarget } = anchorProps;

  const fetchDocument = () => {
    // Only send request if we have not already sent one.
    // if (!url && !requestRef.current) {
    //   requestRef.current = axios
    //     .get(docHref)
    //     .then(() => {
    //       setDocUrl(docHref);
    //     })
    //     .catch((error) => {
    //       console.error(error);
    //       setIsFailure(true);
    //     });
    // }
  };

  const handleClick: MouseEventHandler = (event) => {
    event.preventDefault();
    setModalOpen(true);
    fetchDocument();
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
      <StyledSpan onMouseEnter={fetchDocument} onClick={handleClick}>
        <a {...anchorPropsWithoutTarget} onClick={(event) => event.preventDefault()}>
          {anchorChildren}
        </a>
      </StyledSpan>
    </>
  );
};

export default PdfLink;
