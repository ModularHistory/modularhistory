import Button from "@material-ui/core/Button";

import {useEffect, useState} from "react";
import {useRouter} from "next/router";

export default function SearchButton(props) {
  const router = useRouter();
  const [isLoading, setLoading] = useState(false);

  // NextJS router event subscriptions as a placeholder
  // for a more complex loading indicator
  // https://nextjs.org/docs/api-reference/next/router
  // https://github.com/vercel/next.js/blob/canary/docs/api-reference/next/router.md
  useEffect(() => {
    const setLoadingTrue = () => setLoading(true);
    const setLoadingFalse = () => setLoading(false);
    router.events.on("routeChangeStart", setLoadingTrue);
    router.events.on("routeChangeComplete", setLoadingFalse);
    router.events.on("routeChangeError", setLoadingFalse);
    return () => {
      router.events.off("routeChangeStart", setLoadingTrue);
      router.events.off("routeChangeComplete", setLoadingFalse);
      router.events.off("routeChangeError", setLoadingFalse);
    }
  }, []);

  return (
    <Button variant={"contained"}
            color={"primary"}
            size={"large"}
            disabled={isLoading}
            {...props}
    >
      {isLoading ? "Loading" : "Search"}
    </Button>
  );
}
