import axiosWithoutAuth from "@/axiosWithoutAuth";
import PageHeader from "@/components/PageHeader";
import { ModuleUnion, Topic } from "@/types/modules";
import { Container } from "@mui/material";
import React, { FC, useEffect, useState } from "react";
import Carousel from "react-multi-carousel";
import "react-multi-carousel/lib/styles.css";
import ModuleUnionCard from "./cards/ModuleUnionCard";

const TodayInHistory: FC = () => {
  const [carouselData, setCarouselData] = useState<Exclude<ModuleUnion, Topic>[]>([]);
  const [moduleIndex] = useState(0);

  useEffect(() => {
    axiosWithoutAuth
      .get("/api/search/todayinhistory/")
      .then((response) => {
        setCarouselData(response.data);
      })
      .catch((error) => {
        console.error(error);
      });
  }, []);

  return(
    <Container>
      {(!carouselData && <p className="lead">Loading...</p>) ||
        (
          <div className="carousel-container" style={{ maxHeight: "40%"}}>
            <PageHeader>Today in History</PageHeader>
            <Carousel
              additionalTransfrom={0}
              arrows
              autoPlay
              autoPlaySpeed={3000}
              centerMode={false}
              className=""
              containerClass="container-with-dots"
              dotListClass=""
              draggable
              focusOnSelect={false}
              infinite
              itemClass=""
              keyBoardControl
              minimumTouchDrag={80}
              removeArrowOnDeviceType={["tablet", "mobile"]}
              renderButtonGroupOutside={false}
              renderDotsOutside={false}
              responsive={{
                desktop: {
                  breakpoint: {
                    max: 3000,
                    min: 1024
                  },
                  items: 3,
                  partialVisibilityGutter: 40
                },
                mobile: {
                  breakpoint: {
                    max: 464,
                    min: 0
                  },
                  items: 1,
                  partialVisibilityGutter: 30
                },
                tablet: {
                  breakpoint: {
                    max: 1024,
                    min: 464
                  },
                  items: 2,
                  partialVisibilityGutter: 30
                }
              }}
              showDots={false}
              sliderClass=""
              slidesToSlide={1}
              swipeable
            >
              {carouselData.map((module, index) => (
                  <ModuleUnionCard module={module} selected={index === moduleIndex} key={index}/>
              ))}
            </Carousel>
          </div>
        )
      }
      
      </Container>
  );
};

const ErrorCarousel: FC = () => (
  <div>
      <h1>Oops! No events for today.</h1>
  </div>
);

export default TodayInHistory;