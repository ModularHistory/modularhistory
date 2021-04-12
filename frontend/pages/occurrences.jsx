import Layout from "../components/Layout";
import {useRouter} from "next/router";
import {useEffect} from "react";

export default function Occurrences() {
  const router = useRouter();
  useEffect(() => {
    router.push({
      pathname: "/search",
      query: {content_types: "occurrences.occurrence"},
    })
  }, []);

  return <Layout title={"Occurrences"}/>
}