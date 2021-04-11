import qs from "qs";
import axios from "axios";

import Layout from "../components/Layout";
import Pagination from "../components/Pagination";

import {useRouter} from "next/router";
import {useState, useEffect, useCallback} from "react";

import ModuleCard from "../components/modulecards/ModuleCard";
import ModuleDetail from "../components/moduledetails/ModuleDetail";
import SearchForm from "../components/search/SearchForm";

import {Drawer, Grid, Container, Box} from "@material-ui/core";
import {makeStyles} from "@material-ui/styles";

function useTwoPaneState(...args) {
  // This hook is used to track which card in the left pane
  // should have its details displayed in the right pane.
  const [moduleIndex, setModuleIndex] = useState(...args);

  // event handler for when the user clicks on a module card
  const setModuleIndexFromEvent = useCallback((e) => {
    // This condition allows ctrl-clicking to open details in a new tab.
    if (e.ctrlKey || e.metaKey) return;
    e.preventDefault();
    setModuleIndex(e.currentTarget.dataset.index);
  }, []);
  return {moduleIndex, setModuleIndex, setModuleIndexFromEvent};
}

const useStyles = makeStyles({
  drawer: {
    maxWidth: "0px",
    transition: "max-width .15s",
    zIndex: 2,
    "&.open": {maxWidth: "230px"},
  },
  drawerButton: {
    border: "2px solid black",
    transition: "transform .15s",
    "&.open": {transform: "translateX(229px)"},
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
    }
  }
});

export default function Search({searchResults}) {
  const classes = useStyles();
  const router = useRouter();
  const {
    moduleIndex,
    setModuleIndex,
    setModuleIndexFromEvent
  } = useTwoPaneState(0);

  // determines whether the search filter sidebar is open
  const [isSearchOpen, setIsSearchOpen] = useState(false);

  // Reset the selected module to 0 when a page transition occurs.
  useEffect(() => {
    const handle = () => setModuleIndex(0);
    router.events.on("routeChangeEnd", handle);
    return () => router.events.off("routeChangeEnd", handle);
  }, []);

  // get search string from URL params
  const query = router.query["query"];
  // get modules from API response
  const modules = searchResults["results"] || [];

  const pageHeader = (
    <h1 className='my-0 py-1'>
      {query ?
        <small>{searchResults["count"]} results for <b>{query}</b></small>
        :
        <small>{searchResults["count"]} items</small>
      }
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
              <SearchForm/>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  // This was mostly copied from `modularhistory/templates/list.html`
  // Commented blocks are retained to show what was not converted.
  return (
    <Layout title={title}>
      <div className="serp-container">

        <Drawer open={isSearchOpen}
                anchor={"left"}
                variant={"persistent"}
                onClose={() => setIsSearchOpen(false)}
                className={`${classes.drawer} ${isSearchOpen ? "open" : ""}`}
                PaperProps={{className: classes.paper}}>
          <SearchForm inSidebar/>
        </Drawer>
        <button id="sliderToggle"
                className={`btn ${classes.drawerButton} ${isSearchOpen ? "open" : ""}`}
                onClick={() => setIsSearchOpen(!isSearchOpen)}>
          <i className="fas fa-filter"/>
        </button>

        <div className="results-container">

          {pageHeader}

          <div className="two-pane-container">
            <div className={`results result-cards ${classes.cards}`}>

              {modules.map((module, index) => (
                <a href={module['absolute_url']} className="result 2pane-result"
                   data-href={module['absolute_url']} data-key={module['slug']}
                   key={module['absolute_url']} data-index={index}
                   onClick={setModuleIndexFromEvent}
                >
                  <ModuleCard module={module}
                              cardClass={index == moduleIndex ? "selected" : ""}/>
                </a>
              ))}

            </div>

            <div className="card view-detail sticky">
              <ModuleDetail module={modules[moduleIndex] || moduleIndex[0]}/>
            </div>

          </div>
        </div>
      </div>

      <Container>
        <Pagination count={searchResults["total_pages"]}/>
      </Container>

    </Layout>
  );
}

export async function getServerSideProps(context) {
  let searchResults = {};

  await axios
    .get("http://django:8000/api/search/", {
      params: context.query,
      paramsSerializer: (params) => (
        // we use qs since otherwise axios formats
        // array parameters with "[]" appended.
        qs.stringify(params, {arrayFormat: "repeat"})
      ),
    })
    .then((response) => {
      searchResults = response.data;
    })
    .catch((error) => {
      // console.error(error);
    });

  return {
    props: {
      searchResults,
    },
  };
}