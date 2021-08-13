import ModuleUnionCard from "@/components/cards/ModuleUnionCard";
import ModuleDetail from "@/components/details/ModuleDetail";
import ModuleModal from "@/components/details/ModuleModal";
import Layout from "@/components/Layout";
import Pagination from "@/components/Pagination";
import SearchForm from "@/components/search/SearchForm";
import { ModuleUnion } from "@/interfaces";
import { Container, Drawer, useMediaQuery } from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import axios from "axios";
import { GetServerSideProps } from "next";
import { useRouter } from "next/router";
import qs from "qs";
import { Dispatch, FC, SetStateAction, useCallback, useEffect, useState } from "react";

const useStyles = makeStyles({
  drawer: {
    maxWidth: "0px",
    transition: "max-width .15s",
    zIndex: 2,
    "&.open": { maxWidth: "230px" },
  },
  drawerButton: {
    border: "2px solid black",
    transition: "transform .15s",
    "&.open": { transform: "translateX(229px)" },
  },
  paper: {
    backgroundColor: "whitesmoke",
    boxShadow: "4px 0 10px -5px #888",
    position: "sticky",
    maxHeight: "100vh",
  },
  cards: {
    "& .selected": {
      border: "3px solid black",
      borderRight: "none",
    },
  },
});

interface SearchProps {
  count: number;
  total_pages: number;
  results: ModuleUnion[];
}

const Search: FC<SearchProps> = (props: SearchProps) => {
  const {
    query: { query },
  } = useRouter();
  const title = `${query || "Historical"} occurrences, quotes, sources, and more`;

  return (
    <Layout title={title}>
      {props.results.length === 0 ? (
        <EmptySearchResults />
      ) : (
        <>
          <div className="serp-container">
            <SearchFilter />

            <div className="results-container">
              <SearchPageHeader {...props} />
              <SearchResultsPanes {...props} />
            </div>
          </div>

          <Container>
            <Pagination count={props.total_pages} />
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
        <SearchForm />
      </div>
    </div>
  </div>
);

const SearchFilter: FC = () => {
  const [searchOpen, setSearchOpen] = useState(false);
  const classes = useStyles();

  return (
    <>
      <Drawer
        open={searchOpen}
        anchor={"left"}
        variant={"persistent"}
        onClose={() => setSearchOpen(false)}
        className={`${classes.drawer} ${searchOpen ? "open" : ""}`}
        PaperProps={{ className: classes.paper }}
      >
        <SearchForm inSidebar />
      </Drawer>
      <button
        id="sliderToggle"
        className={`btn ${classes.drawerButton} ${searchOpen ? "open" : ""}`}
        onClick={() => setSearchOpen(!searchOpen)}
      >
        <i className="fas fa-filter" />
      </button>
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
  setModuleIndexFromEvent: (event: MouseEvent) => void;
}

function useTwoPaneState(): TwoPaneState {
  // This hook is used to track which card in the left pane
  // should have its details displayed in the right pane.
  const [moduleIndex, setModuleIndex] = useState(0);

  // event handler for when the user clicks on a module card
  const setModuleIndexFromEvent = useCallback((e) => {
    // This condition allows ctrl-clicking to open details in a new tab.
    if (e.ctrlKey || e.metaKey) return;
    e.preventDefault();
    setModuleIndex(e.currentTarget.dataset.index);
  }, []);

  // Reset the selected module to 0 when a page transition occurs.
  const router = useRouter();
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
}) => {
  const classes = useStyles();

  const selectModule = (event) => {
    setModuleIndexFromEvent(event);
    setModalOpen(true);
  };

  return (
    <div className={`results result-cards ${classes.cards}`}>
      {modules.map((module, index) => (
        <a
          href={module.absoluteUrl}
          className="result 2pane-result"
          data-href={module.absoluteUrl}
          data-key={module.slug}
          key={module.slug}
          data-index={index}
          onClick={selectModule}
        >
          <ModuleUnionCard module={module} selected={index === moduleIndex} />
        </a>
      ))}
    </div>
  );
};

const SearchResultsRightPane: FC<PaneProps> = ({
  results: modules,
  moduleIndex,
  isModalOpen,
  setModalOpen,
}) => {
  // media query value is based on /core/static/styles/serp.css
  const smallScreen = useMediaQuery("(max-width: 660px)");
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
  let searchResults = {};

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
