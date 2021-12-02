import { render } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import mockRouter from "next-router-mock";
import Router from "next/router";
import React from "react";
import Home from "../index.page";

describe("Home", () => {
  it("renders without exceptions", () => {
    render(<Home todayInHistoryModules={[]} featuredModules={[]} />);
  });

  describe("Search form", () => {
    beforeEach(() => {
      mockRouter.setCurrentUrl("/");
    });

    it("can search without input", () => {
      const { queryByTestId } = render(<Home todayInHistoryModules={[]} featuredModules={[]} />);
      const searchButton = queryByTestId("searchButton");
      userEvent.click(searchButton!);
      expect(Router).toMatchObject({
        pathname: "/search/",
        query: { query: "" },
      });
    });

    it("can search with input", () => {
      const { queryByTestId } = render(<Home todayInHistoryModules={[]} featuredModules={[]} />);
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
