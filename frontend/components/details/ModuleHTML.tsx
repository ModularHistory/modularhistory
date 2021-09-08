import { HTMLReactParserOptions } from "html-react-parser";
import { Element } from "html-react-parser/node_modules/domhandler/lib/node";
import { FC, ForwardedRef, forwardRef, ReactElement, useEffect, useState } from "react";

interface ModuleHTMLProps {
  html: string;
}

const ModuleHTML: FC<ModuleHTMLProps> = ({ html }: ModuleHTMLProps) => {
  const [renderedHTML, setRenderedHTML] = useState(() => (
    <div dangerouslySetInnerHTML={{ __html: html }} />
  ));

  useEffect(() => {
    Promise.all([import("html-react-parser"), import("@/components/details/ModuleLink")]).then(
      ([{ default: parse, domToReact, attributesToProps }, { default: ModuleLink }]) => {
        const options: HTMLReactParserOptions = {
          replace: (domNode) => {
            if (domNode.type !== "tag") {
              return;
            }
            const element = domNode as Element;
            if (element.name == "a") {
              const { href } = element.attribs;
              if (!(href.startsWith("/") || href.includes("modularhistory.com/"))) {
                return;
              }

              const anchorProps = attributesToProps(element.attribs);
              const Anchor = forwardRef(function Anchor(
                props,
                ref: ForwardedRef<HTMLAnchorElement>
              ) {
                return (
                  <a {...props} ref={ref}>
                    {domToReact(element.children)}
                  </a>
                );
              });
              return <ModuleLink Anchor={Anchor} anchorProps={anchorProps} />;
            } else {
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

  return renderedHTML;
};

export default ModuleHTML;
