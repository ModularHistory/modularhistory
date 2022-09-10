import axiosWithoutAuth from "@/axiosWithoutAuth";
import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import Pagination from "@/components/Pagination";
import Citation from "@/components/sources/Citation";
import { Source } from "@/types/modules";
import Container from "@mui/material/Container";
import Paper from "@mui/material/Paper";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableRow from "@mui/material/TableRow";
import { GetServerSideProps } from "next";
import { NextSeo } from "next-seo";
import { FC } from "react";

interface SourcesProps {
  sourcesData: {
    results: Source[];
    totalPages: number;
  };
}

const Sources: FC<SourcesProps> = ({ sourcesData }: SourcesProps) => {
  const sources = sourcesData["results"] || [];

  return (
    <Layout>
      <NextSeo
        title={"Sources"}
        canonical={"/sources"}
        description={`Browse historical sources related to your topics or entities of interest.`}
      />
      <Container>
        <PageHeader>Sources</PageHeader>
        <Pagination count={sourcesData.totalPages} />
        <TableContainer component={Paper}>
          <Table
            sx={{
              minWidth: 650,
            }}
            aria-label="source table"
          >
            <TableBody>
              {sources.map((source) => (
                <TableRow key={source.slug}>
                  <TableCell scope="row">
                    <Citation html={source.citationHtml} />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        <Pagination count={sourcesData["totalPages"]} />
      </Container>
    </Layout>
  );
};

export default Sources;

// https://nextjs.org/docs/basic-features/data-fetching#getserversideprops-server-side-rendering
export const getServerSideProps: GetServerSideProps = async (context) => {
  let sourcesData = {};

  await axiosWithoutAuth
    .get(`http://${process.env.DJANGO_HOST}:${process.env.DJANGO_PORT}/api/sources/`, {
      params: context.query,
    })
    .then((response) => {
      sourcesData = response.data;
    });

  return {
    props: {
      sourcesData,
    },
  };
};
