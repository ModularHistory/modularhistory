describe("The Home Page", () => {
  beforeEach(() => {
    cy.visit("/");
  });

  it("Contains important elements", () => {
    cy.get("#global-nav").contains("Sign in");
  });

  it("Allows basic search", () => {
    cy.intercept("**/search.json*", {
      fixture: "emptySearchResults.json",
      delay: 500,
    });

    const searchString = "test_string_for_search_input";
    cy.get('[data-cy="query"]').as("queryInput");
    cy.get('[data-cy="searchButton"]').as("searchButton");

    const checkAndReturn = () => {
      cy.get("@searchButton").should("have.attr", "disabled", "disabled").contains("Loading");

      cy.url().should("include", "/search").and("include", searchString);

      cy.get('[data-cy="brand"]').click();
      cy.url().should("eq", Cypress.config().baseUrl);
    };

    cy.get("@queryInput").type(searchString + "\n");
    checkAndReturn();

    cy.get("@queryInput").type(searchString);
    cy.get("@searchButton").click();
    checkAndReturn();
  });

  it("Does not have bad links", () => {
    const allLinks = [];

    cy.get("a[href]")
      .each((element) => {
        const href = element.attr("href");
        // remove cross-domain links
        if (Cypress.minimatch(href, "/**")) {
          allLinks.push(element.attr("href"));
        }
      })
      .then(() => {
        allLinks.forEach(cy.visit);
      });
  });
});
