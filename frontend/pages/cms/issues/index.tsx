import { Issue } from "@/interfaces";
import { Container, Table, TableBody, TableCell, TableRow } from "@material-ui/core";
import axios from "axios";
import { GetServerSideProps } from "next";
import { Session } from "next-auth";
import { getSession } from "next-auth/client";
import Link from "next/link";
import { FC } from "react";
import { CmsPage } from "..";

interface IssuesPageProps {
  session: Session;
  issues?: Issue[];
}

const IssuesPage: FC<IssuesPageProps> = (props: IssuesPageProps) => {
  console.log(props.issues[0].number);
  return (
    <CmsPage title="Issues" activeTab={1} session={props.session}>
      <Container>
        <Table>
          <TableBody>
            {(!!props.issues?.length &&
              props.issues.map((issue) => (
                <TableRow key={issue.url}>
                  <TableCell>
                    #{issue.number}: <Link href={`/cms/issues/${issue.number}`}>{issue.title}</Link>
                  </TableCell>
                </TableRow>
              ))) || <p style={{ textAlign: "center" }}>There are no open issues.</p>}
          </TableBody>
        </Table>
      </Container>
    </CmsPage>
  );
};

export default IssuesPage;

export const getServerSideProps: GetServerSideProps = async (context) => {
  const session: Session = await getSession(context);
  if (!session?.accessToken) {
    return {
      props: {
        session,
      },
    };
  }
  let issues = [];
  await axios
    .get("http://django:8000/api/cms/issues/", {
      params: context.query,
      headers: {
        Authorization: `Bearer ${session.accessToken}`,
      },
    })
    .then((response) => {
      issues = response.data.results;
    })
    .catch((error) => {
      // TODO...
      console.log(error);
    });
  return {
    props: {
      issues,
      session,
    },
  };
};
