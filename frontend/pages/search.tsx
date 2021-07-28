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
import { FC, useCallback, useEffect, useState } from "react";

function useTwoPaneState() {
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
  return { moduleIndex, setModuleIndex, setModuleIndexFromEvent };
}

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
  searchResults: {
    count: number;
    total_pages: number;
    results: ModuleUnion[];
  };
}

const Search: FC<SearchProps> = ({ searchResults }: SearchProps) => {
  const classes = useStyles();
  const router = useRouter();
  const { moduleIndex, setModuleIndex, setModuleIndexFromEvent } = useTwoPaneState();

  // determines whether the search filter sidebar is open
  const [searchOpen, setSearchOpen] = useState(false);

  // controls whether the modal is open
  const [modalOpen, setModalOpen] = useState(false);
  // media query value is based on /core/static/styles/serp.css
  const smallScreen = useMediaQuery("(max-width: 660px)");

  const selectModule = (event) => {
    setModuleIndexFromEvent(event);
    setModalOpen(true);
  };

  // Reset the selected module to 0 when a page transition occurs.
  useEffect(() => {
    const handle = () => setModuleIndex(0);
    router.events.on("routeChangeComplete", handle);
    return () => router.events.off("routeChangeComplete", handle);
  }, [router.events, setModuleIndex]);

  // get search string from URL params
  const query = router.query["query"];
  // get modules from API response
  const modules = searchResults["results"] || [];

  const pageHeader = (
    <h1 className="my-0 py-1">
      {query ? (
        <small>
          {searchResults["count"]} results for <b>{query}</b>
        </small>
      ) : (
        <small>{searchResults["count"]} items</small>
      )}
    </h1>
  );

  const title = `${query || "Historical"} occurrences, quotes, sources, and more`;

  // if the search had no results
  if (modules?.length === 0) {
    return (
      <Layout title={title}>
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
      </Layout>
    );
  }

  // This was mostly copied from `modularhistory/core/templates/list.html`
  // Commented blocks are retained to show what was not converted.
  return (
    <Layout title={title}>
      <div className="serp-container">
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

        <div className="results-container">
          {pageHeader}

          <div className="two-pane-container">
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
                  <ModuleUnionCard module={module} selected={index == moduleIndex} />
                </a>
              ))}
            </div>

            {smallScreen ? (
              <ModuleModal
                module={modules[moduleIndex] || modules[0]}
                open={modalOpen}
                setOpen={setModalOpen}
              />
            ) : (
              <div className="card view-detail sticky">
                <ModuleDetail module={modules[moduleIndex] || modules[0]} />
              </div>
            )}
          </div>
        </div>
      </div>

      <Container>
        <Pagination count={searchResults["total_pages"]} />
      </Container>
    </Layout>
  );
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
    .then((response) => {
      searchResults = response.data;
    })
    .catch((error) => {
      // TODO...
      console.log(error);
    });

  return {
    props: {
      searchResults,
    },
  };
};
