import SearchPage from "@/pages/search.page";
import type { Quote } from "@/types/modules";
import { render, waitFor } from "@testing-library/react";

describe("Search Page", () => {
  it("renders search form when no results are found", async () => {
    const { getByTestId } = await waitFor(() =>
      render(<SearchPage count={0} totalPages={0} results={[]} />)
    );
    getByTestId("searchForm");
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
    await waitFor(() => render(<SearchPage count={1} totalPages={1} results={[testModule]} />));
  });
});
