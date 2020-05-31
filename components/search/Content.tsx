import React from "react";
import Hit from "./hit";
import { Hits } from "react-instantsearch-dom";

const Content = () => {
  return (
    <div className="content">
      <Hits hitComponent={Hit} />
    </div>
  );
};

export default Content;