import { render } from "@testing-library/react";
import React from "react";
import Home from "../index.page";

describe("Home", () => {
  it("renders without exceptions", () => {
    render(<Home />);
  });
});
