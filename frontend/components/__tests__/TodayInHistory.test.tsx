import TodayInHistory from "@/components/TodayInHistory";
import { Quote } from "@/types/modules";
import { render } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
// import { rest } from "msw";
// import { setupServer } from "msw/node";
import mockRouter from "next-router-mock";
import Router from "next/router";

describe("TodayInHistory", () => {
  const testModule: Quote = {
    id: 1,
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
    render(<TodayInHistory todayModules={[]} />);
  });

  describe("with content", () => {
    it("renders modules", async () => {
      const { findByText } = render(<TodayInHistory todayModules={[testModule]} />);
      expect(await findByText(testModule.title)).toBeInTheDocument();
    });

    it("has modules linked to details pages", async () => {
      mockRouter.setCurrentUrl("/");
      const { findByText } = render(<TodayInHistory todayModules={[testModule]} />);
      userEvent.click(await findByText(testModule.title));
      expect(Router.asPath).toStrictEqual(testModule.absoluteUrl);
    });
  });

  describe("without content", () => {
    it("shows 'no modules' message", async () => {
      const { findByText } = render(<TodayInHistory todayModules={[]} />);
      expect(
        await findByText("There are no modules associated with this date.")
      ).toBeInTheDocument();
    });
  });

  describe("module card clicked", () => {
    it("renders clicked module card", async () => {
      mockRouter.setCurrentUrl("/");
      const { findByText } = render(<TodayInHistory todayModules={[testModule]} />);
      userEvent.click(await findByText(testModule.title));
      expect(Router.asPath).toStrictEqual(testModule.absoluteUrl);
    });
  });
});
