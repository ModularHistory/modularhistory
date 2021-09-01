import { HTMLReactParserOptions } from "html-react-parser";
import { Element } from "html-react-parser/node_modules/domhandler/lib/node";
import { FC, ReactElement, useEffect, useState } from "react";

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
        // const  = module;
        const options: HTMLReactParserOptions = {
          // eslint-disable-next-line react/display-name
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

              return (
                <ModuleLink
                  Anchor={({ onClick }) => (
                    <a {...attributesToProps(element.attribs)} onClick={onClick}>
                      {domToReact(element.children)}
                    </a>
                  )}
                  // example href: "/entities/thomas-aquinas/"
                  model={href.split("/").filter(Boolean)[0]}
                  id={element.attribs["data-id"]}
                />
              );
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
