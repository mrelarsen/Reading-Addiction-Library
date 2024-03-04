const { callReader } = Window.this.parameters;

let hideInfo = false;

document.ready = () => {
  document.$("#btn_reader_download").state.disabled = true;
  document.on("click", "#btn_reader_download", () => {
    const text = document.$(
      "#inp_reader_download_url_list > htmlarea"
    ).textContent;
    const chapter_depth = document.$("#inp_chapter_depth").textContent;
    callReader("download_list", [text, +chapter_depth]);
    Window.this.close(0);
  });
  document.on("click", "#show_hide_info", () => {
    hideInfo = !hideInfo;
    hideShow();
  });

  document.on(
    "change",
    "#inp_reader_download_url_list > htmlarea",
    (_, htmlarea) => updateDisabled(htmlarea)
  );

  document.on("click", "#btn_reader_1", () => {
    const htmlarea = document.$("#inp_chapter_depth");
    htmlarea.value = "1";
  });
  document.on("click", "#btn_reader_5", () => {
    const htmlarea = document.$("#inp_chapter_depth");
    htmlarea.value = "5";
  });
  document.on("click", "#btn_reader_10", () => {
    const htmlarea = document.$("#inp_chapter_depth");
    htmlarea.value = "10";
  });
  document.on("click", "#btn_reader_15", () => {
    const htmlarea = document.$("#inp_chapter_depth");
    htmlarea.value = "15";
  });
  document.on("click", "#btn_reader_20", () => {
    const htmlarea = document.$("#inp_chapter_depth");
    htmlarea.value = "20";
  });
  document.on("click", "#btn_reader_25", () => {
    const htmlarea = document.$("#inp_chapter_depth");
    htmlarea.value = "25";
  });

  document.on("click", "#btn_reader_download_paste", () => {
    const htmlarea = document.$("#inp_reader_download_url_list > htmlarea");
    htmlarea.value = callReader("paste_html");
    updateDisabled(htmlarea);
  });

  document.on("click", "#btn_reader_download_paste_continuous", () => {
    const htmlarea = document.$("#inp_reader_download_url_list > htmlarea");
    htmlarea.value = `!${callReader("paste_html")}`;
    updateDisabled(htmlarea);
  });

  document.on("click", "#btn_reader_download_clear", () => {
    const htmlarea = document.$("#inp_reader_download_url_list > htmlarea");
    htmlarea.value = "";
    updateDisabled(htmlarea);
  });

  document.on("click", "#btn_reader_download_add", () => {
    const htmlarea = document.$("#inp_reader_download_url_list > htmlarea");
    htmlarea.value = htmlarea.textContent
      ? `${htmlarea.value} ${callReader("paste_html")}`
      : callReader("paste_html");
    updateDisabled(htmlarea);
  });

  document.on("click", "#btn_reader_download_add_continuous", () => {
    const htmlarea = document.$("#inp_reader_download_url_list > htmlarea");
    htmlarea.value = htmlarea.textContent
      ? `${htmlarea.value} !${callReader("paste_html")}`
      : callReader("paste_html");
    updateDisabled(htmlarea);
  });
};
function hideShow() {
  if (hideInfo) {
    document.$("#hidden_info").style.display = "block";
  } else {
    document.$("#hidden_info").style.display = "none";
  }
}

function updateDisabled(element) {
  if (element.textContent) {
    document.$("#btn_reader_download").state.disabled = false;
  } else {
    document.$("#btn_reader_download").state.disabled = true;
  }
}
