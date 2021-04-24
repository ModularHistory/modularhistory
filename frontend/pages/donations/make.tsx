import Container from "@material-ui/core/Container";
import DropIn from "braintree-web-drop-in-react";
import { GetServerSideProps } from "next";
import { useRouter } from "next/router";
import { FC, useEffect, useState } from "react";
import axiosWithoutAuth from "../../axiosWithoutAuth";
import Layout from "../../components/Layout";
interface DonateProps {
  clientToken: string;
}

const Donate: FC<DonateProps> = (props: DonateProps) => {
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

  const makeDonation = (e) => {
    e.preventDefault();
    console.log("Triggered.");
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
        } else {
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
                ModularHistory provide its content for free. If you will like to help keep
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
            </div>
            <DropIn options={{ authorization: clientToken }} onInstance={(_) => setInstance(_)} />
            <button onClick={makeDonation}>Make donation</button>
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
