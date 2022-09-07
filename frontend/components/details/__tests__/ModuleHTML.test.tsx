import ModuleHTML from "@/components/details/ModuleHTML";
import { createTheme, ThemeProvider, useTheme } from "@mui/material/styles";
import { render, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import mockRouter from "next-router-mock";
import Router from "next/router";
import { FC } from "react";
import ReactDOMServer from "react-dom/server";

describe("ModuleHTML", () => {
  const normalLinkTestId = "normal";
  const moduleLinkTestId = "moduleLink";
  const normalLink = <a href={"example.com"} data-testid={normalLinkTestId} />;
  const moduleLink = (
    <a href={"/entities/666"} data-id={"666"} data-testid={moduleLinkTestId}>
      Lucy
    </a>
  );
  const twoLinksNode = (
    <div>
      {normalLink}
      {moduleLink}
    </div>
  );

  const doubleRender = async ({
    node = twoLinksNode,
    options = {},
  }: {
    node?: Parameters<typeof render>[0];
    options?: Parameters<typeof render>[1];
  } = {}) => ({
    moduleHTML: within(
      await waitFor(
        () =>
          render(
            <ThemeProvider theme={createTheme({})}>
              <ModuleHTML html={ReactDOMServer.renderToStaticMarkup(node)} />
            </ThemeProvider>,
            options
          ).container
      )
    ),
    normal: within(render(node).container),
  });

  it("renders normal HTML", async () => {
    const node = (
      <div data-testid={"root"}>
        text content<a href={"/"}>an anchor</a>
        <span>
          nested<a>text</a>
        </span>
      </div>
    );
    const { moduleHTML, normal } = await doubleRender({ node });
    expect(moduleHTML.getByTestId("root")).toStrictEqual(normal.getByTestId("root"));
  });

  it("only replaces module links", async () => {
    const { moduleHTML, normal } = await doubleRender();
    // normal html has same parent for both links
    expect(normal.getByTestId(moduleLinkTestId).parentElement).toBe(
      normal.getByTestId(normalLinkTestId).parentElement
    );
    // but module html has different parent for each link
    expect(moduleHTML.getByTestId(moduleLinkTestId).parentElement).not.toBe(
      moduleHTML.getByTestId(normalLinkTestId).parentElement
    );
  });

  it("does not use next/link when on search page", async () => {
    const Wrapper: FC<unknown> = (props) => <ThemeProvider theme={useTheme()} {...props} />;
    mockRouter.setCurrentUrl("/search");
    const { moduleHTML } = await doubleRender({
      options: {
        wrapper: Wrapper,
      },
    });

    userEvent.click(moduleHTML.getByTestId(moduleLinkTestId));
    expect(moduleLink.props.href).not.toStrictEqual(Router.asPath);
  });
});
