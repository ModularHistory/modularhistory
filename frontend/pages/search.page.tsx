import BigAnchor from "@/components/BigAnchor";
import ModuleUnionCard from "@/components/cards/ModuleUnionCard";
import ModuleModal from "@/components/details/ModuleModal";
import Layout from "@/components/Layout";
import Pagination from "@/components/Pagination";
import type { TimelineProps } from "@/components/search/Timeline";
import SwipeableEdgeDrawer from "@/components/SwipeableEdgeDrawer";
import { SerpModule } from "@/types/modules";
import { Divider, Grid, Stack } from "@mui/material";
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
  RefObject,
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

// const SliderToggle = styled("button")({
//   border: "2px solid black !important",
//   transition: "transform .15s !important",
//   "&.open": { transform: "translateX(229px) !important" },
// });

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
        <Stack divider={<Divider />} alignItems={"center"}>
          <SearchPageHeader {...props} />
          <SearchResultsPanes modules={props.results} />
          <Pagination count={props.totalPages} />
        </Stack>
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

// const SearchFilter: FC = () => {
//   const [searchOpen, setSearchOpen] = useState(false);
//   return (
//     <>
//       <Drawer
//         open={searchOpen}
//         anchor={"left"}
//         variant={"persistent"}
//         onClose={() => setSearchOpen(false)}
//         className={searchOpen ? "open" : ""}
//         sx={{
//           maxWidth: "0px",
//           transition: "max-width .15s",
//           zIndex: 2,
//           "&.open": { maxWidth: "230px" },
//         }}
//         PaperProps={{
//           sx: {
//             backgroundColor: "whitesmoke",
//             boxShadow: "4px 0 10px -5px #888",
//             position: "sticky",
//             maxHeight: "100vh",
//           },
//         }}
//       >
//         <DynamicSearchForm inSidebar />
//       </Drawer>
//       <SliderToggle
//         id="sliderToggle"
//         className={`btn ${searchOpen ? "open" : ""}`}
//         onClick={() => setSearchOpen(!searchOpen)}
//       >
//         <i className="fas fa-filter" />
//       </SliderToggle>
//     </>
//   );
// };

const SearchPageHeader: FC<SearchProps> = ({ count }: SearchProps) => {
  const {
    query: { query },
  } = useRouter();
  const jutContent = query ? (
    <small>
      {count} results for <b>{query}</b>
    </small>
  ) : (
    <small>{count} items</small>
  );
  return (
    <SwipeableEdgeDrawer jutRem={1.5} jutContent={jutContent}>
      <DynamicSearchForm />
    </SwipeableEdgeDrawer>
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

      const viewStateRegistry: TimelineProps["viewStateRegistry"] = useMemo(() => new Map(), []);
      // TODO: no need for useMemo since the whole thang is memoized
      const modulesWithRefs: (SerpModule & { ref: RefObject<any> })[] = useMemo(
        () => modules.map((module) => ({ ...module, ref: createRef() })),
        [modules]
      );

      return (
        <Stack direction={"row"} divider={<Divider orientation={"vertical"} flexItem />}>
          <Timeline
            modules={modulesWithRefs}
            viewStateRegistry={viewStateRegistry}
            sx={{
              position: "sticky",
              top: "5.5rem",
              marginTop: "3.2rem",
              height: "80vh",
              zIndex: 10,
            }}
          />
          {useMemo(
            () => (
              <SearchResultsGrid
                modules={modulesWithRefs}
                {...{
                  moduleIndex,
                  setModuleIndex,
                  setModalOpen,
                  router,
                  viewStateRegistry,
                }}
              />
            ),
            [modules, moduleIndex, viewStateRegistry]
          )}
          <ModuleModal module={modules[moduleIndex]} open={isModalOpen} setOpen={setModalOpen} />
        </Stack>
      );
    },
    (prevProps, nextProps) => {
      // prevent re-render when router updates.
      return prevProps.modules === nextProps.modules;
    }
  )
);

interface LeftPaneProps extends Pick<TimelineProps, "viewStateRegistry"> {
  modules: (SerpModule & { ref: RefObject<any> })[];
  setModalOpen: Dispatch<SetStateAction<boolean>>;
  moduleIndex: number;
  setModuleIndex: Dispatch<SetStateAction<number>>;
  router: NextRouter;
}

const SearchResultsGrid: FC<LeftPaneProps> = ({
  modules,
  moduleIndex,
  setModuleIndex,
  setModalOpen,
  router,
  viewStateRegistry,
}) => {
  // we are unable to obtain the url anchor during SSR,
  // so we must update the selected module after rendering.
  useEffect(() => {
    const urlAnchor = router.asPath.split("#")[1];
    const initialIndex = urlAnchor ? modules.findIndex((module) => module.slug === urlAnchor) : 0;
    if (initialIndex > 0) {
      setModuleIndex(initialIndex);
      setTimeout(
        () =>
          modules[initialIndex].ref.current?.scrollIntoView({
            behavior: "smooth",
            block: "nearest",
          }),
        100
      );
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

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
    <Grid
      container
      maxWidth={1800}
      spacing={2}
      padding="1rem"
      alignItems="flex-start"
      justifyContent="flex-start"
    >
      {modules.map((module, index) => (
        <Grid
          xs={12}
          sm={6}
          md={4}
          lg={3}
          xl={2}
          item
          key={module.absoluteUrl}
          sx={{
            "& .selected": {
              borderLeft: "8px solid #FFE000",
              borderRadius: "5px",
            },
          }}
        >
          <InView
            as="div"
            onChange={(inView) => {
              // viewStateRegistry.get(module.absoluteUrl)?.(inView);
            }}
          >
            <BigAnchor
              href={module.absoluteUrl}
              key={module.absoluteUrl}
              data-index={index}
              onClick={selectModule}
              ref={modules[index].ref}
              onMouseEnter={() => viewStateRegistry.get(module.absoluteUrl)?.(true)}
              onMouseLeave={() => viewStateRegistry.get(module.absoluteUrl)?.(false)}
            >
              <ModuleUnionCard module={module} className={index == moduleIndex ? "selected" : ""} />
            </BigAnchor>
          </InView>
        </Grid>
      ))}
    </Grid>
  );
};

export default Search;

export const getServerSideProps: GetServerSideProps = async (context) => {
  let searchResults: SearchProps = {
    count: 0,
    totalPages: 0,
    results: [],
  };

  await axios
    .get(`http://django:${process.env.DJANGO_PORT}/api/search/`, {
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
