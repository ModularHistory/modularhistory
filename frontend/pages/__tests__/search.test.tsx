import SearchPage, { SearchProps } from "@/pages/search.page";
import type { Quote } from "@/types/models";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import { Partial } from "@react-spring/types";
import { render, screen } from "@testing-library/react";
import { mockAllIsIntersecting } from "react-intersection-observer/test-utils";

describe("Search Page", () => {
  function renderSearch(props?: Partial<SearchProps>) {
    const queries = render(
      <ThemeProvider theme={createTheme({})}>
        <SearchPage count={0} totalPages={0} results={[]} {...props} />
      </ThemeProvider>
    );
    mockAllIsIntersecting(true);
    return queries;
  }

  it("renders search form when no results are found", async () => {
    renderSearch();
    await expect(screen.findByTestId("searchForm")).resolves.toBeInTheDocument();
  });

  it("renders results", async () => {
    const testModule: Quote = {
      id: 1,
      verified: false,
      slug: "",
      title: "",
      model: "quotes.quote",
      adminUrl: "",
      absoluteUrl: "",
      attributeeHtml: "",
      attributeeString: "",
      bite: "",
      dateString: "",
      html: "",
      primaryImage: {} as any,
      cachedTags: [],
      cachedCitations: [],
    };
    renderSearch({ count: 1, totalPages: 1, results: [testModule] });
    await expect(screen.findByTestId("moduleCard")).resolves.toBeInTheDocument();
  });
});
