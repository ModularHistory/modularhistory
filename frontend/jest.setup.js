// https://nextjs.org/docs/testing
import "@testing-library/jest-dom/extend-expect";

// mock out user auth
jest.mock("next-auth/react", () => ({
  useSession: () => [null, false],
}));

// eslint-disable-next-line
jest.mock("next/dist/client/router", () => require("next-router-mock"));
