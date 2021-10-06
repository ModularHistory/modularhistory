import { render } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import mockRouter from "next-router-mock";
import Router from "next/router";
import React from "react";
import Home from "../index.page";

describe("Home", () => {
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
