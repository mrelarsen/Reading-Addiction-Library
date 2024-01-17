export class ReadUrlsModal extends Element {
  text;
  callReader;
  btnDisabled = true;
  close;

  this(props) {
    this.text = props.text;
    this.callReader = props.callReader;
  }

  render() {
    return (
      <div id="modal-content" style="height:*">
        <label id="lbl_story_title">Read content of urls</label>
        <br />
        <label id="lbl_reader_title">Url list</label>
        <button class="dark" id="btn_reader_paste">
          Replace
        </button>
        <button class="dark" id="btn_reader_clear">
          Clear
        </button>
        <button class="dark" id="btn_reader_add">
          Add
        </button>
        <br />
        <richtext
          class="dark"
          id="inp_reader_url_list"
          style="width:*;height:*;"
        >
          <htmlarea class="dark">{this.text}</htmlarea>
        </richtext>
        <button class="dark" disabled={this.btnDisabled} id="btn_reader_read">
          Read list
        </button>
      </div>
    );
  }

  updateDisabled(element) {
    this.componentUpdate({ btnDisabled: !element.textContent });
  }

  "on click at #btn_reader_read"() {
    const textContent = document.$(
      "#inp_reader_url_list > htmlarea"
    ).textContent;
    this.callReader("read_list", [textContent]);
    this.close();
  }

  "on change at #inp_reader_url_list > htmlarea"(_, htmlarea) {
    this.updateDisabled(htmlarea);
  }

  "on click at #btn_reader_paste"() {
    const htmlarea = document.$("#inp_reader_url_list > htmlarea");
    htmlarea.value = this.callReader("paste_html");
    this.updateDisabled(htmlarea);
  }

  "on click at #btn_reader_clear"() {
    const htmlarea = document.$("#inp_reader_url_list > htmlarea");
    htmlarea.value = "";
    this.updateDisabled(htmlarea);
  }

  "on click at #btn_reader_add"() {
    const htmlarea = document.$("#inp_reader_url_list > htmlarea");
    htmlarea.value = htmlarea.textContent
      ? `${htmlarea.value} ${this.callReader("paste_html")}`
      : this.callReader("paste_html");
    this.updateDisabled(htmlarea);
  }
}
