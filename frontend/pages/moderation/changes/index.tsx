import { Change } from "@/interfaces";
import { CmsPage } from "@/pages/moderation";
import { Container, Table, TableBody, TableCell, TableRow } from "@material-ui/core";
import axios from "axios";
import { GetServerSideProps } from "next";
import { Session } from "next-auth";
import { getSession } from "next-auth/client";
import Link from "next/link";
import { FC } from "react";

interface ChangesPageProps {
  session: Session;
  changes?: Change[];
}

const ChangesPage: FC<ChangesPageProps> = (props: ChangesPageProps) => {
  return (
    <CmsPage title="Changes" activeTab={2} session={props.session}>
      <Container>
        {(!!props.changes?.length && (
          <Table>
            <TableBody>
              {props.changes.map((change) => (
                <TableRow key={change.id}>
                  <TableCell>
                    #{change.id}:{" "}
                    <Link href={`/moderation/changes/${change.id}`}>{change.description}</Link>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )) || <p style={{ textAlign: "center" }}>There are no changes to review.</p>}
      </Container>
    </CmsPage>
  );
};

export default ChangesPage;

export const getServerSideProps: GetServerSideProps = async (context) => {
  const session: Session = await getSession(context);
  if (!session?.accessToken) {
    return {
      props: {
        session,
      },
    };
  }
  let changes = [];
  await axios
    .get("http://django:8000/api/moderation/changes/", {
      params: context.query,
      headers: {
        Authorization: `Bearer ${session.accessToken}`,
      },
    })
    .then((response) => {
      changes = response.data.results;
    })
    .catch((error) => {
      // TODO...
      console.log(error);
    });
  return {
    props: {
      changes,
      session,
    },
  };
};
