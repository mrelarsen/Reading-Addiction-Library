export const chapterColumnMetadata = {
  id: {
    key: true,
    title: "Id",
    width: "40px",
    visible: true,
    sortable: true,
  },
  name: {
    title: "Name",
    width: "*",
    visible: true,
    sortable: true,
  },
  key: {
    title: "Key",
    width: "70px",
    sortable: true,
  },
  created: {
    title: "Created",
    width: "100px",
    visible: true,
    sortable: true,
  },
  updated: {
    title: "Updated",
    width: "100px",
    sortable: true,
    displayValue: (item, col) =>
      item[col]?.toString() == "None" ? "" : item[col],
    sortValue: (item, col) =>
      (item[col]?.toString() == "None" ? "" : item[col]) || "0000-00-00",
  },
  status: {
    title: "Status",
    width: "80px",
    visible: true,
    sortable: true,
  },
};
