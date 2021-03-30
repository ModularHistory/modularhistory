import Link from "next/link";
import React from "react";

export default function Footer() {
  return (
    <footer id="footer" className="page-footer font-small unique-color-dark pt-4">
      <div className="container-fluid">
        <ul className="list-unstyled list-inline text-center py-2">
          <li className="list-inline-item">
            <a href="https://www.patreon.com/modularhistory" className="btn btn-outline-white">
              Support on Patreon
            </a>
          </li>
        </ul>

        <div className="row">
          <div className="col-md-12 col-lg-12 text-center">
            <div className="footer-links mb-1" style={{ backgroundColor: "rgba(0,0,0,0.2)" }}>
              <span className="text-center py-3 mx-5">&copy; 2020 ModularHistory, Inc.</span>

              <Link href="/about">
                <a>About ModularHistory</a>
              </Link>

              <Link href="/privacy">
                <a>Privacy Policy</a>
              </Link>

              <Link href="/terms">
                <a>Terms of Use</a>
              </Link>

              <ul
                className="list-social list-unstyled list-inline mx-5"
                style={{ display: "inline-block" }}
              >
                <li style={{ display: "inline-block" }}>
                  <a
                    href="https://twitter.com/modularhistory"
                    rel="nofollow noopener"
                    target="_blank"
                    aria-label="Twitter"
                  >
                    <span className="fab fa-twitter" />
                  </a>
                </li>

                <li style={{ display: "inline-block" }}>
                  <a
                    href="https://www.facebook.com/modularhistory"
                    rel="nofollow noopener"
                    target="_blank"
                    aria-label="Facebook"
                  >
                    <span className="fab fa-facebook-f" />
                  </a>
                </li>

                <li style={{ display: "inline-block" }}>
                  <a
                    href="https://www.pinterest.com/modularhistory"
                    rel="nofollow noopener"
                    target="_blank"
                    aria-label="Pinterest"
                  >
                    <span className="fab fa-pinterest" />
                  </a>
                </li>

                <li style={{ display: "inline-block" }}>
                  <a
                    href="https://www.youtube.com/c/modularhistory"
                    rel="nofollow noopener"
                    target="_blank"
                    aria-label="YouTube"
                  >
                    <span className="fab fa-youtube-f" />
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
