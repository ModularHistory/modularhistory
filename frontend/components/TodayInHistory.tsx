import axiosWithoutAuth from "@/axiosWithoutAuth";
import { ModuleUnion, Topic } from "@/types/modules";
import { Card, CardContent, Grid, Skeleton } from "@mui/material";
import Typography from "@mui/material/Typography";
import { FC, useEffect, useState } from "react";
import ModuleUnionCard from "./cards/ModuleUnionCard";

const TodayInHistory: FC = () => {
  const [items, setItems] = useState<Exclude<ModuleUnion, Topic>[]>([]);
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
  }, [loading]);

  return (
    <>
      {items.length && (
        <div style={{ textAlign: "center" }}>
          <Typography variant="h6" gutterBottom component="div" fontWeight="bold">
            Today in History
          </Typography>
        </div>
      )}
      <Grid container spacing={1} justifyContent="center" alignItems="center">
        {!items.length && !loading ? null : (
          <>
            {loading ? (
              <Grid item>
                <Card>
                  <CardContent>
                    <Skeleton sx={{ minHeight: 200 }} />
                  </CardContent>
                </Card>
              </Grid>
            ) : (
              <>
                {items.map((module, index) => (
                  <Grid item key={index}>
                    <ModuleUnionCard module={module} key={index} />
                  </Grid>
                ))}
              </>
            )}
          </>
        )}
      </Grid>
    </>
  );
};

export default TodayInHistory;
