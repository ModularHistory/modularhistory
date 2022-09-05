/*
  Based on https://github.com/nathanstitt/react-braintree-fields/blob/master/demo/demo-functional.jsx
*/

import Layout from "@/components/Layout";
import Container from "@mui/material/Container";
import $ from "jquery";
import { GetServerSideProps } from "next";
import { NextSeo } from "next-seo";
import { FC, MouseEventHandler, useRef, useState } from "react";
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import { Braintree, HostedField } from "react-braintree-fields";
import axiosWithoutAuth from "../../axiosWithoutAuth";

interface DonateProps {
  clientToken: string;
}

const Donate: FC<DonateProps> = ({ clientToken }: DonateProps) => {
  // Set the initial value of tokenize to be an anonymous function that returns null.
  // Subsequently, tokenize is set by the Braintree drop-in component.
  const [tokenize, setTokenizeFunc] = useState(() => {
    return () => Promise.reject(new Error("tokenize function is not yet available"));
  });
  const [cardType, _setCardType] = useState("");
  const [error, setError] = useState("");
  const [token, setToken] = useState(null);
  const [focusedFieldName, _setFocusedField] = useState("");
  const numberField = useRef();
  const cvvField = useRef();
  const cardholderNameField = useRef();

  const _getToken = () => {
    tokenize().then(setToken).catch(handleError);
  };
  const handleError = (newError: Error) => {
    setError(newError.message || String(newError));
  };

  // TODO
  // const onAuthorizationSuccess = () => {
  //   console.log("Authorization succeeded.");
  //   numberField.current.focus();
  // };
  // const onDataCollectorInstanceReady = (collector) => {
  //   // DO SOMETHING with Braintree collector as needed
  // };
  // const onFieldBlur = (field, event) => setFocusedField("");
  // const onFieldFocus = (field, event) => setFocusedField(event.emittedBy);
  // const onCardTypeChange = ({ cards }) => {
  //   if (cards.length === 1) {
  //     const [card] = cards;
  //     setCardType(card.type);
  //     if (card.code && card.code.name) {
  //       cvvField.current.setPlaceholder(card.code.name);
  //     } else {
  //       cvvField.current.setPlaceholder("CVV");
  //     }
  //   } else {
  //     setCardType("");
  //     cvvField.current.setPlaceholder("CVV");
  //   }
  // };

  const makeDonation: MouseEventHandler = async (e) => {
    e.preventDefault();
    try {
      // Set donor name in localstorage.
      // window.localStorage.setItem("donor", $("#name").val());

      // Send the nonce to the server.
      const response = await axiosWithoutAuth.post(
        `http://django:${process.env.DJANGO_PORT}/api/donations/process/`,
        {
          paymentMethodNonce: token,
          amount: $("#amount").val(),
          name: $("#name").val(),
        }
      );
      if (response.data == "OK") {
        location.href = "/donations/success";
      } else {
        location.href = "/donations/error";
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <Layout>
      <NextSeo
        title="Donate"
        canonical="/donations/make"
        description={"Make a donation to support ModularHistory's educational mission."}
      />
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
            <Braintree
              className="demo"
              authorization={clientToken}
              // onAuthorizationSuccess={onAuthorizationSuccess}
              // onDataCollectorInstanceReady={onDataCollectorInstanceReady}
              onError={handleError}
              // onCardTypeChange={onCardTypeChange}
              getNonceRef={(ref:any) => setTokenizeFunc(() => ref)} // prettier-ignore
              styles={{
                input: {
                  "font-size": "inherit",
                },
                ":focus": {
                  color: "blue",
                },
              }}
            >
              <div className="form-container">
                {error && <p className="error">{error}</p>}
                <div className="row col-12 p-0 m-0 mt-3">
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
                <div className="row col-12 p-0 m-0 mt-3">
                  <p>Number:</p>
                  <HostedField
                    type="number"
                    className={
                      focusedFieldName === "number" ? "focused form-control" : "form-control"
                    }
                    // onBlur={onFieldBlur}
                    // onFocus={onFieldFocus}
                    placeholder="4111 1111 1111 1111"
                    ref={numberField}
                  />
                  {cardType && <p>Card type: {cardType}</p>}
                  Name:
                  <HostedField
                    type="cardholderName"
                    className={
                      focusedFieldName === "cardholderName"
                        ? "focused form-control"
                        : "form-control"
                    }
                    // onBlur={onFieldBlur}
                    // onFocus={onFieldFocus}
                    placeholder="Name on Card"
                    ref={cardholderNameField}
                  />
                  Date:
                  <HostedField
                    type="expirationDate"
                    // onBlur={onFieldBlur}
                    // onFocus={onFieldFocus}
                    className={
                      focusedFieldName === "expirationDate"
                        ? "focused form-control"
                        : "form-control"
                    }
                  />
                  Month:
                  <HostedField
                    type="expirationMonth"
                    className={
                      focusedFieldName === "expirationDate"
                        ? "focused form-control"
                        : "form-control"
                    }
                  />
                  Year:
                  <HostedField
                    type="expirationYear"
                    className={
                      focusedFieldName === "expirationDate"
                        ? "focused form-control"
                        : "form-control"
                    }
                  />
                  CVV:
                  <HostedField
                    type="cvv"
                    placeholder="CVV"
                    ref={cvvField}
                    className={
                      focusedFieldName === "expirationDate"
                        ? "focused form-control"
                        : "form-control"
                    }
                  />
                  Zip:
                  <HostedField
                    type="postalCode"
                    className={
                      focusedFieldName === "expirationDate"
                        ? "focused form-control"
                        : "form-control"
                    }
                  />
                </div>
              </div>
            </Braintree>
            <div>
              <input
                id="button-pay"
                className="mt-5 m-auto"
                type="submit"
                value="Make donation"
                onClick={makeDonation}
              />
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
    .get(`http://django:${process.env.DJANGO_PORT}/api/donations/token/`)
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
