import Layout from "../components/layout";
import axios from "axios";
import {useRouter} from "next/router";
import {useState} from "react";

import ModuleCard from "../components/modulecards/ModuleCard";
import ModuleDetail from "../components/moduledetails/ModuleDetail";

function useTwoPaneState(...args) {
  const [moduleIndex, setModuleIndex] = useState(...args);
  return [moduleIndex, (e) => {
    if (e.ctrlKey || e.metaKey) return;
    e.preventDefault();
    setModuleIndex(e.currentTarget.dataset.index);
  }];
}

export default function Search({searchResults}) {
  const router = useRouter();
  const query = router.query['query'];
  const modules = searchResults['results'];

  const [moduleIndex, setModuleIndex] = useTwoPaneState(0);

  const pageHeader = (
    <h1 className='my-0 py-1'>
      {query ?
        <small>{searchResults['count']} results for <b>{query}</b></small>
        :
        <small>{searchResults['count']} items</small>
      }
    </h1>
  );

  if (modules?.length === 0) {
    return (
      <Layout title={"SERCH"}>
        <div className="serp-container">
          <div className="container">
            <p className="lead text-center my-3 py-3">
              There are no results for your search. Please try a different search.
            </p>
            <div className="row">
              <div className="col-12 col-md-6 mx-auto my-3 py-3">
                {/*{% crispy search_form %}*/}
                <p>{"<Crispy Search Form>"}</p>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title={"SERCH"}>
      <div className="serp-container">

        {/*{% with display_option=request.GET.display %}*/}
        <div id="slider" className="refinements-container side closed">
          {/*{% crispy search_form %}*/}
          <p>crispy</p>
        </div>
        <button id="sliderToggle" className="toggle-button btn btn-md btn-outline-black">
          <i className="fas fa-filter"/>
        </button>

        <div className="display-options">
          {/*{% with selected_option=display_option %}*/}
          {/*<span className="display-option">*/}
          {/*                      <input type="radio" id="2pane-option" name="display" value="2pane"*/}
          {/*                             {% if selected_option == '2pane' or not selected_option %} checked{% endif %} />*/}
          {/*                      <label htmlFor="2pane-option"><i className="fas fa-list"></i></label>*/}
          {/*                  </span>*/}
          {/*<span className="display-option">*/}
          {/*                      <input type="radio" id="rows-option" name="display" value="rows"*/}
          {/*                             {% if selected_option == 'rows' %} checked{% endif %} />*/}
          {/*                      <label htmlFor="rows-option"><i className="fas fa-bars"></i></label>*/}
          {/*                  </span>*/}
          {/*<span className="display-option">*/}
          {/*                      <input type="radio" id="timeline-option" name="display" value="timeline"*/}
          {/*                             {% if selected_option == 'timeline' %} checked{% endif %} />*/}
          {/*                      <label htmlFor="timeline-option"><i className="fas fa-columns"></i></label>*/}
          {/*                  </span>*/}
          {/*{% endwith %}*/}
        </div>

        <div className="results-container">
          {pageHeader}
          {/*{% if display_option == '2pane' or not display_option %}*/}
          <div className="two-pane-container">
            <div className="results result-cards">
              {modules.map((module, index) => (
                <a href={module['absolute_url']} className="result 2pane-result"
                   data-href={module['absolute_url']} data-key={module['slug']}
                   key={module['absolute_url']} data-index={index}
                   onClick={setModuleIndex}
                >
                  <ModuleCard module={module}/>
                </a>
              ))}
            </div>
            <div className="card view-detail sticky">
              <ModuleDetail module={modules[moduleIndex]}/>
            </div>
          </div>
          {/*{% elif display_option == 'rows' %}*/}
          {/*<div className="container results">*/}
          {/*  {% for object in object_list %}*/}
          {/*  <div className="result" data-key="{{ object.slug }}">*/}
          {/*    {{object | get_detail_html}}*/}
          {/*  </div>*/}
          {/*  <hr style="clear: both"/>*/}
          {/*  {% endfor %}*/}
          {/*</div>*/}
          {/*{% elif display_option == 'timeline' %}*/}
          {/*<p>Not yet implemented</p>*/}
          {/*{% endif %}*/}
        </div>
      </div>
    </Layout>
  );
}

export async function getServerSideProps(context) {
  let searchResults = {};
  // convert query object into url query string
  const query = (
    Object.entries(context.query).map(([k, v]) => `${k}=${v}`).join('&')
  );

  await axios.get(
    `http://django:8000/api/search/${query && `?${query}`}`
  ).then((response) => {
    searchResults = response.data;
  }).catch((error) => {
    // console.error(error);
  });

  return {
    props: {
      searchResults,
    },
  };
}