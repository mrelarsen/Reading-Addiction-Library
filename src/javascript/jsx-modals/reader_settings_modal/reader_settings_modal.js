export class ReaderSettingsModal extends Element {
  settings;
  changeClass;
  callReader;
  saveDisabled = true;
  close;

  this(props) {
    this.settings = props.settings;
    this.changeClass = props.changeClass;
    this.callReader = props.callReader;
  }

  render() {
    return (
      <div id="modal-content" style="height:*">
        <label id="lbl_story_title">Settings</label>
        <br />
        <div>
          <label>Voice:</label>
          <br />
          <button class="dark" id="rdr_btn_rate">
            {`Rate: x${this.settings.rate}`}
          </button>
          <select
            class="dark"
            id="rdr_slt_voice"
            value={this.settings.voices.find((x) =>
              x.includes(this.settings.voice)
            )}
          >
            {this.settings.voices.map((voice) => (
              <option class="dark">{voice}</option>
            ))}
          </select>
        </div>
        <div>
          <label>Automatic:</label>
          <br />
          <button class="dark" id="rdr_btn_auto">
            {`Continuation: ${this.settings.auto_continuation}`}
          </button>
          <button class="dark" id="rdr_btn_scroll">
            {`Scroll: ${this.settings.auto_scroll}`}
          </button>
        </div>
        <div>
          <label>Text:</label>
          <br />
          <button class="dark" id="rdr_btn_text_size">
            {`Text ${this.settings.text_size}*`}
          </button>
        </div>
        <div class="inline" style="text-align:right;">
          <button
            class="dark"
            id="rdr_btn_save_settings"
            disabled={this.saveDisabled}
          >
            Save as default
          </button>
        </div>
      </div>
    );
  }

  "on change at #inp_reader_url_list > htmlarea, #rdr_btn_rate, #rdr_btn_auto, #rdr_btn_scroll, #rdr_btn_text_size, #rdr_slt_voice"() {
    this.componentUpdate({ saveDisabled: false });
  }

  "on click at #rdr_btn_save_settings"() {
    this.callReader("save_settings", [this.settings]);
    this.close();
  }

  "on click at #btn_reader_read"() {
    const text = document.$("#inp_reader_url_list > htmlarea").textContent;
    this.callReader("read_list", [text]);
    this.close();
  }

  "on click at #btn_reader_paste"() {
    document.$("#inp_reader_url_list > htmlarea").value =
      this.callReader("paste_html");
  }

  "on click at #rdr_btn_rate"(_, btn) {
    const rate = this.callReader("next_rate");
    btn.textContent = `Rate: x${rate}`;
    this.componentUpdate({ settings: { ...this.settings, rate } });
  }

  "on click at #rdr_btn_auto"(_, btn) {
    const auto_continuation = this.callReader("toggle_auto");
    btn.textContent = `Continuation: ${auto_continuation}`;
    this.componentUpdate({ settings: { ...this.settings, auto_continuation } });
  }

  "on click at #rdr_btn_scroll"(_, btn) {
    const auto_scroll = this.callReader("toggle_scroll");
    btn.textContent = `Scroll: ${auto_scroll}`;
    this.componentUpdate({ settings: { ...this.settings, auto_scroll } });
  }

  "on click at #rdr_btn_text_size"(_, btn) {
    const prevClass = `tm-${this.settings.text_size}`;
    this.componentUpdate({
      settings: {
        ...this.settings,
        text_size: (this.settings.text_size % 7) + 1,
        saveDisabled: false,
      },
    });
    const newClass = `tm-${this.settings.text_size}`;
    this.changeClass("#rdr_content", prevClass, newClass);
    btn.textContent = `Text ${this.settings.text_size}*`;
  }
}
