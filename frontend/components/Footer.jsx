import Link from "next/link";
import React from "react";

const SocialIcon = ({href, ariaLabel, spanClass}) => (
  <li style={{display: "inline-block"}}>
    <a target="_blank"
       rel="nofollow noopener"
       href={href}
       aria-label={ariaLabel}
    >
      <span className={`fab ${spanClass}`}/>
    </a>
  </li>
);

export default function Footer() {
  const socialIcons = (
    <ul className="list-social list-unstyled list-inline mx-5"
        style={{display: "inline-block"}}
    >
      <SocialIcon ariaLabel="Twitter"
                  href="https://twitter.com/modularhistory"
                  spanClass="fa-twitter"/>
      <SocialIcon ariaLabel="Facebook"
                  href="https://www.facebook.com/modularhistory"
                  spanClass={"fa-facebook-f"}/>
      <SocialIcon ariaLabel="Pinterest"
                  href="https://www.pinterest.com/modularhistory"
                  spanClass={"fa-pinterest"}/>
      <SocialIcon aria-label="YouTube"
                  href="https://www.youtube.com/channel/UCKyHzWH1tId0qvXtLbjyQ_A"
                  spanClass="fa-youtube"/>
    </ul>
  );

  return (
    <footer id="footer"
            className="page-footer font-small unique-color-dark pt-4">
      <div className="container-fluid">
        <div className="row">
          <div className="col-md-12 col-lg-12 text-center">
            <div className="footer-links mb-1"
                 style={{backgroundColor: "rgba(0,0,0,0.2)", color: "white"}}>
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

              {socialIcons}

            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
