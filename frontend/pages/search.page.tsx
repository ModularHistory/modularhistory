import ModuleUnionCard from "@/components/cards/ModuleUnionCard";
import ModuleDetail from "@/components/details/ModuleDetail";
import ModuleModal from "@/components/details/ModuleModal";
import Layout from "@/components/Layout";
import Pagination from "@/components/Pagination";
import { GlobalTheme } from "@/pages/_app.page";
import { ModuleUnion, Topic } from "@/types/modules";
import { Compress } from "@mui/icons-material";
import type { Mark } from "@mui/material";
import {
  Box,
  Container,
  Divider,
  Drawer,
  Slider,
  SliderMark,
  SliderMarkLabel,
  Stack,
  styled,
  useMediaQuery,
} from "@mui/material";
import axios from "axios";
import { GetServerSideProps } from "next";
import { NextSeo } from "next-seo";
import dynamic from "next/dynamic";
import { useRouter } from "next/router";
import qs from "qs";
import {
  Dispatch,
  FC,
  MouseEventHandler,
  SetStateAction,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import { InView } from "react-intersection-observer";

const DynamicSearchForm = dynamic(() => import("@/components/search/SearchForm"), {
  ssr: false,
});

const SliderToggle = styled("button")({
  border: "2px solid black !important",
  transition: "transform .15s !important",
  "&.open": { transform: "translateX(229px) !important" },
});

const getModuleUID = ({ model, id }: SearchProps["results"][number]) => `${model}-${id}`;

interface SearchProps {
  count: number;
  totalPages: number;
  results: Exclude<ModuleUnion, Topic>[];
}

const Search: FC<SearchProps> = (props: SearchProps) => {
  const {
    query: { query },
  } = useRouter();
  const title = `${query || "Historical"} occurrences, quotes, sources, and more`;

  const [viewState, setViewState] = [
    Object.fromEntries(props.results.map((module) => [getModuleUID(module), false])),
    () => {},
  ]; //useState(() =>
  //Object.fromEntries(props.results.map((module) => [getModuleUID(module), false]))
  //);

  const now = new Date().getFullYear();
  const marks: Mark[] = [];
  const years = props.results.map((r) => r.timelinePosition).sort((a, b) => a - b);
  props.results.forEach((module, index) =>
    marks.push({
      value: module.timelinePosition + Number(`${index}e-5`),
      label: module.slug, //viewState[getModuleUID(module)] ? module.slug : null,
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
            {now - (end - buffer)} CE — {now - (start + buffer)} CE
          </Box>
        ),
        length: length - 2 * buffer,
      };
      breaks.push(break_);
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

  console.log({ marks: [...marks] });
  marks.forEach((mark) => {
    mark.value = scale(mark.value);
  });

  const buffer = averageDistance / 4;
  const min = Math.floor(years[0] - buffer);
  const max = scale(Math.ceil(years[years.length - 1] + buffer));
  console.log({ breaks, years, yearsCE: years.map((y) => 2021 - y), scale, descale });
  const slider = (
    <Slider
      orientation={"vertical"}
      valueLabelDisplay={"on"}
      marks={marks}
      defaultValue={[min, max]}
      min={min}
      max={max}
      valueLabelFormat={(value) => {
        // if (breaks.map(b => b.value).includes(descale(value))) return "break";
        return `${now - descale(value)} CE`; // return `${2021 - value} CE`;
      }}
      sx={{
        height: "80vh",
        position: "fixed",
        left: "80px",
        "& .MuiSlider-mark": {
          width: "12px",
          backgroundColor: "#212529",
        },
      }}
      components={{
        Mark: (props) => (
          <SliderMark {...props}>
            {props["data-index"] >= years.length && (
              <Compress sx={{ transform: "translate(-25%, -50%)", backgroundColor: "white" }} />
            )}
          </SliderMark>
        ),
        MarkLabel: (props) => {
          // console.log(props)
          return <SliderMarkLabel {...props} />;
        },
      }}
    />
  );

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
              {/*<hr />*/}
              {/*{slider}*/}
              {/*<hr />*/}
              <Stack
                direction={"row"}
                spacing={12}
                divider={<Divider orientation="vertical" flexItem />}
              >
                {slider}
                <SearchResultsPanes {...props} setViewState={setViewState} />
              </Stack>
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

interface TwoPaneState {
  moduleIndex: number;
  setModuleIndex: Dispatch<SetStateAction<number>>;
  setModuleIndexFromEvent: MouseEventHandler;
}

function useTwoPaneState(): TwoPaneState {
  // This hook is used to track which card in the left pane
  // should have its details displayed in the right pane.
  const router = useRouter();
  const [moduleIndex, setModuleIndex] = useState(0);

  // event handler for when the user clicks on a module card
  const setModuleIndexFromEvent = useCallback(
    (e) => {
      // This condition allows ctrl-clicking to open details in a new tab.
      if (e.ctrlKey || e.metaKey) return;
      e.preventDefault();

      const { index, key } = e.currentTarget.dataset;
      setModuleIndex(index);
      router.replace({ hash: key });
    },
    [router.replace]
  );

  // Reset the selected module to 0 when a page transition occurs.
  useEffect(() => {
    const handle = () => setModuleIndex(0);
    router.events.on("routeChangeComplete", handle);
    return () => router.events.off("routeChangeComplete", handle);
  }, [router.events]);

  return { moduleIndex, setModuleIndex, setModuleIndexFromEvent };
}

interface PaneProps extends SearchProps, TwoPaneState {
  isModalOpen: boolean;
  setModalOpen: Dispatch<SetStateAction<boolean>>;
  initialUrlAnchor: string;
}

const SearchResultsPanes: FC<SearchProps> = (props: SearchProps) => {
  const twoPaneState = useTwoPaneState();

  // controls whether the modal is open (conditional based on screen size)
  const [isModalOpen, setModalOpen] = useState(false);

  const paneProps: PaneProps = {
    ...props,
    ...twoPaneState,
    isModalOpen,
    setModalOpen,
    // useRef here guarantees the initial value is retained when the hash is updated
    initialUrlAnchor: useRef(useRouter().asPath.split("#")[1]).current,
  };

  return (
    <div className="two-pane-container">
      <SearchResultsLeftPane {...paneProps} />
      <SearchResultsRightPane {...paneProps} />
    </div>
  );
};

const SearchResultsLeftPane: FC<PaneProps> = ({
  results: modules,
  moduleIndex,
  setModuleIndexFromEvent,
  setModalOpen,
  initialUrlAnchor,
  setViewState,
}) => {
  const selectModule: MouseEventHandler = (event) => {
    setModuleIndexFromEvent(event);
    setModalOpen(true);
  };

  // on initial load, scroll to the module card designated by the url anchor
  const initialModuleRef = useRef<HTMLAnchorElement>(null);
  useEffect(() => {
    // non-delayed scrolls sometimes cause inconsistent behavior, so wait 100ms
    setTimeout(() => initialModuleRef.current?.scrollIntoView({ behavior: "smooth" }), 100);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return (
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
            console.debug(`Inview: ${inView}`, module.slug);
            setViewState((os) => ({ ...os, [getModuleUID(module)]: inView }));
          }}
        >
          <a
            href={module.absoluteUrl}
            className={`result 2pane-result ${index == moduleIndex ? "selected" : ""}`}
            data-href={module.absoluteUrl}
            data-key={module.slug}
            key={module.slug}
            data-index={index}
            onClick={selectModule}
            ref={initialUrlAnchor === module.slug && index !== 0 ? initialModuleRef : undefined}
          >
            <ModuleUnionCard module={module} selected={index === moduleIndex} />
          </a>
        </InView>
      ))}
    </Box>
  );
};

const SearchResultsRightPane: FC<PaneProps> = ({
  results: modules,
  moduleIndex,
  isModalOpen,
  setModalOpen,
  setModuleIndex,
  initialUrlAnchor,
}) => {
  // we are unable to obtain the url anchor during SSR,
  // so we must update the selected module after rendering.
  useEffect(() => {
    const initialIndex = initialUrlAnchor
      ? modules.findIndex((module) => module.slug === initialUrlAnchor)
      : 0;
    setModuleIndex(initialIndex);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // media query value is based on /core/static/styles/serp.css
  const smallScreen = useMediaQuery((theme: GlobalTheme) => theme.breakpoints.down("sm"));
  const selectedModule = modules[moduleIndex] || modules[0];

  if (smallScreen) {
    return <ModuleModal module={selectedModule} open={isModalOpen} setOpen={setModalOpen} />;
  } else {
    return (
      <div className="card view-detail sticky">
        <ModuleDetail module={selectedModule} key={selectedModule.absoluteUrl} />
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
