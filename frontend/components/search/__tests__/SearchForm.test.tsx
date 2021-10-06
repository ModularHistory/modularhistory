import SearchForm from "@/components/search/SearchForm";
import { render, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import mockRouter from "next-router-mock";
import Router from "next/router";

describe("Search Form", () => {
  it("populates fields from router query", async () => {
    const query = "query";
    mockRouter.setCurrentUrl({
      pathname: "/",
      query: { query },
    });
    const { getByTestId } = await waitFor(() => render(<SearchForm />));
    // expect(getByTestId("queryField").textContent).toEqual("test")
    expect(getByTestId("queryField").querySelector("input")).toHaveValue(query);
  });

  it("excludes undefined fields from search parameters", async () => {
    const query = {
      query: "query",
      topics: ["1", "2", "3"],
    };
    mockRouter.setCurrentUrl({
      pathname: "/",
      query,
    });

    const { getByTestId } = await waitFor(() => render(<SearchForm />));

    userEvent.click(getByTestId("searchButton"));
    expect(Router).toMatchObject({ query });
  });
});
