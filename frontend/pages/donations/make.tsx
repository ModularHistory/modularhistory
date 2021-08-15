import Layout from "@/components/Layout";
import { Button } from "@material-ui/core";
import Container from "@material-ui/core/Container";
import { makeStyles } from "@material-ui/styles";
import DropIn from "braintree-web-drop-in-react";
import { GetServerSideProps } from "next";
import Link from "next/link";
import { useRouter } from "next/router";
import { FC, useEffect, useState } from "react";
import axiosWithoutAuth from "../../axiosWithoutAuth";

const useStyles = makeStyles({
  root: {
    height: "100%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    marginTop: "1.5rem",
    marginBottom: "2rem",
  },
});
interface DonateProps {
  clientToken: string;
}

const Donate: FC<DonateProps> = (props: DonateProps) => {
  const classes = useStyles();
  const [clientToken, setClientToken] = useState(props.clientToken);
  const [instance, setInstance] = useState(null);
  const router = useRouter();
  useEffect(() => {
    async function getClientToken() {
      await axiosWithoutAuth
        .get("/api/donations/token/")
        .then((response) => {
          setClientToken(response.data);
        })
        .catch((error) => {
          console.error(error);
        });
      return {
        props: {
          clientToken,
        },
      };
    }
    getClientToken();
  });

  function SuccessMessage() {
    return (
      <div>
        <div className="pt-5">
          <p className="h1 mt-5">Donated Successfully.</p>
          <div className="mt-3 pt-5 h4">
            Thank you for your donation! Your patronage makes ModularHistory possible.
          </div>
          <div>
            <Link href={"/home"}>
              <Button variant="contained" color="primary">
                Return Home
              </Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  function ErrorMessage() {
    return (
      <div className={classes.root}>
        <div className="pt-5">
          <p className="h1 mt-5">Oops, something went wrong.</p>
          <div className="mt-3 pt-5 h4">Sorry, there were some issues with your donation.</div>
        </div>
      </div>
    );
  }

  const makeDonation = (e) => {
    e.preventDefault();
    async function getNonce() {
      const { nonce } = await instance.requestPaymentMethod();
      try {
        // Send the nonce to the server.
        const response = await axiosWithoutAuth.post("/api/donations/process/", {
          paymentMethodNonce: nonce,
          amount: $("#amount").val(),
          name: $("#name").val(),
        });
        if (response.data == "OK") {
          router.push("/donations/success");
          // return <SuccessMessage />;
        } else {
          // return <ErrorMessage />;
          router.push("/donations/error");
        }
      } catch (err) {
        console.error(err);
      }
    }
    getNonce();
  };

  return (
    <Layout title="Donate">
      <Container>
        {(!clientToken && <p className="lead">Loading...</p>) || (
          <div>
            <header>
              <p className="h3">Help us keep ModularHistory running</p>
              <p>
                ModularHistory provide its content for free. If you would like to help keep
                ModularHistory afloat, you can use this form to make a donation.
              </p>
            </header>
            <div className="row col-12 p-0 m-0 mt-3">
              <div className="col pl-0">
                <input
                  type="text"
                  className="form-control"
                  name="name"
                  id="name"
                  placeholder="Name"
                  required
                />
              </div>
              <div className="col pr-0">
                <input
                  type="number"
                  className="form-control"
                  name="amount"
                  id="amount"
                  placeholder="Amount"
                  required
                />
              </div>
              <DropIn options={{ authorization: clientToken }} onInstance={(_) => setInstance(_)} />
              <Button variant="contained" color="primary" onClick={makeDonation}>
                Make donation
              </Button>
            </div>
          </div>
        )}
      </Container>
    </Layout>
  );
};

export default Donate;

export const getServerSideProps: GetServerSideProps = async () => {
  let clientToken = null;
  await axiosWithoutAuth
    .get("http://django:8000/api/donations/token/")
    .then((response) => {
      clientToken = response.data;
    })
    .catch((error) => {
      console.error(error);
    });
  return {
    props: {
      clientToken,
    },
  };
};
