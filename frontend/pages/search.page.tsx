import BigAnchor from "@/components/BigAnchor";
import ModuleUnionCard from "@/components/cards/ModuleUnionCard";
import ModuleDetail from "@/components/details/ModuleDetail";
import ModuleModal from "@/components/details/ModuleModal";
import Layout from "@/components/Layout";
import Pagination from "@/components/Pagination";
import type { TimelineProps } from "@/components/search/Timeline";
import { GlobalTheme } from "@/pages/_app.page";
import { SerpModule } from "@/types/modules";
import { Box, Container, Drawer, styled, useMediaQuery } from "@mui/material";
import axios from "axios";
import { GetServerSideProps } from "next";
import { NextSeo } from "next-seo";
import dynamic from "next/dynamic";
import { NextRouter, useRouter, withRouter } from "next/router";
import qs from "qs";
import {
  createRef,
  Dispatch,
  FC,
  memo,
  MouseEventHandler,
  SetStateAction,
  useEffect,
  useMemo,
  useState,
} from "react";
import { InView } from "react-intersection-observer";

const DynamicSearchForm = dynamic(() => import("@/components/search/SearchForm"), {
  ssr: false,
});

const Timeline = dynamic(() => import("@/components/search/Timeline"), { ssr: false });

const SliderToggle = styled("button")({
  border: "2px solid black !important",
  transition: "transform .15s !important",
  "&.open": { transform: "translateX(229px) !important" },
});

export interface SearchProps {
  count: number;
  totalPages: number;
  results: SerpModule[];
}

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
  memo(
    function SearchResultsPanes({
      modules,
      router,
    }: {
      modules: SerpModule[];
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

      return (
        <div className="two-pane-container">
          {useMemo(
            () => (
              <SearchResultsLeftPane {...{ modules, setModuleIndex, setModalOpen, router }} />
            ),
            [modules]
          )}
          <SearchResultsRightPane
            // set key to prevent new details from retaining previous scroll position
            key={moduleIndex}
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
  modules: SerpModule[];
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
        () => modulesWithRefs[initialIndex].ref.current?.scrollIntoView({ behavior: "smooth" }),
        100
      );
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const viewStateRegistry: TimelineProps["viewStateRegistry"] = new Map();

  const modulesWithRefs: TimelineProps<HTMLAnchorElement>["modules"] = useMemo(
    () => modules.map((module) => ({ ...module, ref: createRef() })),
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
          style={{ marginBottom: "0.5rem" }}
        >
          <BigAnchor
            href={module.absoluteUrl}
            className={`result 2pane-result`}
            key={module.absoluteUrl}
            data-index={index}
            onClick={selectModule}
            ref={modulesWithRefs[index].ref}
          >
            <ModuleUnionCard module={module} />
          </BigAnchor>
        </InView>
      ))}
    </Box>
  );
};

interface RightPaneProps {
  module: SerpModule;
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
