import Layout from "@/components/Layout";
import { Button } from "@material-ui/core";
import Container from "@material-ui/core/Container";
import DropIn from "braintree-web-drop-in-react";
import { GetServerSideProps } from "next";
import { useRouter } from "next/router";
import { FC, MouseEventHandler, useEffect, useRef, useState } from "react";
import axiosWithoutAuth from "../../axiosWithoutAuth";

interface DonateProps {
  clientToken: string;
}

const Donate: FC<DonateProps> = (props: DonateProps) => {
  const [clientToken, setClientToken] = useState(props.clientToken);
  const [instance, setInstance] = useState<any>();
  const router = useRouter();

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
      const { nonce } = await instance.requestPaymentMethod();
      try {
        // Send the nonce to the server.
        const response = await axiosWithoutAuth.post("/api/donations/process/", {
          paymentMethodNonce: nonce,
          amount: amountRef.current?.value,
          name: nameRef.current?.value ?? "",
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
            <DropIn options={{ authorization: clientToken }} onInstance={setInstance} />
            <Button variant="contained" color="primary" onClick={makeDonation}>
              Make donation
            </Button>
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
