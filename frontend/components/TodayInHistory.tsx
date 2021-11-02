import axiosWithoutAuth from "@/axiosWithoutAuth";
import { ModuleUnion, Topic } from "@/types/modules";
import { Card, CardContent, CardHeader, Grid, Skeleton } from "@mui/material";
import Typography from "@mui/material/Typography";
import axios from "axios";
import Link from "next/link";
import { FC, useEffect, useState } from "react";
import ModuleUnionCard from "./cards/ModuleUnionCard";

const TodayInHistory: FC = () => {
  const [items, setItems] = useState<Exclude<ModuleUnion, Topic>[]>([]);
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
  }, [loading]);

  return (
    <>
      <div style={{ textAlign: "center" }}>
        <Typography variant="h6" gutterBottom component="div" fontWeight="bold">
          Today in History
        </Typography>
      </div>
      <Grid container spacing={1} justifyContent="center" alignItems="center">
        <>
          {items.length ? (
            items.map((module, index) => (
              <Grid item xs={12} sm={6} md={4} lg={3} xl={3} key={index}>
                <Link href={module.absoluteUrl}>
                  <a>
                    <ModuleUnionCard module={module} />
                  </a>
                </Link>
              </Grid>
            ))
          ) : loading ? (
            <Card>
              <CardHeader title={"Fetching content"} hidden />
              <CardContent>
                <Skeleton sx={{ minHeight: 200 }} />
              </CardContent>
            </Card>
          ) : (
            <p>There are no modules associated with this date.</p>
          )}
        </>
      </Grid>
    </>
  );
};

export default TodayInHistory;
