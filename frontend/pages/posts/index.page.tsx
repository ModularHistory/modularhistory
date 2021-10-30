import axiosWithoutAuth from "@/axiosWithoutAuth";
import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import Pagination from "@/components/Pagination";
import Container from "@mui/material/Container";
import Paper from "@mui/material/Paper";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import { GetServerSideProps } from "next";
import { NextSeo } from "next-seo";
import { FC } from "react";

interface PostsProps {
  postsData: {
    totalPages: number;
    results: any[];
  };
}

const Posts: FC<PostsProps> = ({ postsData }: PostsProps) => {
  const posts = postsData.results || [];
  return (
    <Layout>
      <NextSeo title={"Posts"} />
      <Container>
        <PageHeader>Posts</PageHeader>
        <Pagination count={postsData["totalPages"]} />
        <TableContainer component={Paper}>
          <Table
            sx={{
              minWidth: 650,
            }}
            aria-label="posts table"
          >
            <TableHead>
              <TableRow>
                <TableCell>Title</TableCell>
                <TableCell>Content</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Author</TableCell>
                <TableCell>Parent&nbsp;Thread</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {posts.map((post) => (
                <TableRow
                  key={post.name}
                  sx={{ "&:last-child td, &:last-child th": { border: 0 } }}
                >
                  <TableCell>{post.title}</TableCell>
                  <TableCell>{post.content}</TableCell>
                  <TableCell>{post.date}</TableCell>
                  <TableCell>{post.author}</TableCell>
                  <TableCell>{post.parentThread}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        <Pagination count={postsData["totalPages"]} />
      </Container>
    </Layout>
  );
};

export default Posts;

// https://nextjs.org/docs/basic-features/data-fetching#getserversideprops-server-side-rendering
export const getServerSideProps: GetServerSideProps = async (context) => {
  let postsData = {};

  await axiosWithoutAuth
    .get("http://django:8000/api/forums/posts/", { params: context.query })
    .then((response) => {
      postsData = response.data;
    });

  return {
    props: {
      postsData,
    },
  };
};
