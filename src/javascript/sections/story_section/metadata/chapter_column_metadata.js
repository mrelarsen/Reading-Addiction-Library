export const chapterColumnMetadata = {
  id: {
    key: true,
    title: "Id",
    width: "2*",
    visible: true,
    sortable: true,
  },
  name: {
    title: "Name",
    width: "10*",
    visible: true,
    sortable: true,
  },
  key: {
    title: "Key",
    width: "5*",
    sortable: true,
  },
  domain: {
    title: "Domain",
    width: "5*",
    sortable: true,
  },
  created: {
    title: "Created",
    width: "4*",
    visible: true,
    sortable: true,
  },
  updated: {
    title: "Updated",
    width: "4*",
    sortable: true,
    displayValue: (item, col) =>
      !item[col] || item[col].toString() == "None" ? "" : item[col],
    sortValue: (item, col) =>
      (item[col]?.toString() == "None" ? "" : item[col]) || "0000-00-00",
  },
  status: {
    title: "Status",
    width: "2.5*",
    visible: true,
    sortable: true,
  },
};
