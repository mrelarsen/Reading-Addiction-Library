import { Remarkable } from "../../../../libraries/remarkable/index.js";
import { HeaderIds } from "../../../../libraries/remarkable/plugins/header-ids.js";
import { ReadUrlsModal } from "../../jsx-modals/read_urls_modal/read_urls_modal.js";
import { DownloadUrlsModal } from "../../jsx-modals/download_urls_modal/download_urls_modal.js";
import { ReaderSettingsModal } from "../../jsx-modals/reader_settings_modal/reader_settings_modal.js";

var reader = document.$("#reader_section");
var reader_text_modifier = 1;
const callReader = (methodName, params) =>
  Window.this.xcall("call_handler", "reader_handler", methodName, params || []);

globalThis.setUrls = setUrls;
globalThis.replaceManga = (images) => replaceManga(images);

let settings;
let urlDict = {};
const useJSX = false;

document.ready = () => {
  const urls = callReader("get_urls");
  setUrls(urls);
  settings = callReader("get_settings");
};

function setUrls(urls) {
  urlDict = urls;
  reader.$("#rdr_btn_prev").state.disabled = !urls["prev"];
  reader.$("#rdr_btn_copy_prev").state.disabled = !urls["prev"];
  reader.$("#rdr_btn_next").state.disabled = !urls["next"];
  reader.$("#rdr_btn_copy_next").state.disabled = !urls["next"];
  reader.$("#rdr_btn_copy").state.disabled = !urls["current"];
}

function changeClass(selector, a, b) {
  document.$(selector).classList.remove(a);
  document.$(selector).classList.add(b);
}

function replaceManga(images) {
  loadToggle(true);
  const html = images
    .map(
      (_, index) =>
        `<div class="manga-image" style="width:*;"><img #manga-page-${index} style="max-width: 50%; display: block;  margin-left: auto;  margin-right: auto;"></div>`
    )
    .join("");
  globalThis.replaceId("rdr_content", html);
  for (var i = 0; i < images.length; i++) {
    const image = images[i];
    const mangaImg = reader.$(`#manga-page-${i}`);
    mangaImg.value = Graphics.Image.fromBytes(image);
    // mangaImg.onClick((evt, element) => console.log("click image 1"));
    mangaImg.on(
      "click",
      (evt, element) =>
        (element.style.maxWidth =
          element.style.maxWidth == "100%" ? "50%" : "100%")
    );
  }
  loadToggle(false);
}

const md = new Remarkable({ html: true });
md.use(HeaderIds({ anchorText: " " }));

function loadMarkdown(href) {
  href = URL.fromPath(href);
  load(href);
}

async function load(href) {
  try {
    const url = new URL(href);
    if (url.extension !== "md") return;

    const r = await fetch(url.href);
    let body = r.text();
    body = md.render(body);
    callReader("read_html", [body]);
  } catch (e) {
    console.error(e.message);
  }
}

// Window.this.document.on("keydown", (evt) => console.log(evt.code, evt.keyCode));

onClick([
  [
    "#rdr_btn_open_file",
    () => {
      let fileName = Window.this.selectFile({
        filter: "Markdown Files (*.md)|*.md;|All Files (*.*)|*.*",
        mode: "open",
        path: URL.toPath(__DIR__ + "../../Novels/Stories"),
      });
      if (fileName) {
        loadMarkdown(fileName);
      }
    },
  ],
  ["#rdr_btn_reset", () => callReader("reset_reader")],
  [
    "#rdr_btn_download",
    () => {
      if (useJSX) {
        Window.this.modal({
          url: __DIR__ + "../../jsx-modals/basic_modal/basic_modal.htm",
          alignment: -5,
          width: 400,
          height: 350,
          parameters: {
            jsx: (
              <DownloadUrlsModal callReader={callReader}></DownloadUrlsModal>
            ),
            title: "Download wavs from urls",
          },
        });
      } else {
        Window.this.modal({
          url:
            __DIR__ +
            "../../modals/download_urls_modal/download_urls_modal.htm",
          alignment: -5,
          width: 400,
          height: 350,
          parameters: { callReader: callReader },
        });
      }
    },
  ],
  [
    '[id^="line-"]',
    (_, element) => callReader("goto_line", [element.id.substring(5)]),
  ],
  [
    "#rdr_btn_read",
    () => {
      if (useJSX) {
        Window.this.modal({
          url: __DIR__ + "../../jsx-modals/basic_modal/basic_modal.htm",
          alignment: -5,
          width: 400,
          height: 350,
          parameters: {
            jsx: (
              <ReadUrlsModal
                callReader={callReader}
                text={urlDict["list"]?.join(" ") || urlDict["current"]}
              ></ReadUrlsModal>
            ),
            title: "Read content of urls",
          },
        });
      } else {
        Window.this.modal({
          url: __DIR__ + "../../modals/read_urls_modal/read_urls_modal.htm",
          alignment: -5,
          width: 400,
          height: 350,
          parameters: {
            text: urlDict["list"]?.join(" ") || urlDict["current"],
            callReader: callReader,
          },
        });
      }
    },
  ],
  [
    "#rdr_btn_settings",
    () => {
      if (!settings) settings = callReader("get_settings");
      if (useJSX) {
        Window.this.modal({
          url: __DIR__ + "../../jsx-modals/basic_modal/basic_modal.htm",
          alignment: -5,
          width: 400,
          height: 350,
          parameters: {
            jsx: (
              <ReaderSettingsModal
                callReader={callReader}
                changeClass={changeClass}
                settings={settings}
              ></ReaderSettingsModal>
            ),
            title: "Settings",
          },
        });
      } else {
        Window.this.modal({
          url:
            __DIR__ +
            "../../modals/reader_settings_modal/reader_settings_modal.htm",
          alignment: -5,
          width: 400,
          height: 350,
          parameters: {
            callReader: callReader,
            changeClass: changeClass,
            saveSettings: (settings) =>
              Window.this.xcall("save_settings", settings),
            settings: settings,
          },
        });
      }
    },
  ],
  ["#rdr_btn_paste", () => callReader("read_paste")],
  ["#rdr_btn_prev", () => callReader("read", [-1])],
  ["#rdr_btn_next", () => callReader("read", [1])],
  ["#rdr_btn_pause", () => callReader("pause")],
  ["#rdr_btn_copy", () => callReader("copy_url")],
  ["#rdr_btn_copy_prev", () => callReader("copy_url", [-1])],
  ["#rdr_btn_copy_next", () => callReader("copy_url", [1])],
  [
    "#rdr_content a",
    () => (_, element) => {
      const link = element.getAttribute("link");
      callReader("copy_text", [link]);
      callReader("open_link", [link]);
    },
  ],
]);
