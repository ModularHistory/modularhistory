import SearchPage from "@/pages/search.page";
import { render } from "@testing-library/react";

describe("Search Page", () => {
  it("renders search form when no results are found", () => {
    const { getByTestId } = render(<SearchPage count={0} totalPages={0} results={[]} />);
    getByTestId("searchForm");
  });

  it("renders results", () => {});
});
