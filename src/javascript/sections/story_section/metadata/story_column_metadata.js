export const storyColumnMetadata = {
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
    displayValue: (item, col) => item.name || item.key,
    filterValue: (item, col) => item.name || item.key,
  },
  key: {
    title: "Key",
    width: "*",
    sortable: true,
  },
  type: {
    title: "Type",
    width: "50px",
    visible: true,
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
  rating: {
    title: "Rating",
    width: "5px",
    visible: true,
    sortable: true,
    displayValue: (item, col) => item[col] || 0.0,
  },
  tags: {
    title: "Tags",
    width: "50px",
    sortable: false,
    exclude: "nsfw",
  },
};