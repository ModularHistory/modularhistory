// declare module "react-braintree-fields" {
//   import { CSSProperties, ReactNode } from "react";
//
//   export class Braintree extends React.Component {
//     // derived from https://github.com/nathanstitt/react-braintree-fields/blob/master/src/braintree.jsx
//     props: {
//       children: ReactNode;
//       onAuthorizationSuccess?: () => void;
//       authorization?: string;
//       getTokenRef?: () => Promise<unknown>;
//       onValidityChange?: () => void;
//       onCardTypeChange?: () => void;
//       onError?: () => void;
//       // https://braintree.github.io/braintree-web/current/module-braintree-web_hosted-fields.html#~styleOptions
//       styles?: CSSProperties & { [key: string]: CSSProperties };
//       className?: string;
//       tagName?: string;
//     };
//   }
//
//   export class HostedField {
//     // derived from https://github.com/nathanstitt/react-braintree-fields/blob/master/src/field.jsx
//     type:
//       | "number"
//       | "expirationDate"
//       | "expirationMonth"
//       | "expirationYear"
//       | "cvv"
//       | "postalCode"
//       | "cardholderName";
//     id?: string | number;
//     placeholder?: string;
//     className?: string;
//     onCardTypeChange?: () => void;
//     onValidityChange?: () => void;
//     onNotEmpty?: () => void;
//     onFocus?: () => void;
//     onEmpty?: () => void;
//     onBlur?: () => void;
//     prefill?: string;
//   }
// }
