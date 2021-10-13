import axiosWithoutAuth from "@/axiosWithoutAuth";
import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import Pagination from "@/components/Pagination";
import { Button, TextField } from "@mui/material";
import Container from "@mui/material/Container";
import Grid from "@mui/material/Grid";
import { GetServerSideProps } from "next";
import { useRouter } from "next/router";
import { FC, useRef } from "react";

interface PostsProps {
  postsData: {
    totalPages: number;
    results: any[];
  };
}

const Entities: FC<PostsProps> = ({ postsData }: PostsProps) => {
  const posts = postsData.results || [];
  // const entityCards = entities.map((post) => (
  //   <Grid item key={post.slug} xs={6} sm={4} md={3}>
  //     <Link href={`/entities/${post.slug}`}>
  //       <a>
  //         <ModuleUnionCard module={post} />
  //       </a>
  //     </Link>
  //   </Grid>
  // ));

  const titleInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();
  const createNewPost = () => {
    axiosWithoutAuth
      .post("/api/forums/posts/", {
        content: "New post from button",
        title: titleInputRef.current?.value || "default title",
        date: new Date().toISOString(),
        author: 42,
        parentThread: 1,
      })
      .then(router.reload)
      .catch(console.error);
  };

  return (
    <Layout title={"Posts"}>
      <Container>
        <PageHeader>Posts</PageHeader>
        <TextField inputRef={titleInputRef} />
        <Button onClick={createNewPost} />
        <Pagination count={postsData["totalPages"]} />
        <Grid container spacing={2}>
          <pre>{JSON.stringify(posts, null, 4)}</pre>
        </Grid>
        <Pagination count={postsData["totalPages"]} />
      </Container>
    </Layout>
  );
};

export default Entities;

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
