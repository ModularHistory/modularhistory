import { Element, HTMLReactParserOptions } from "html-react-parser";
import { FC, ReactElement, useEffect, useState } from "react";

// Compare this snippet from frontend/components/details/ModuleLink.tsx:
interface HtmlParserProps {
  html: string;
  filterFunc: CallableFunction;
  component: FC<any>;
}

/**
 * This component first renders a HTML string using `dangerouslySetInnerHtml`,
 * then asynchronously parses the HTML to replace some DOM nodes with React elements.
 *
 * @param html - the HTML string to render; unsafe if not cleaned before rendering.
 * @param filterFunc - a function that takes a DOM element as a param and returns a boolean
 * indicating whether the element should be replaced with the designated React component.
 * @param component - the React component.
 */
const HtmlParser: FC<HtmlParserProps> = ({
  html,
  filterFunc,
  component: Component,
}: HtmlParserProps) => {
  const [renderedHTML, setRenderedHTML] = useState(() => (
    <div dangerouslySetInnerHTML={{ __html: html }} />
  ));
  useEffect(() => {
    // Load the parsing module asynchronously to improve performance.
    Promise.all([import("html-react-parser")]).then(
      ([{ default: parse, domToReact, attributesToProps }]) => {
        const options: HTMLReactParserOptions = {
          replace: (domNode) => {
            if (domNode.type !== "tag") {
              return;
            }
            // The cast here is necessary to get around a weird bug
            // when using this package with NextJS and TS.
            // remarkablemark/html-react-parser#221
            const element = domNode as Element;
            if (filterFunc(element)) {
              return (
                <Component elementProps={attributesToProps(element.attribs)}>
                  {domToReact(element.children)}
                </Component>
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
  }, [html, Component, filterFunc]);

  return <div>{renderedHTML}</div>;
};

export default HtmlParser;
