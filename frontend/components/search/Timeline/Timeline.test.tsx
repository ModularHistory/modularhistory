import { act, render, screen, waitFor } from "@testing-library/react";
import { createRef } from "react";
import Timeline, { TimelineProps } from "./Timeline";

describe("Timeline", () => {
  const markTestId = "timelineModuleMark";
  const breakTestId = "timelineBreakMark";
  const tooltipTestId = "timelineTooltip";

  let consoleMock: jest.SpyInstance;
  beforeEach(() => {
    consoleMock = jest.spyOn(console, "error");
  });
  afterEach(() => {
    expect(consoleMock).toHaveBeenCalledTimes(0);
  });

  function renderTimeline(props?: Partial<TimelineProps>) {
    return render(<Timeline modules={[]} viewStateRegistry={new Map()} {...props} />);
  }

  function createModules(n: number, multiplier = 1): Required<TimelineProps["modules"][number]>[] {
    return [...Array(n)].map((_, i) => ({
      timelinePosition: i * multiplier,
      title: `title${i}`,
      absoluteUrl: `/url/${i}/`,
      ref: createRef(),
    }));
  }

  function getMarkPosition<T extends HTMLElement>(mark: T) {
    return Number(mark.style.bottom.replace("%", ""));
  }

  it("renders with no modules", () => {
    renderTimeline();
  });

  it("renders with one module", async () => {
    renderTimeline({ modules: createModules(1) });
    await expect(screen.findAllByTestId(markTestId)).rejects.toThrowError();
  });

  it("renders with two modules", async () => {
    renderTimeline({ modules: createModules(2) });
    await expect(screen.findAllByTestId(markTestId)).resolves.toHaveLength(2);
  });

  it("renders with un-positioned modules", async () => {
    renderTimeline({
      modules: createModules(2).map(({ timelinePosition, ...rest }) => ({ ...rest })),
    });
    await expect(screen.findAllByTestId(markTestId)).rejects.toThrowError();
  });

  it("adds break to large gap", async () => {
    const modules = createModules(4);
    modules.slice(2).forEach((m) => (m.timelinePosition += 100));
    renderTimeline({ modules });
    const marks = await screen.findAllByTestId(markTestId);
    const breaks = await screen.findAllByTestId(breakTestId);
    expect(breaks).toHaveLength(1);

    // style.bottom determines the offset along the rail
    const positioned = [...marks, ...breaks]
      .map((e) => ({
        dataset: e.dataset,
        position: getMarkPosition(e),
      }))
      .sort((a, b) => a.position - b.position);

    // expect the middle positioned element to be the break
    expect(positioned[2].dataset.testid).toBe(breakTestId);
  });

  it("registers tooltip state dispatch", async () => {
    const modules = createModules(2);
    const viewStateRegistry: TimelineProps["viewStateRegistry"] = new Map();
    renderTimeline({ modules, viewStateRegistry });
    await waitFor(() => {
      expect(viewStateRegistry.size).toBe(2);
    });

    await expect(screen.findAllByTestId(tooltipTestId)).rejects.toThrowError();
    act(() => Array.from(viewStateRegistry.values()).forEach((setState) => setState(true)));
    await expect(screen.findAllByTestId(tooltipTestId)).resolves.toHaveLength(2);
  });

  describe("has no out of bounds marks", () => {
    function expectBounded<T extends HTMLElement>(marks: T[]) {
      expect(marks.map(getMarkPosition).filter((p) => 0 < p && p < 100)).toHaveLength(marks.length);
    }

    test("with close positions", async () => {
      const modules = createModules(20, 0.1);
      renderTimeline({ modules });
      expectBounded(await screen.findAllByTestId(markTestId));
    });

    test("with distant positions", async () => {
      const modules = createModules(20, 1e3);
      renderTimeline({ modules });
      expectBounded(await screen.findAllByTestId(markTestId));
    });

    test("with mixed positions", async () => {
      const modules = [
        ...createModules(5, 0.1),
        ...createModules(5, 1),
        ...createModules(5, 1e6),
        ...createModules(5, 1e9),
      ];

      renderTimeline({ modules });
      expectBounded(await screen.findAllByTestId(markTestId));
    });
  });
});
