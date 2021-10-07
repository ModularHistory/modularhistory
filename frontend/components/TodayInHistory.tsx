import axiosWithoutAuth from "@/axiosWithoutAuth";
import PageHeader from "@/components/PageHeader";
import { ModuleUnion, Topic } from "@/types/modules";
import { Skeleton } from "@mui/lab";
import { Card, CardContent, CardHeader, Container } from "@mui/material";
import React, { FC, useEffect, useState } from "react";
import Carousel from "react-multi-carousel";
import "react-multi-carousel/lib/styles.css";
import ModuleUnionCard from "./cards/ModuleUnionCard";

const TodayInHistory: FC = () => {
  const [carouselData, setCarouselData] = useState<Exclude<ModuleUnion, Topic>[]>([]);
  const [moduleIndex] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axiosWithoutAuth
      .get("/api/search/todayinhistory/")
      .then((response) => {
        setCarouselData(response.data);
        setLoading(false);
      })
      .catch((error) => {
        console.error(error);
        setLoading(false);
      });
  }, []);

  return (
    <Container>
      {(!carouselData && <p className="lead">Loading...</p>) || (
        <div className="carousel-container" style={{ maxHeight: "40%" }}>
          <PageHeader>Today in History</PageHeader>

          <Carousel
            additionalTransfrom={0}
            arrows={carouselData.length > 1}
            autoPlay={carouselData.length > 1}
            autoPlaySpeed={3000}
            centerMode={false}
            containerClass="container-with-dots"
            focusOnSelect={false}
            infinite
            keyBoardControl
            minimumTouchDrag={80}
            removeArrowOnDeviceType={["tablet", "mobile"]}
            renderButtonGroupOutside={false}
            renderDotsOutside={false}
            responsive={{
              desktop: {
                breakpoint: {
                  max: 3000,
                  min: 1024,
                },
                items: 1,
                partialVisibilityGutter: 40,
              },
              mobile: {
                breakpoint: {
                  max: 464,
                  min: 0,
                },
                items: 1,
                partialVisibilityGutter: 30,
              },
              tablet: {
                breakpoint: {
                  max: 1024,
                  min: 464,
                },
                items: 2,
                partialVisibilityGutter: 30,
              },
            }}
            showDots={false}
            slidesToSlide={1}
            swipeable
          >
            {carouselData.length > 0 ? (
              carouselData.map((module, index) => (
                <ModuleUnionCard module={module} selected={index === moduleIndex} key={index} />
              ))
            ) : loading ? (
              <Card>
                <CardHeader title={""} />
                <CardContent>
                  <Skeleton sx={{ minHeight: 200 }} />
                </CardContent>
              </Card>
            ) : (
              <Card raised>
                <CardHeader title={"No historical events found for today's date"} />
                <CardContent></CardContent>
              </Card>
            )}
          </Carousel>
        </div>
      )}
    </Container>
  );
};

export default TodayInHistory;
