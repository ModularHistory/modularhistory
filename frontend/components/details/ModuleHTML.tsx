import ModuleLink from "@/components/details/ModuleLink";
import HtmlParser from "@/components/HtmlParser";
import { Element } from "html-react-parser";
import { FC } from "react";

interface ModuleHTMLProps {
  html: string;
}

/**
 * This component first renders a HTML string using `dangerouslySetInnterHtml`,
 * then asynchronously parses the HTML to replace some DOM nodes with React elements.
 *
 * @param html - the HTML string to render; unsafe if not cleaned before rendering.
 */
const ModuleHTML: FC<ModuleHTMLProps> = ({ html }: ModuleHTMLProps) => {
  const htmlFilterFunc = (element: Element) => {
    if (element.name === "a") {
      const { href } = element.attribs;
      // Only format internal links.
      if (href?.startsWith("/")) {
        return true;
      }
    }
    return false;
  };
  return (
    <div data-testid={"moduleHTML"}>
      <HtmlParser html={html} filterFunc={htmlFilterFunc} component={ModuleLink} />
    </div>
  );
};

export default ModuleHTML;
