import entities from "@/components/entities/admin";
import propositions from "@/components/propositions/admin";
import sources from "@/components/sources/admin";
import images from "@/components/images/admin";
import topics from "@/components/topics/admin";
import drfProvider from "ra-data-django-rest-framework";
import { FC } from "react";
import { Admin, Resource } from "react-admin";

const dataProvider = drfProvider("/api");

const DataAdmin: FC = () => {
  if (!dataProvider) {
    return <div>Loading...</div>;
  } else {
    return (
      <Admin dataProvider={dataProvider}>
        <Resource name="propositions" {...propositions} />
        <Resource name="entities" {...entities} />
        <Resource name="sources" {...sources} />
        <Resource name="topics" {...topics} />
        <Resource name="images" {...images} />
      </Admin>
    );
  }
};

export default DataAdmin;
