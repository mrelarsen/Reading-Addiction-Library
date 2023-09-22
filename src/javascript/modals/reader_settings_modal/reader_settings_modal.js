import { onClick } from "../../../../libraries/methods";
const { callReader, changeClass, settings } = Window.this.parameters;

document.ready = () => {
  document.$("#rdr_btn_rate").textContent = `Rate: x${settings.rate}`;
  settings.voices.forEach((voice) => {
    document.$("#rdr_slt_voice").append(<option class="dark">{voice}</option>);
  });

  document.$("#rdr_slt_voice").value = settings.voice;
  document
    .$("#rdr_slt_voice")
    .on("change", (_, el) => callReader("set_voice", [el.value]));

  document.$(
    "#rdr_btn_auto"
  ).textContent = `Continuation: ${settings.auto_continuation}`;
  document.$("#rdr_btn_scroll").textContent = `Scroll: ${settings.auto_scroll}`;
  document.$("#rdr_btn_text_size").textContent = `Text ${settings.text_size}*`;
  onClickLocal();
};

function onClickLocal() {
  onClick([
    [
      "#rdr_btn_save_settings",
      () => {
        callReader("save_settings", [settings]);
        Window.this.close(0);
      },
    ],
    [
      "#btn_reader_read",
      () => {
        const text = document.$("#inp_reader_url_list > htmlarea").textContent;
        callReader("read_list", [text]);
        Window.this.close(0);
      },
    ],
    [
      "#btn_reader_paste",
      () =>
        (document.$("#inp_reader_url_list > htmlarea").value =
          callReader("paste_html")),
    ],
    [
      "#rdr_btn_rate",
      (_, btn) => {
        const rate = callReader("next_rate");
        btn.textContent = `Rate: x${rate}`;
        settings.rate = rate;
      },
    ],
    [
      "#rdr_btn_auto",
      (_, btn) => {
        const auto_continuation = callReader("toggle_auto");
        btn.textContent = `Continuation: ${auto_continuation}`;
        settings.auto_continuation = auto_continuation;
      },
    ],
    [
      "#rdr_btn_scroll",
      (_, btn) => {
        const auto_scroll = callReader("toggle_scroll");
        btn.textContent = `Scroll: ${auto_scroll}`;
        settings.auto_scroll = auto_scroll;
      },
    ],
    [
      "#rdr_btn_text_size",
      (_, btn) => {
        const prevClass = `tm-${settings.text_size}`;
        settings.text_size = (settings.text_size % 7) + 1;
        const newClass = `tm-${settings.text_size}`;
        changeClass("#rdr_content", prevClass, newClass);
        btn.textContent = `Text ${settings.text_size}*`;
      },
    ],
  ]);
}
