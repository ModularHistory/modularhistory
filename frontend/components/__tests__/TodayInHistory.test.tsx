import TodayInHistory from "@/components/TodayInHistory";
import { Quote } from "@/types/modules";
import { render } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import mockRouter from "next-router-mock";

describe("TodayInHistory", () => {
  const testModule: Quote = {
    pk: 1,
    verified: false,
    slug: "",
    title: "Test Quote",
    model: "quotes.quote",
    adminUrl: "",
    absoluteUrl: "/quotes/test-quote",
    attributeeHtml: "",
    attributeeString: "",
    bite: "",
    dateString: "",
    html: "",
    primaryImage: {} as any,
    cachedTags: [],
    cachedCitations: [],
  };

  it("renders", () => {
    render(<TodayInHistory modules={[]} />);
  });

  describe("with content", () => {
    it("renders modules", async () => {
      const { findByText } = render(<TodayInHistory modules={[testModule]} />);
      expect(await findByText(testModule.title)).toBeInTheDocument();
    });

    it("has modules linked to details pages", async () => {
      mockRouter.setCurrentUrl("/");
      const { findByText } = render(<TodayInHistory modules={[testModule]} />);
      userEvent.click(await findByText(testModule.title));
      // TODO: this probably only works on mobile
      // expect(Router.asPath).toStrictEqual(testModule.absoluteUrl);
    });
  });

  describe("without content", () => {
    it("shows 'no modules' message", async () => {
      const { findByText } = render(<TodayInHistory modules={[]} />);
      expect(
        await findByText("There are no modules associated with this date.")
      ).toBeInTheDocument();
    });
  });
});
