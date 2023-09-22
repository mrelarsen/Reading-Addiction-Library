import { VirtualList } from "virtual-select.js";

export class VirtualTable extends Element {
  filter = "";
  data = []; // full data set
  list = []; // data to render
  idName = "";
  onRowClick;
  hideSettings = false;
  toolbar = [];
  filterMap = {};
  excludeMap = {};
  modal;
  sortOrder;
  columnMetadata;

  this(props) {
    this.data = props.data;
    this.idName = props.idName;
    this.columnMetadata = props.columnMetadata;
    this.onRowClick = props.onRowClick;
    this.hideSettings = props.hideSettings;
    this.toolbar = props.toolbar || [];
    Object.entries(this.columnMetadata).forEach((x) => {
      if (typeof x[1].filter === "string") {
        this.filterMap[x[0]] = x[1].filter;
      }
      if (typeof x[1].exclude === "string") {
        this.excludeMap[x[0]] = x[1].exclude;
      }
    });
    this.list = this.data; // render full list initially
  }

  render() {
    const ths = Object.entries(this.columnMetadata).map((x) => {
      const attributes = {};
      attributes["name"] = x[0];
      if (!x[1].visible) {
        attributes["style"] = `width: ${x[1].width}; display: none;`;
      } else {
        attributes["style"] = `width: ${x[1].width};`;
      }
      if (x[1].sortable) {
        attributes["class"] = "sortable";
      }
      return <th {...attributes}>{x[1].title}</th>;
    });
    const tableToolbar = this.hideSettings
      ? [...this.toolbar]
      : [
          <button class="table-settings dark" title="Table settings">
            <icon class="icon-settings"></icon>
          </button>,
          ...this.toolbar,
        ];
    return (
      <div id={this.idName} scrollable style="width:*;height:*;">
        <table class="virtual-table">
          <thead class="virtual-head">
            <tr>{ths}</tr>
          </thead>
          <VirtualTableBody
            id={this.idName + "_body"}
            scrollable
            class="virtual-body"
            list={this.list}
            columnMetadata={this.columnMetadata}
            onRowClick={this.onRowClick}
          />
        </table>
        {tableToolbar}
      </div>
    );
  }

  sortColumnAndUpdateList(headerElement) {
    sortColumn(headerElement, this, this.columnMetadata);
    const picker_body = this.querySelector(`#${this.idName + "_body"}`);
    const length = picker_body.totalItems();
    const start = 0;
    const where = 0;
    picker_body.oncontentrequired({ data: { length, start, where } });
  }

  updateFilter(column, filter) {
    if (filter === undefined || filter === "") {
      delete this.filterMap[column];
    } else {
      this.filterMap[column] = filter.toLowerCase();
    }
  }

  updateExclude(column, exclude) {
    if (exclude === undefined || exclude === "") {
      delete this.excludeMap[column];
    } else {
      this.excludeMap[column] = exclude.toLowerCase();
    }
  }

  updateListFilterAndExclude(column, filter, exclude) {
    this.updateFilter(column, filter);
    this.updateExclude(column, exclude);
    this.updateList();
  }

  updateListFiltersAndExcludes(filters, excludes) {
    Object.entries(filters).forEach((filter) => {
      this.updateFilter(filter[0], filter[1]);
    });
    Object.entries(excludes).forEach((exclude) => {
      this.updateExclude(exclude[0], exclude[1]);
    });
    this.updateList();
  }

  setVisibleColumns(visible) {
    Object.entries(this.columnMetadata).forEach(
      (x) => (x[1].visible = visible.includes(x[0]))
    );
    this.patch(this.render());
  }

  overrideRow(item) {
    const dataRow = this.data.find((row) => row.id === item.id);
    if (dataRow) {
      Object.assign(dataRow, item);
      this.updateList();
    }
  }

  deleteRows(rowIds) {
    this.data = this.data.filter((x) => !rowIds.includes(x.id));
    this.updateList();
  }

  deleteRow(rowId) {
    this.data = this.data.filter((x) => x.id !== rowId);
    this.updateList();
  }

  updateList() {
    const filterList = Object.entries(this.filterMap);
    const excludeList = Object.entries(this.excludeMap);
    this.componentUpdate({
      list: this.data
        .filter(
          (record) =>
            filterList.every(this.include(record)) &&
            !excludeList.some(this.include(record))
        )
        .sort(this.sortOrder),
    });
  }

  include(record) {
    return (x) => {
      let value = record[x[0]];
      if (this.columnMetadata[x[0]].filterValue) {
        value = this.columnMetadata[x[0]].filterValue(record, x[0]);
      } else if (this.columnMetadata[x[0]].displayValue) {
        value = this.columnMetadata[x[0]].displayValue(record, x[0]);
      }
      const terms = x[1]?.split(" ") || [];
      for (const term of terms) {
        if (!value?.toString().toLowerCase().includes(term)) {
          return false;
        }
      }
      return true;
    };
  }

  sortList(sortOrder) {
    this.sortOrder = sortOrder;
    this.updateList();
  }

  "on click at .table-settings"(_, __) {
    Window.this.modal({
      url: __DIR__ + "./column_settings_modal.htm",
      alignment: -5,
      width: 400,
      height: Object.keys(this.columnMetadata).length * 27 + 65,
      caption: "Settings",
      parameters: {
        metadata: Object.entries(this.columnMetadata),
        visible: Object.entries(this.columnMetadata)
          .filter((x) => x[1].visible)
          .map((x) => x[0]),
        setVisibleColumns: (visible) => this.setVisibleColumns(visible),
        filters: this.filterMap,
        excludes: this.excludeMap,
        setColumnFilters: (filters, excludes) =>
          this.updateListFiltersAndExcludes(filters, excludes),
      },
    });
  }

  "on click at th"(event, element) {
    if (event.ctrlKey) {
      this.updateListFilterAndExclude(element["name"], "", "");
    }
    if (event.shiftKey) {
      Window.this.modal({
        url: __DIR__ + "./filter_modal.htm",
        alignment: -5,
        width: 250,
        height: 80,
        parameters: {
          title: element["name"],
          filter: this.filterMap[element["name"]],
          exclude: this.excludeMap[element["name"]],
          setFilter: (filter, exclude) =>
            this.updateListFilterAndExclude(element["name"], filter, exclude),
        },
      });
    }
    if (
      element.classList.contains("sortable") &&
      !event.ctrlKey &&
      !event.shiftKey
    ) {
      this.sortColumnAndUpdateList(element);
    }
  }
}

// table body with virtual data source
class VirtualTableBody extends VirtualList {
  list; // array of items
  onRowClick;
  selectedRows = [];
  lastClickedRow;
  columnMetadata;

  this(props) {
    this.list = props.list;
    this.columnMetadata = props.columnMetadata;
    this.onRowClick = props.onRowClick;
  }

  itemAt(at) {
    return this.list[at];
  }

  totalItems() {
    return this.list.length;
  }

  indexOf(item) {
    return this.list.indexOf(item);
  }

  // overridable
  renderItem(item, isCurrent, isSelected) {
    const key = Object.entries(this.columnMetadata).find((x) => x[1].key);
    const trAttributes = {};
    if (isSelected) {
      trAttributes["class"] = "selected";
    }
    const tds = Object.entries(this.columnMetadata).map((x) => {
      const tdAttribute = {};
      tdAttribute[x[0]] = true;
      if (!x[1].visible) {
        tdAttribute["style"] = "display: none;";
      }
      let content = this.columnMetadata[x[0]].displayValue?.(item, x[0]);
      content = content != undefined ? content : item[x[0]];
      return <td {...tdAttribute}>{content}</td>;
    });
    return (
      <tr {...trAttributes} key={item[key[0]]}>
        {tds}
      </tr>
    );
  }

  renderList(
    items // overridable
  ) {
    return (
      <tbody styleset={__DIR__ + "virtual-table.css#tbody"}>{items}</tbody>
    );
  }

  "on click at tr"(evt, rowElement) {
    const rowItem = this.itemOfElement(rowElement);
    if (!rowItem) {
      return;
    }
    const rowId = rowItem.id;
    const listItems = [];
    if (evt.ctrlKey) {
      listItems.push(rowItem);
    }
    if (evt.shiftKey && this.currentItem) {
      const lastClickIndex = this.list.findIndex(
        (x) => x.id == this.currentItem.id
      );
      const clickIndex = this.list.findIndex((x) => x.id == rowId);
      if (clickIndex > lastClickIndex) {
        listItems.push(...this.list.slice(lastClickIndex + 1, clickIndex + 1));
      } else if (clickIndex < lastClickIndex) {
        listItems.push(...this.list.slice(clickIndex, lastClickIndex));
      }
    }
    let selected = [rowItem];
    if (listItems.length !== 0) {
      selected = [...(this.selectedItems || selected)];
      listItems.forEach((listItem) => {
        if (!selected.includes(listItem)) {
          selected.push(listItem);
        }
      });
    }

    this.componentUpdate({
      currentItem: this.itemOfElement(rowElement),
      selectedItems: selected,
    });
    if (typeof this.onRowClick === "function") {
      this.onRowClick(this.currentItem, rowElement, this.selectedItems);
    }
  }
}

function sortColumn(headerElement, table, metadata) {
  var name = headerElement["name"];
  var order = headerElement["order"];

  function cmpascend(a, b) {
    return cmp(a, b, -1);
  }
  function cmpdescend(a, b) {
    return cmp(a, b);
  }
  function cmp(a, b, dir = 1) {
    const aValue = getValue(a, name);
    const bValue = getValue(b, name);
    if (aValue < bValue) return dir;
    else if (aValue > bValue) return -dir;
    return 0;
  }
  function getValue(item, col) {
    let value = item[col];
    if (metadata) {
      if (metadata[col].sortValue) {
        value = metadata[col].sortValue(item, col);
      } else if (metadata[col].displayValue) {
        value = metadata[col].displayValue(item, col);
      }
    }
    return typeof value === "string" ? value.toLowerCase() : value;
  }

  if (order == "ascend") {
    headerElement["order"] = "descend";
    table.sortList(cmpdescend);
  } else if (order == "descend") {
    headerElement["order"] = "ascend";
    table.sortList(cmpascend);
  } else {
    // the column was not ordered before, remove @order from other columns
    const psort = headerElement.parentElement.querySelector("th[order]");
    if (psort) psort["order"] = undefined; // remove the attribute from previously ordered sibling
    // set this column as ascend order:
    headerElement["order"] = "ascend";
    table.sortList(cmpascend);
  }
}
