import axiosWithoutAuth from "@/axiosWithoutAuth";
import InstantSearch, { InstantSearchProps } from "@/components/search/InstantSearch/InstantSearch";
import { FC } from "react";

type TopicsInstantSearchProps = {
  defaultValue?: number | number[] | string | string[];
} & Partial<Omit<InstantSearchProps, "defaultValue">>;

const TopicsInstantSearch: FC<TopicsInstantSearchProps> = ({
  defaultValue,
  ...instantSearchProps
}) => (
  <InstantSearch
    label={"Topics"}
    labelKey={"name"}
    defaultValue={
      defaultValue
        ? axiosWithoutAuth
            .get("/graphql/", {
              params: {
                query: `{ topics(ids: [${defaultValue}]) { id name } }`,
              },
            })
            .then(({ data: { data } }) => data.topics)
        : []
    }
    getDataForInput={(input, config) =>
      axiosWithoutAuth
        .get("/api/topics/instant_search/", {
          params: { query: input },
          ...config,
        })
        .then(({ data }) => data)
    }
    {...instantSearchProps}
  />
);

export default TopicsInstantSearch;
