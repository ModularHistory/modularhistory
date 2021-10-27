import { render } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { rest } from "msw";
import { setupServer } from "msw/node";
import mockRouter from "next-router-mock";
import Router from "next/router";
import React from "react";
import Home from "../index.page";

const server = setupServer(
  rest.get("/api/home/today_in_history/", (req, res, ctx) => res(ctx.json([])))
);

describe("Home", () => {
  beforeAll(() => server.listen());
  afterAll(() => server.close());

  it("renders without exceptions", () => {
    render(<Home />);
  });

  describe("Search form", () => {
    beforeEach(() => {
      mockRouter.setCurrentUrl("/");
    });

    it("can search without input", () => {
      const { queryByTestId } = render(<Home />);
      const searchButton = queryByTestId("searchButton");
      userEvent.click(searchButton!);
      expect(Router).toMatchObject({
        pathname: "/search/",
        query: { query: "" },
      });
    });

    it("can search with input", () => {
      const { queryByTestId } = render(<Home />);
      const searchInput = queryByTestId("query");
      const queryString = "jest is best";
      userEvent.type(searchInput!, queryString + "{enter}");
      expect(Router).toMatchObject({
        pathname: "/search/",
        query: { query: queryString },
      });
    });
  });
});
