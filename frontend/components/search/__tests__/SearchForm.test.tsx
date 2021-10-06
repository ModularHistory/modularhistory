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
      quality: "verified",
    };

    mockRouter.setCurrentUrl({
      pathname: "/",
      query,
    });

    const { getByTestId } = await waitFor(() => render(<SearchForm />));

    const queryInput = getByTestId("queryField").querySelector("input");
    expect(queryInput).not.toBeNull();
    userEvent.type(queryInput!, "query");
    userEvent.click(getByTestId("searchButton"));
    expect(Router.query).toEqual({ ...query, query: "query" });
  });
});
