import Layout from "@/components/Layout";
import { Alert, AlertTitle, Button } from "@mui/material";
import Container from "@mui/material/Container";
import { Dropin } from "braintree-web-drop-in";
import DropIn from "braintree-web-drop-in-react";
import { GetServerSideProps } from "next";
import { NextSeo } from "next-seo";
import { FC, MouseEventHandler, useEffect, useRef, useState } from "react";
import axiosWithoutAuth from "../../axiosWithoutAuth";

interface DonateProps {
  clientToken: string;
}

const MakeDonationPage: FC<DonateProps> = (props: DonateProps) => {
  const [clientToken, setClientToken] = useState(props.clientToken);
  const [instance, setInstance] = useState<Dropin>();
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState(false);

  const amountRef = useRef<HTMLInputElement>(null);
  const nameRef = useRef<HTMLInputElement>(null);

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

  const makeDonation: MouseEventHandler = (e) => {
    e.preventDefault();

    async function getNonce() {
      if (!instance) return;
      const { nonce } = await instance.requestPaymentMethod();
      try {
        // Send the nonce to the server.
        const response = await axiosWithoutAuth.post("/api/donations/process/", {
          paymentMethodNonce: nonce,
          amount: amountRef.current?.value,
          name: nameRef.current?.value ?? "",
        });
        if (response.data == "OK") {
          setSuccess(true);
        } else {
          setError(true);
        }
      } catch (err) {
        console.error(err);
      }
    }

    getNonce();
  };

  return (
    <Layout>
      <NextSeo
        title="Donate"
        canonical="/donations/make"
        description={"Make a donation to support ModularHistory's educational mission."}
      />
      <Container
        sx={{
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          marginTop: "1.5rem",
          marginBottom: "2rem",
        }}
      >
        {(!clientToken && <p className="lead">Loading...</p>) || (
          <div>
            <header>
              <p className="h3">Help us keep ModularHistory running</p>
              <p>
                ModularHistory provide its content for free. If you would like to help keep
                ModularHistory afloat, you can use this form to make a donation.
              </p>
            </header>
            {(success && <SuccessMessage />) || (error && <ErrorMessage />)}
            <div className="row col-12 p-0 m-0 mt-3">
              <div className="col pl-0">
                <input
                  ref={nameRef}
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
                  ref={amountRef}
                  type="number"
                  className="form-control"
                  name="amount"
                  id="amount"
                  placeholder="Amount"
                  required
                />
              </div>
            </div>
            <DropIn
              options={{
                authorization: clientToken,
                paypal: { flow: "vault" },
                venmo: { allowNewBrowserTab: false },
              }}
              onInstance={setInstance}
            />
            <Button variant="contained" color="primary" onClick={makeDonation}>
              Make donation
            </Button>
          </div>
        )}
      </Container>
    </Layout>
  );
};

const SuccessMessage: FC = () => (
  <Alert severity="success">
    <AlertTitle>Donated Successfully.</AlertTitle>
    <strong>Thank you for your donation!</strong> Your patronage makes ModularHistory possible.
  </Alert>
);

const ErrorMessage: FC = () => (
  <Alert severity="error">
    <AlertTitle>Oops, something went wrong.</AlertTitle>
    Sorry, there were some issues with your donation.
  </Alert>
);

export default MakeDonationPage;

export const getServerSideProps: GetServerSideProps = async () => {
  let clientToken = null;
  await axiosWithoutAuth
    .get(`http://${process.env.DJANGO_HOSTNAME}:${process.env.DJANGO_PORT}/api/donations/token/`)
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
