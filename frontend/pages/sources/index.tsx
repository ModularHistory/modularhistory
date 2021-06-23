import axiosWithoutAuth from "@/axiosWithoutAuth";
import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import Pagination from "@/components/Pagination";
import { Source } from "@/interfaces";
import Container from "@material-ui/core/Container";
import Paper from "@material-ui/core/Paper";
import { makeStyles } from "@material-ui/core/styles";
import Table from "@material-ui/core/Table";
import TableBody from "@material-ui/core/TableBody";
import TableCell from "@material-ui/core/TableCell";
import TableContainer from "@material-ui/core/TableContainer";
import TableRow from "@material-ui/core/TableRow";
import { GetServerSideProps } from "next";
import { FC } from "react";

const useStyles = makeStyles({
  table: {
    minWidth: 650,
  },
});

interface SourcesProps {
  sourcesData: {
    results: Source[];
  };
}

const Sources: FC<SourcesProps> = ({ sourcesData }: SourcesProps) => {
  const sources = sourcesData["results"] || [];
  const classes = useStyles();

  return (
    <Layout title={"Sources"}>
      <Container>
        <PageHeader>Sources</PageHeader>
        <Pagination count={sourcesData["total_pages"]} />
        <TableContainer component={Paper}>
          <Table className={classes.table} aria-label="source table">
            <TableBody>
              {sources.map((source) => (
                <TableRow key={source.slug}>
                  <TableCell scope="row">
                    <span dangerouslySetInnerHTML={{ __html: source.citationHtml }} />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        <Pagination count={sourcesData["total_pages"]} />
      </Container>
    </Layout>
  );
};

export default Sources;

// https://nextjs.org/docs/basic-features/data-fetching#getserversideprops-server-side-rendering
export const getServerSideProps: GetServerSideProps = async (context) => {
  let sourcesData = {};

  await axiosWithoutAuth
    .get("http://django:8000/api/sources/", { params: context.query })
    .then((response) => {
      sourcesData = response.data;
    });

  return {
    props: {
      sourcesData,
    },
  };
};
