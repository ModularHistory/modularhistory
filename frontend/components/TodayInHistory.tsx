import axiosWithoutAuth from "@/axiosWithoutAuth";
import { ModuleUnion, Topic } from "@/types/modules";
import { Card, CardContent, CardHeader, Grid, Skeleton } from "@mui/material";
import { FC, useEffect, useState } from "react";
import ModuleUnionCard from "./cards/ModuleUnionCard";

const TodayInHistory: FC = () => {
  const [items, setItems] = useState<Exclude<ModuleUnion, Topic>[]>([]);
  const [moduleIndex] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axiosWithoutAuth
      .get("/api/home/today_in_history/")
      .then((response) => {
        setItems(response.data);
        setLoading(false);
      })
      .catch((error) => {
        console.error(error);
        setLoading(false);
      });
  }, []);

  return (
    <Grid container spacing={1} justifyContent="center" alignItems="center">
      {(!items && <p className="lead">Loading...</p>) || (
        <>
          {items.length > 0 ? (
            items.map((module, index) => (
              <Grid item key={index}>
                <ModuleUnionCard module={module} selected={index === moduleIndex} key={index} />
              </Grid>
            ))
          ) : loading ? (
            <Card>
              <CardHeader title={""} />
              <CardContent>
                <Skeleton sx={{ minHeight: 200 }} />
              </CardContent>
            </Card>
          ) : null}
        </>
      )}
    </Grid>
  );
};

export default TodayInHistory;
