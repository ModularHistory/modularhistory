import HtmlParser from "@/components/HtmlParser";
import PdfLink from "@/components/sources/PdfLink";
import { Element } from "html-react-parser";
import { FC } from "react";

interface CitationProps {
  html: string;
}

/**
 * This component first renders a HTML string using `dangerouslySetInnerHtml`,
 * then asynchronously parses the HTML to replace some DOM nodes with React elements.
 *
 * @param html - the HTML string to render; unsafe if not cleaned before rendering.
 */
const Citation: FC<CitationProps> = ({ html }: CitationProps) => {
  const htmlFilterFunc = (element: Element) => {
    if (element.name === "a") {
      const { href } = element.attribs;
      // Only process links for hosted PDFs.
      if (href?.includes(".pdf") && !href?.includes("//")) {
        return true;
      }
    }
    return false;
  };
  return (
    <div data-testid={"citation"}>
      <HtmlParser html={html} filterFunc={htmlFilterFunc} component={PdfLink} />
    </div>
  );
};

export default Citation;
