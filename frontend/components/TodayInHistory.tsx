import axiosWithoutAuth from "@/axiosWithoutAuth";
import { ModuleUnion, Topic } from "@/types/modules";
import { Skeleton } from "@mui/lab";
import { Card, CardContent, CardHeader, Grid } from "@mui/material";
import axios from "axios";
import { FC, useEffect, useState } from "react";
import ModuleUnionCard from "./cards/ModuleUnionCard";

const TodayInHistory: FC = () => {
  const [items, setItems] = useState<Exclude<ModuleUnion, Topic>[]>([]);
  const [moduleIndex] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const cancelTokenSource = axios.CancelToken.source();
    axiosWithoutAuth
      .get("/api/home/today_in_history/", { cancelToken: cancelTokenSource.token })
      .then((response) => {
        setItems(response.data);
        setLoading(false);
      })
      .catch((error) => {
        if (axios.isCancel(error)) return;
        console.error(error);
        setLoading(false);
      });
    return () => {
      cancelTokenSource.cancel("component unmounted");
    };
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
