import { Element, HTMLReactParserOptions } from "html-react-parser";
import { FC, ReactElement, useEffect, useState } from "react";

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
  const [renderedHTML, setRenderedHTML] = useState(() => (
    <div dangerouslySetInnerHTML={{ __html: html }} />
  ));

  useEffect(() => {
    // asynchronously load parsing and rendering modules to improve performance
    Promise.all([import("html-react-parser"), import("@/components/sources/PdfLink")]).then(
      ([{ default: parse, domToReact, attributesToProps }, { default: PdfLink }]) => {
        const options: HTMLReactParserOptions = {
          replace: (domNode) => {
            if (domNode.type !== "tag") {
              return;
            }

            // The cast here is necessary to get around a weird bug
            // when using this package with NextJS and TS.
            // remarkablemark/html-react-parser#221
            const element = domNode as Element;

            if (element.name === "a") {
              const { href } = element.attribs;

              // Only process links for hosted PDFs.
              if (!href?.includes(".pdf") || href?.includes("//")) {
                return;
              }

              return (
                <PdfLink
                  anchorProps={attributesToProps(element.attribs)}
                  anchorChildren={domToReact(element.children)}
                />
              );
            } else {
              // casting to prevent TS error; we can cast safely because domNode.type is
              // always "tag" here, so the rendered node will never be a string;
              return domToReact(element.children, options) as Exclude<
                ReturnType<typeof domToReact>,
                string
              >;
            }
          },
        };

        setRenderedHTML(parse(html, options) as ReactElement);
      }
    );
  }, [html]);

  return <div data-testid={"citation"}>{renderedHTML}</div>;
};

export default Citation;
