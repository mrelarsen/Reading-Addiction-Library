export class VirtualList extends Element {
  currentItem = null; // item, one of items
  previousItem = null; // item, one of items
  selectedItems; // TODO: = new WeakSet();
  styleSet;
  props;

  this(props) {
    const { renderItem, renderList, ...rest } = props;
    super.this?.(rest);
    this.props = rest;
    this.renderItem = renderItem || this.renderItem;
    this.renderList = renderList || this.renderList;
    this.styleset =
      props.styleset || __DIR__ + "virtual-select.css#virtual-select";
  }

  itemAt(at) {
    // virtual function, must be overriden
    return null;
  }

  totalItems() {
    // virtual function, must be overriden
    return 0;
  }

  indexOf(item) {
    // virtual function, must be overriden
    return -1;
  }

  render() {
    const list = [];
    if (!this.vlist) return this.renderList(list);

    const firstIndex = this.vlist.firstBufferIndex;
    let lastIndex = this.vlist.lastBufferIndex;
    const firstVisibleIndex =
      firstIndex + this.vlist.firstVisibleItem?.elementIndex || 0;
    const lastVisibleIndex =
      firstIndex + this.vlist.lastVisibleItem?.elementIndex;

    const totalItems = this.totalItems();

    if (this.vlist.itemsTotal != totalItems) {
      // number of items reduced, update scroll
      if (firstVisibleIndex == 0) {
        this.post(() => {
          this.vlist.navigate("start");
        });
        return this.renderList([]); // render empty list and request "from start" navigation
      }

      if (lastVisibleIndex >= totalItems) {
        this.post(() => {
          this.vlist.navigate("end");
        });
        return this.renderList([]); // render empty list and request "from end" navigation
      }

      lastIndex =
        Math.min(totalItems, firstIndex + this.vlist.slidingWindowSize) - 1;
      this.post(() => {
        console.log(totalItems, this.vlist.itemsBefore, this.children.length);
        this.vlist.itemsAfter =
          totalItems - this.vlist.itemsBefore - this.children.length;
      });
    }

    const { currentItem, selectedItems } = this;
    for (let index = firstIndex; index <= lastIndex; ++index) {
      const item = this.itemAt(index);
      if (item)
        list.push(
          this.renderItem(
            item,
            item === currentItem,
            selectedItems?.includes(item)
          )
        );
    }

    return this.renderList(list);
  }

  // scroll down
  appendElements(index, n) {
    const { currentItem, selectedItems } = this;
    if (index === undefined) index = 0;
    const elements = [];
    for (let i = 0; i < n; ++i, ++index) {
      if (index >= this.totalItems()) break;
      const item = this.itemAt(index);
      elements.push(
        this.renderItem(
          item,
          item === currentItem,
          selectedItems?.includes(item)
        )
      );
    }

    this.append(elements);
    return { moreafter: this.totalItems() - index }; // return estimated number of items below this chunk
  }

  // scroll up
  prependElements(index, n) {
    const { currentItem, selectedItems } = this;
    if (index === undefined) index = this.totalItems() - 1;
    const elements = [];
    for (let i = 0; i < n; ++i, --index) {
      if (index < 0) break;
      const item = this.itemAt(index);
      elements.push(
        this.renderItem(
          item,
          item === currentItem,
          selectedItems?.includes(item)
        )
      );
    }

    elements.reverse();
    this.prepend(elements);
    return { morebefore: index < 0 ? 0 : index + 1 }; // return estimated number of items above this chunk
  }

  // scroll to
  replaceElements(index, n) {
    const { currentItem, selectedItems } = this;
    const elements = [];
    const start = index;
    for (let i = 0; i < n; ++i, ++index) {
      if (index >= this.totalItems()) break;
      const item = this.itemAt(index);
      elements.push(
        this.renderItem(
          item,
          item === currentItem,
          selectedItems?.includes(item)
        )
      );
    }

    this.patch(elements);
    return {
      morebefore: start <= 0 ? 0 : start,
      moreafter: this.totalItems() - index,
    }; // return estimated number of items before and above this chunk
  }

  renderList(
    items // overridable
  ) {
    return (
      <virtual-select {...this.props} styleset={this.styleset}>
        {items}
      </virtual-select>
    );
  }

  renderItem(
    item,
    index // overridable
  ) {
    return <option key={index}>item {index}</option>;
  }

  oncontentrequired(evt) {
    const { length, start, where } = evt.data;
    if (where > 0) evt.data = this.appendElements(start, length);
    // scrolling down, need to append more elements
    else if (where < 0) evt.data = this.prependElements(start, length);
    // scrolling up, need to prepend more elements
    else evt.data = this.replaceElements(start, length); // scrolling to index
    return true;
  }

  itemOfElement(element) {
    return this.itemAt(element.elementIndex + this.vlist.firstBufferIndex);
  }

  advanceNext() {
    if (!this.currentItem)
      this.componentUpdate({
        previousItem: this.currentItem,
        currentItem: this.itemOfElement(this.vlist.firstVisibleItem),
      });
    else {
      let index = this.indexOf(this.currentItem);
      if (++index < this.totalItems()) {
        console.log(this.currentItem["name"], this.itemAt(index)["name"]);
        this.componentUpdate({
          previousItem: this.currentItem,
          currentItem: this.itemAt(index),
        });
        this.vlist.advanceTo(index);
      }
    }
    return true;
  }

  advancePrevious() {
    if (!this.currentItem)
      this.componentUpdate({
        previousItem: this.currentItem,
        currentItem: this.itemOfElement(this.vlist.lastVisibleItem),
      });
    else {
      let index = this.indexOf(this.currentItem);
      if (--index >= 0) {
        this.componentUpdate({
          previousItem: this.currentItem,
          currentItem: this.itemAt(index),
        });
        this.vlist.advanceTo(index);
      }
    }
    return true;
  }

  advanceFirst() {
    this.currentItem = this.itemAt(0);
    this.vlist.navigateTo("start");
    return true;
  }

  advanceLast() {
    this.currentItem = this.itemAt(this.totalItems() - 1);
    this.vlist.navigateTo("end");
    return true;
  }

  onkeydown(evt) {
    switch (evt.code) {
      case "ArrowDown":
        return this.advanceNext();
      case "ArrowUp":
        return this.advancePrevious();
      case "End":
        return this.advanceLast();
      case "Home":
        return this.advanceFirst();
      default:
        return false;
    }
    this.post(new Event("input", { bubbles: true }));
    return true;
  }

  // auto scroll with pressed mouse button ++
  ["on ~mousedown"](evt) {
    this.state.capture(true);
  }
  ["on ~mouseup"](evt) {
    this.state.capture(false);
  }

  ["on ~mousetick"](evt) {
    console.log(evt.y);
    let height = this.state.box("height");
    if (evt.y < 0) this.vlist.navigate("itemprior");
    else if (evt.y > height) this.vlist.navigate("itemnext");
  }
  // auto scroll with pressed mouse button --

  setCurrentOption(child) {
    let option;
    for (let node = child; node; node = node.parentElement) {
      if (node.parentElement === this) {
        option = node;
        break;
      }
    }

    if (option) {
      this.componentUpdate({
        previousItem: this.currentItem,
        currentItem: this.itemOfElement(option),
      });
      this.post(new Event("input", { bubbles: true }));
      return true;
    }
  }

  ["on mousedown"](evt) {
    if (evt.button == 1) this.setCurrentOption(evt.target);
  }

  ["on mousemove"](evt) {
    if (evt.button == 1) this.setCurrentOption(evt.target);
  }

  get value() {
    if (!this.currentItem) return;
    return this.currentItem;
  }
}
