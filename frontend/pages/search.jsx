import Layout from "../components/layout";
import axios from "axios";

export default function Search({searchResults}) {
  return (
    <Layout title={"SERCH"}>
      <pre>
        {JSON.stringify(searchResults, null, 4)}
      </pre>
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