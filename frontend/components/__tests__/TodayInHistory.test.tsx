import TodayInHistory from "@/components/TodayInHistory";
import { Quote } from "@/types/modules";
import { render } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { rest } from "msw";
import { setupServer } from "msw/node";
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
    render(<TodayInHistory />);
  });

  it("starts in loading state", () => {
    const { queryByText } = render(<TodayInHistory />);
    expect(queryByText("Fetching content")).toBeInTheDocument();
  });

  describe("with content", () => {
    const serverWithContent = setupServer(
      rest.get("/api/home/today_in_history/", (req, res, ctx) => {
        return res(ctx.json([testModule]));
      })
    );

    beforeAll(() => {
      serverWithContent.listen();
    });

    afterAll(() => {
      serverWithContent.close();
    });

    it("renders modules", async () => {
      const { findByText } = render(<TodayInHistory />);
      expect(await findByText(testModule.title)).toBeInTheDocument();
    });

    it("has modules linked to details pages", async () => {
      mockRouter.setCurrentUrl("/");
      const { findByText } = render(<TodayInHistory />);
      userEvent.click(await findByText(testModule.title));
      expect(Router.asPath).toStrictEqual(testModule.absoluteUrl);
    });
  });

  describe("without content", () => {
    const serverWithoutContent = setupServer(
      rest.get("/api/home/today_in_history/", (req, res, ctx) => {
        return res(ctx.json([]));
      })
    );

    beforeAll(() => {
      serverWithoutContent.listen();
    });

    afterAll(() => {
      serverWithoutContent.close();
    });

    it("shows 'no modules' message", async () => {
      const { findByText } = render(<TodayInHistory />);
      expect(
        await findByText("There are no modules associated with this date.")
      ).toBeInTheDocument();
    });
  });

  describe("with error response", () => {
    const serverWithError = setupServer(
      rest.get("/api/home/today_in_history/", (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ errorMessage: "test error" }));
      })
    );

    beforeAll(() => {
      serverWithError.listen();
    });

    afterAll(() => {
      serverWithError.close();
    });

    it("shows 'no modules' message", async () => {
      const { findByText } = render(<TodayInHistory />);
      expect(
        await findByText("There are no modules associated with this date.")
      ).toBeInTheDocument();
    });
  });
});
