import { useState } from "react";
import { useRouter } from "next/router";
import MuiPagination from "@material-ui/lab/Pagination";
import { makeStyles, useMediaQuery, useTheme } from "@material-ui/core";

const useStyles = makeStyles((theme) => ({
  root: {
    // override bootstrap css
    "& button:focus": { outline: "none" },
    // center the pagination
    "& > *": {
      marginTop: theme.spacing(1),
      marginBottom: theme.spacing(1),
      justifyContent: "center",
      display: "flex",
    },
  },
}));

function usePageState(...args) {
  // This hook is used to trigger route changes
  // when a page button is clicked.

  const router = useRouter();
  const [pageNum, setPageNum] = useState(...args);
  const [loading, setLoading] = useState(false);

  const query = { ...router.query };
  const setPage = (event, newPageNum) => {
    // remove page query param when page=1
    if (newPageNum > 1) {
      query["page"] = newPageNum;
    } else {
      delete query["page"];
    }

    // `loading` is true during page transitions so the paginator
    // can be disabled until the transition completes.
    setLoading(true);
    router.push({ query }).then(() => setLoading(false));
    setPageNum(newPageNum);
  };
  return [pageNum, setPage, loading];
}

export default function Pagination({ count }) {
  const router = useRouter();
  const theme = useTheme();
  const classes = useStyles(theme);

  // increase pagination size based on viewport size
  const sibCount =
    1 +
    ["sm", "md"]
      .map((size) => useMediaQuery(theme.breakpoints.up(size)))
      .reduce((sum, current) => sum + current);

  const [pageNum, setPageNum, loading] = usePageState(Number(router.query["page"] || 1));

  // https://material-ui.com/api/pagination/
  return (
    <MuiPagination
      count={count}
      page={pageNum}
      siblingCount={sibCount}
      onChange={setPageNum}
      disabled={loading}
      variant="outlined"
      shape="rounded"
      size={sibCount > 2 ? "large" : undefined}
      className={classes.root}
    />
  );
}
