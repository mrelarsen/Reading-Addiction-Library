const { callReader } = Window.this.parameters;

document.ready = () => {
  document.$("#btn_reader_download").state.disabled = true;
  document.on("click", "#btn_reader_download", () => {
    const text = document.$(
      "#inp_reader_download_url_list > htmlarea"
    ).textContent;
    callReader("download_list", [text]);
    Window.this.close(0);
  });

  document.on(
    "change",
    "#inp_reader_download_url_list > htmlarea",
    (_, htmlarea) => updateDisabled(htmlarea)
  );

  document.on("click", "#btn_reader_download_paste", () => {
    const htmlarea = document.$("#inp_reader_download_url_list > htmlarea");
    htmlarea.value = callReader("paste_html");
    updateDisabled(htmlarea);
  });
};

function updateDisabled(element) {
  if (element.textContent) {
    document.$("#btn_reader_download").state.disabled = false;
  } else {
    document.$("#btn_reader_download").state.disabled = true;
  }
}
