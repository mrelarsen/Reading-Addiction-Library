import { VirtualList } from "virtual-select.js";

export class VirtualTable extends Element {
	filter = "";
	data = []; // full data set
	list = []; // data to render
	idName = "";
	onRowClick;
	hideSettings = false;
	toolbar = [];
	filterMap;
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
		if (!this.filterMap) {
			this.filterMap = {};
			Object.entries(this.columnMetadata).forEach((x) => {
				if (typeof x[1].filter === "string") {
					this.filterMap[x[0]] = x[1].filter;
				}
				if (typeof x[1].exclude === "string") {
					this.excludeMap[x[0]] = x[1].exclude;
				}
			});
		}
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

	sortColumnAndUpdateList(headerElement, order = undefined) {
		sortColumn(headerElement, this, this.columnMetadata, order);
	}

	updateMap(map, key, value) {
		if (!value) {
			delete map[key];
		} else {
			map[key] = value.toLowerCase();
		}
		return map;
	}

	updateListFilterAndExclude(column, filter, exclude) {
		const filterMap = this.updateMap({...this.filterMap}, column, filter);
		const excludeMap = this.updateMap({...this.excludeMap}, column, exclude);
		const list = this.getModdedList(null, filterMap, excludeMap, null);
		this.componentUpdate({
			filterMap,
			excludeMap,
			list,
		});
	}

	updateListFiltersAndExcludes(filters, excludes) {
		const filterMap = Object.entries(filters).reduce((acc, c) => !c[1] ? acc : ({...acc, [c[0]]: c[1].toLowerCase()}), {});
		const excludeMap = Object.entries(excludes).reduce((acc, c) => !c[1] ? acc : ({...acc, [c[0]]: c[1].toLowerCase()}), {});
		const list = this.getModdedList(null, filterMap, excludeMap);
		this.componentUpdate({
			list,
			filterMap,
			excludeMap
		});
	}

	setVisibleColumns(visible) {
		const columnMetadata = Object.entries(this.columnMetadata)
			.reduce((acc, c) => ({...acc, [c[0]]: {...c[1], visible: visible.includes(c[0])}}), {});
		this.componentUpdate({
			columnMetadata,
		});
	}

	overrideRow(item) {
		const dataRowIdx = this.data.findIndex(x => x.id === item.id);
		const data = [...this.data.slice(0, dataRowIdx), {...this.data[dataRowIdx], ...item}, ...this.data.slice(dataRowIdx + 1)];
		const list = this.getModdedList(data);
		this.componentUpdate({
			data,
			list,
		});
	}

	deleteRows(rowIds) {
		const data = this.data.filter((x) => !rowIds.includes(x.id));
		const list = this.getModdedList(data);
		this.componentUpdate({
			data,
			list,
		});
	}

	deleteRow(rowId) {
		const data = this.data.filter((x) => x.id !== rowId);
		const list = this.getModdedList(data);
		this.componentUpdate({
			data,
			list,
		});
	}

	getModdedList(data, filterMap, excludeMap, sortOrder) {
		const filterList = Object.entries(filterMap || this.filterMap);
		const excludeList = Object.entries(excludeMap || this.excludeMap);
		const content = data || this.data;
		return content.filter(
				(record) =>
					filterList.every(this.include(record)) &&
					!excludeList.some(this.include(record))
			)
			.sort(sortOrder || this.sortOrder);
	}

	updateList() {
		const list = this.getModdedList();
		this.componentUpdate({
			list,
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
		const list = this.getModdedList(null, null, null, sortOrder);
		this.componentUpdate({
			sortOrder,
			list,
		});
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
						this.updateListFilterAndExclude(
							element["name"],
							filter,
							exclude
						),
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
			return <td {...tdAttribute} key={`${item.id}_${x[0]}_${x[1].visible}`}>{content}</td>;
		});
		return (
			<tr {...trAttributes} key={item.id}>
				{tds}
			</tr>
		);
	}

	renderList(
		items // overridable
	) {
		return (
			<tbody styleset={__DIR__ + "virtual-table.css#tbody"}>
				{items}
			</tbody>
		);
	}

	"on click at tr"(evt, rowElement) {
		const rowItem = this.itemOfElement(rowElement);
		if (!rowItem) {
			return;
		}
		this.select(evt.ctrlKey, evt.shiftKey);
		if (typeof this.onRowClick === "function") {
			this.onRowClick(this.currentItem, rowElement, this.selectedItems);
		}
	}

	onkeydown(evt) {
		const result = super.onkeydown(evt);
		if (result) {
			this.select(evt.ctrlKey, evt.shiftKey);
			const rowElement = this.$(`tr[key=${this.currentItem.key}]`);
			if (typeof this.onRowClick === "function") {
				this.onRowClick(
					this.currentItem,
					rowElement,
					this.selectedItems
				);
			}
		}
		return result;
	}

	select(ctrl, shift) {
		const listItems = [];
		if (ctrl) {
			listItems.push(this.currentItem);
		}
		if (shift && this.currentItem) {
			const lastClickIndex = this.list.findIndex(
				(x) => x.id == this.previousItem.id
			);
			const clickIndex = this.list.findIndex(
				(x) => x.id == this.currentItem.id
			);
			if (clickIndex > lastClickIndex) {
				listItems.push(
					...this.list.slice(lastClickIndex + 1, clickIndex + 1)
				);
			} else if (clickIndex < lastClickIndex) {
				listItems.push(...this.list.slice(clickIndex, lastClickIndex));
			}
		}
		let selected = [this.currentItem];
		if (listItems.length !== 0) {
			selected = [...(this.selectedItems || selected)];
			listItems.forEach((listItem) => {
				if (!selected.includes(listItem)) {
					selected.push(listItem);
				}
			});
		}

		this.componentUpdate({
			selectedItems: selected,
		});
	}
}

function sortColumn(headerElement, table, metadata, order) {
	var name = headerElement["name"];
	var headerOrder = headerElement["order"];

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

	if (order == "descend" || headerOrder == "ascend") {
		headerElement["order"] = "descend";
		table.sortList(cmpdescend);
	} else if (order == "ascend" || headerOrder == "descend") {
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
