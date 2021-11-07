import ModuleUnionCard from "@/components/cards/ModuleUnionCard";
import ModuleDetail from "@/components/details/ModuleDetail";
import ModuleModal from "@/components/details/ModuleModal";
import Layout from "@/components/Layout";
import Pagination from "@/components/Pagination";
import { GlobalTheme } from "@/pages/_app.page";
import { ModuleUnion, Topic } from "@/types/modules";
import { Compress } from "@mui/icons-material";
import type { Mark, SliderProps } from "@mui/material";
import {
  Box,
  Container,
  Drawer,
  Slider as MuiSlider,
  sliderClasses,
  SliderMark as MuiSliderMark,
  SliderThumb,
  styled,
  Tooltip,
  useMediaQuery,
} from "@mui/material";
import axios from "axios";
import { GetServerSideProps } from "next";
import { NextSeo } from "next-seo";
import dynamic from "next/dynamic";
import { NextRouter, useRouter, withRouter } from "next/router";
import qs from "qs";
import React, {
  ComponentProps,
  createRef,
  Dispatch,
  FC,
  MouseEventHandler,
  MutableRefObject,
  RefObject,
  SetStateAction,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { InView } from "react-intersection-observer";

const commaRegex = new RegExp(/(\d)(?=(\d{3})+$)/g);

function formatYbp(ybp: number, thisYear: number) {
  const TEN_THOUSAND = 1e4;
  const MILLION = 1e6;
  const BILLION = 1e9;
  const diff = thisYear - ybp;
  const bce = -diff - 1;

  let year: number;
  let type: "CE" | "BCE" | "YBP";
  let multiplier: "M" | "B" | "" = "";

  if (diff > 0) {
    year = diff;
    type = "CE";
  } else if (bce <= 1e4) {
    year = bce;
    type = "BCE";
  } else {
    year = ybp;
    type = "YBP";
  }
  if (type != "CE") {
    if (year >= TEN_THOUSAND) {
      const digits = Math.floor(Math.log10(year)) + 1;
      const divisor = 10 ** (digits - 3);
      year = Math.round(year / divisor) * divisor;
    }

    if (year >= BILLION) {
      year /= BILLION;
      multiplier = "B";
    } else if (year >= MILLION) {
      year /= MILLION;
      multiplier = "M";
    }
  }
  const yearStr = multiplier ? year.toPrecision(3) : year.toString().replace(commaRegex, "$1,");
  return `${yearStr}${multiplier} ${type}`;
}

console.log(formatYbp);

const DynamicSearchForm = dynamic(() => import("@/components/search/SearchForm"), {
  ssr: false,
});

const SliderToggle = styled("button")({
  border: "2px solid black !important",
  transition: "transform .15s !important",
  "&.open": { transform: "translateX(229px) !important" },
});

interface SearchProps {
  count: number;
  totalPages: number;
  results: Exclude<ModuleUnion, Topic>[];
}

type ElementRef<T extends HTMLElement = HTMLElement> = MutableRefObject<T | null>;

const Slider: FC<SliderProps<"span", { componentsProps?: { mark: SliderMarkProps } }>> = styled(
  MuiSlider
)({
  height: "80vh",
  position: "fixed",
  left: "40px",
  [`& .${sliderClasses.mark}`]: {
    width: "12px",
    backgroundColor: "#212529",
  },
  [`.${sliderClasses.thumb}[data-index='0'] .${sliderClasses.valueLabel}`]: {
    top: 58,
    "&:before": { top: -8 },
  },
});

const BreakIcon = styled(Compress)({
  transform: "translate(-25%, -50%)",
  color: "gray",
  backgroundColor: "white",
});

interface SliderMarkProps extends ComponentProps<typeof MuiSliderMark> {
  modules: SearchProps["results"];
  moduleRefs: RefObject<any>[];
  viewStateRegistry: Map<string, Dispatch<SetStateAction<boolean>>>;
}

const SliderMark: FC<SliderMarkProps> = React.memo(
  ({ modules, moduleRefs, viewStateRegistry, ...markProps }) => {
    // Mui passes this prop but doesn't type it.
    const moduleIndex = (markProps as typeof markProps & { "data-index": number })["data-index"];
    const isBreak = moduleIndex >= modules.length;
    const module = isBreak ? undefined : modules[moduleIndex];

    const [tooltipOpen, setTooltipOpen] = useState(false);
    const [inView, setInView] = useState(false);
    if (module) viewStateRegistry.set(module.absoluteUrl, setInView);

    const handleClick = () => {
      const moduleCard = moduleRefs[moduleIndex].current;
      moduleCard?.scrollIntoView({ behavior: "smooth" });
      moduleCard?.click();
    };

    const sliderMark = (
      <MuiSliderMark {...markProps}>
        {isBreak ? (
          <BreakIcon />
        ) : (
          <Box position={"relative"} bottom={"3px"} padding={"5px"} onClick={handleClick} />
        )}
      </MuiSliderMark>
    );
    return isBreak ? (
      sliderMark
    ) : (
      <Tooltip
        title={
          <Box whiteSpace={"nowrap"} onClick={handleClick}>
            {modules[moduleIndex].title}
          </Box>
        }
        arrow
        placement={"right"}
        open={inView || tooltipOpen}
        onOpen={() => setTooltipOpen(true)}
        onClose={() => setTooltipOpen(false)}
        // MUI mis-types "popper" key as PopperProps instead of Partial<PopperProps>
        componentsProps={{ popper: { disablePortal: true } as any }}
      >
        {sliderMark}
      </Tooltip>
    );
  },
  (prevProps, nextProps) => {
    const keys: Array<keyof SliderMarkProps> = ["modules", "moduleRefs", "viewStateRegistry"];
    for (const key of keys) {
      if (prevProps[key] !== nextProps[key]) return false;
    }
    return true;
  }
);
SliderMark.displayName = "SliderMark";

type TimelineProps = {
  modules: SearchProps["results"];
  moduleRefs: RefObject<any>[];
} & Pick<SliderMarkProps, "viewStateRegistry">;

type TimelineCalculations = {
  now: number;
  scale: (n: number) => number;
  descale: (n: number) => number;
} & Required<Pick<SliderProps, "marks" | "min" | "max">>;

const Timeline: FC<TimelineProps> = ({ modules, moduleRefs, viewStateRegistry }) => {
  const [calculations, setCalculations] = useState<TimelineCalculations | null>(null);
  useEffect(() => {
    const now = new Date().getFullYear();
    const marks: Mark[] = [];
    const years = modules
      .map((m) => m.timelinePosition)
      .filter((n) => !Number.isNaN(n))
      .sort((a, b) => a - b);
    modules.forEach((module, index) =>
      marks.push({
        // add a tiny incremental value to eliminate duplicate keys
        value: module.timelinePosition + Number(`${index}e-5`),
      })
    );

    const ranges = years.slice(0, -1).map((year, index) => years[index + 1] - year);

    const averageDistance = (years[years.length - 1] - years[0]) / years.length;
    const breaks: (Mark & { length: number })[] = [];

    ranges.forEach((rangeLength, index) => {
      if (rangeLength > averageDistance) {
        const [start, end] = years.slice(index, index + 2).map(Math.round);
        const length = end - start;
        const buffer = Math.round(Math.min(averageDistance / 4, length * 0.1));
        // if (length <= buffer * 3) return;

        const break_ = {
          value: start + buffer,
          label: (
            <Box color={"lightgray"}>
              {formatYbp(end - buffer, now)} — {formatYbp(start + buffer, now)}
            </Box>
          ),
          length: length - 2 * buffer,
        };
        breaks.push(break_);
        // we scale marks but don't scale breaks, so create a new object
        marks.push({ ...break_ });
      }
    }, [] as number[]);
    breaks.sort((a, b) => a.value - b.value);
    const reverseBreaks = [...breaks].reverse();

    const scale = (n: number) => {
      for (const { value, length } of reverseBreaks) {
        if (n > value) n -= length;
      }
      return n;
    };

    const descale = (n: number) => {
      for (const { value, length } of breaks) {
        if (n > value) n += length;
      }
      return n;
    };

    marks.forEach((mark) => {
      mark.value = scale(mark.value);
    });

    const buffer = averageDistance / 4;
    const min = Math.floor(years[0] - buffer);
    const max = scale(Math.ceil(years[years.length - 1] + buffer));

    setCalculations({ now, marks, min, max, scale, descale });
  }, [modules]);

  const thumbRefs: ElementRef[] = [useRef(null), useRef(null)];

  if (calculations === null) {
    return <Slider key={0} orientation={"vertical"} defaultValue={[0, 100]} disabled />;
  }

  const { now, marks, min, max, descale } = calculations;

  return (
    <Slider
      key={1}
      onMouseDownCapture={(event) => {
        if (!thumbRefs.map((r) => r.current).includes(event.target as HTMLElement))
          event.stopPropagation();
      }}
      orientation={"vertical"}
      valueLabelDisplay={"on"}
      marks={marks}
      defaultValue={[min, max]}
      min={min}
      max={max}
      valueLabelFormat={(ybp) => formatYbp(descale(ybp), now)}
      componentsProps={{ mark: { modules, moduleRefs, viewStateRegistry } }}
      components={{
        Mark: SliderMark,
        Thumb: (props) => <SliderThumb {...props} ref={thumbRefs[props["data-index"]]} />,
      }}
    />
  );
};

const Search: FC<SearchProps> = (props: SearchProps) => {
  const {
    query: { query },
  } = useRouter();
  const title = `${query || "Historical"} occurrences, quotes, sources, and more`;

  return (
    <Layout>
      <NextSeo
        title={title}
        // TODO: build canonical URL for search?
        // canonical={"/search"}
        description={
          query
            ? `See occurrences, quotes, sources, etc. related to ${query}`
            : `Browse historical occurrences, quotes, sources, and more.`
        }
      />
      {props.results.length === 0 ? (
        <EmptySearchResults />
      ) : (
        <>
          <div className="serp-container">
            <SearchFilter />

            <div className="results-container">
              <SearchPageHeader {...props} />
              {/* force re-mount when results change because a variable number of hooks are used */}
              <SearchResultsPanes modules={props.results} />
            </div>
          </div>

          <Container>
            <Pagination count={props.totalPages} />
          </Container>
        </>
      )}
    </Layout>
  );
};

const EmptySearchResults: FC = () => (
  <div className="serp-container">
    <div className="container">
      <p className="lead text-center my-3 py-3">
        There are no results for your search. Please try a different search.
      </p>
      <div className="row">
        <DynamicSearchForm />
      </div>
    </div>
  </div>
);

const SearchFilter: FC = () => {
  const [searchOpen, setSearchOpen] = useState(false);

  return (
    <>
      <Drawer
        open={searchOpen}
        anchor={"left"}
        variant={"persistent"}
        onClose={() => setSearchOpen(false)}
        className={searchOpen ? "open" : ""}
        sx={{
          maxWidth: "0px",
          transition: "max-width .15s",
          zIndex: 2,
          "&.open": { maxWidth: "230px" },
        }}
        PaperProps={{
          sx: {
            backgroundColor: "whitesmoke",
            boxShadow: "4px 0 10px -5px #888",
            position: "sticky",
            maxHeight: "100vh",
          },
        }}
      >
        <DynamicSearchForm inSidebar />
      </Drawer>
      <SliderToggle
        id="sliderToggle"
        className={`btn ${searchOpen ? "open" : ""}`}
        onClick={() => setSearchOpen(!searchOpen)}
      >
        <i className="fas fa-filter" />
      </SliderToggle>
    </>
  );
};

const SearchPageHeader: FC<SearchProps> = ({ count }: SearchProps) => {
  const {
    query: { query },
  } = useRouter();
  return (
    <h1 className="my-0 py-1">
      {query ? (
        <small>
          {count} results for <b>{query}</b>
        </small>
      ) : (
        <small>{count} items</small>
      )}
    </h1>
  );
};

const SearchResultsPanes = withRouter(
  React.memo(
    function SearchResultsPanes({
      modules,
      router,
    }: {
      modules: SearchProps["results"];
      router: NextRouter;
    }) {
      // currently selected module
      const [moduleIndex, setModuleIndex] = useState(0);

      // Reset the selected module to 0 when a page transition occurs.
      useEffect(() => {
        const handle = () => setModuleIndex(0);
        router.events.on("routeChangeComplete", handle);
        return () => router.events.off("routeChangeComplete", handle);
      }, [router.events]);

      // controls whether the modal is open (conditional based on screen size)
      const [isModalOpen, setModalOpen] = useState(false);

      console.log("outer render");
      return (
        <div className="two-pane-container">
          {useMemo(
            () => (
              <SearchResultsLeftPane {...{ modules, setModuleIndex, setModalOpen, router }} />
            ),
            [modules]
          )}
          <SearchResultsRightPane
            {...{ module: modules[moduleIndex] ?? modules[0], isModalOpen, setModalOpen }}
          />
        </div>
      );
    },
    (prevProps, nextProps) => {
      // prevent re-render when router updates.
      return prevProps.modules === nextProps.modules;
    }
  )
);

interface LeftPaneProps {
  modules: SearchProps["results"];
  setModalOpen: Dispatch<SetStateAction<boolean>>;
  setModuleIndex: Dispatch<SetStateAction<number>>;
  router: NextRouter;
}

const SearchResultsLeftPane: FC<LeftPaneProps> = ({
  modules,
  setModuleIndex,
  setModalOpen,
  router,
}) => {
  // we are unable to obtain the url anchor during SSR,
  // so we must update the selected module after rendering.
  useEffect(() => {
    const urlAnchor = router.asPath.split("#")[1];
    const initialIndex = urlAnchor ? modules.findIndex((module) => module.slug === urlAnchor) : 0;
    if (initialIndex > 0) {
      setModuleIndex(initialIndex);
      setTimeout(
        () => moduleRefs[initialIndex].current?.scrollIntoView({ behavior: "smooth" }),
        100
      );
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const viewStateRegistry: TimelineProps["viewStateRegistry"] = new Map();

  const moduleRefs: RefObject<HTMLAnchorElement>[] = useMemo(
    () => [...Array(modules.length)].map(() => createRef()),
    [modules]
  );

  const selectModule: MouseEventHandler = (e) => {
    // This condition allows ctrl-clicking to open details in a new tab.
    if (e.ctrlKey || e.metaKey) return;
    e.preventDefault();

    const { index } = (e.currentTarget as any).dataset;
    setModuleIndex(index);
    router.replace({ hash: modules[index].slug });
    setModalOpen(true);
  };

  return (
    <>
      <Timeline {...{ modules, moduleRefs, viewStateRegistry }} />
      <Box
        className={"results result-cards"}
        sx={{
          "& .selected": {
            border: "3px solid black",
            borderRight: "none",
          },
        }}
      >
        {modules.map((module, index) => (
          <InView
            as="div"
            onChange={(inView) => {
              viewStateRegistry.get(module.absoluteUrl)?.(inView);
            }}
            key={module.absoluteUrl}
          >
            <a
              href={module.absoluteUrl}
              className={`result 2pane-result`}
              key={module.absoluteUrl}
              data-index={index}
              onClick={selectModule}
              ref={moduleRefs[index]}
            >
              <ModuleUnionCard module={module} />
            </a>
          </InView>
        ))}
      </Box>
    </>
  );
};

interface RightPaneProps {
  module: SearchProps["results"][number];
  isModalOpen: boolean;
  setModalOpen: Dispatch<SetStateAction<boolean>>;
}

const SearchResultsRightPane: FC<RightPaneProps> = ({ module, isModalOpen, setModalOpen }) => {
  // media query value is based on /core/static/styles/serp.css
  const smallScreen = useMediaQuery((theme: GlobalTheme) => theme.breakpoints.down("sm"));

  if (smallScreen) {
    return <ModuleModal module={module} open={isModalOpen} setOpen={setModalOpen} />;
  } else {
    return (
      <div className="card view-detail sticky">
        <ModuleDetail module={module} key={module.absoluteUrl} />
      </div>
    );
  }
};

export default Search;

export const getServerSideProps: GetServerSideProps = async (context) => {
  let searchResults: SearchProps = {
    count: 0,
    totalPages: 0,
    results: [],
  };

  await axios
    .get("http://django:8000/api/search/", {
      params: context.query,
      paramsSerializer: (params) =>
        // we use qs since otherwise axios formats
        // array parameters with "[]" appended.
        qs.stringify(params, { arrayFormat: "repeat" }),
    })
    .then(({ data }) => {
      searchResults = data;
      if (!Array.isArray(searchResults["results"])) {
        searchResults["results"] = [];
      }
    })
    // TODO: handle error
    .catch(console.error);

  return {
    props: searchResults,
  };
};
