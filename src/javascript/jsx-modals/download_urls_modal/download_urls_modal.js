import { ModalComponent } from "../basic_modal/modal_component.js";

export class DownloadUrlsModal extends ModalComponent {
  callReader;
  downloadDisabled = true;

  this(props) {
    this.callReader = props.callReader;
  }

  render() {
    return (
      <div id="modal-content" style="height:*">
        <label id="lbl_reader_title">Url list</label>
        <button id="btn_reader_download_paste" class="dark ml-3">
          Paste
        </button>
        <richtext id="inp_reader_download_url_list" class="dark">
          <htmlarea class="dark" />
        </richtext>
        <button
          class="dark"
          id="btn_reader_download"
          disabled={this.downloadDisabled}
        >
          Download list
        </button>
      </div>
    );
  }

  updateDisabled(element) {
    this.componentUpdate({ downloadDisabled: !element.textContent });
  }

  "on click at #btn_reader_download"() {
    const text = this.$("#inp_reader_download_url_list > htmlarea").textContent;
    this.callReader("download_list", [text]);
    this.close(0);
  }

  "on change at #inp_reader_download_url_list > htmlarea"(_, element) {
    this.updateDisabled(element);
  }

  "on click at #btn_reader_download_paste"() {
    const htmlarea = this.$("#inp_reader_download_url_list > htmlarea");
    htmlarea.value = this.callReader("paste_html");
    this.updateDisabled(htmlarea);
  }
}
