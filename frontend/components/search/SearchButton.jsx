import Button from "@material-ui/core/Button";

import {useEffect, useContext} from "react";
import {useRouter} from "next/router";

import PageTransitionContext from "../PageTransitionContext";

export default function SearchButton(props) {
  // A button with "Search" label.
  // The label changes to "Loading" when a page transition occurs.
  // All props are passed along to the Mui Button.

  const router = useRouter();
  const isLoading = useContext(PageTransitionContext);

  // asynchronously download JS for the search page
  useEffect(() => {
    router.prefetch("/search");
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
