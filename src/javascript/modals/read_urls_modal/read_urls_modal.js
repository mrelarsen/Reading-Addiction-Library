const { callReader, text } = Window.this.parameters;

document.ready = () => {
  document.$("#btn_reader_read").state.disabled = true;
  document.$("#inp_reader_url_list > htmlarea").textContent = text;
  document.on("click", "#btn_reader_read", () => {
    const textContent = document.$(
      "#inp_reader_url_list > htmlarea"
    ).textContent;
    callReader("read_list", [textContent]);
    Window.this.close(0);
  });

  document.on("change", "#inp_reader_url_list > htmlarea", (_, htmlarea) =>
    updateDisabled(htmlarea)
  );

  document.on("click", "#btn_reader_paste", () => {
    const htmlarea = document.$("#inp_reader_url_list > htmlarea");
    htmlarea.value = callReader("paste_html");
    updateDisabled(htmlarea);
  });

  document.on("click", "#btn_reader_clear", () => {
    const htmlarea = document.$("#inp_reader_url_list > htmlarea");
    htmlarea.value = "";
    updateDisabled(htmlarea);
  });

  document.on("click", "#btn_reader_add", () => {
    const htmlarea = document.$("#inp_reader_url_list > htmlarea");
    htmlarea.value = htmlarea.textContent
      ? `${htmlarea.value} ${callReader("paste_html")}`
      : callReader("paste_html");
    updateDisabled(htmlarea);
  });
};

function updateDisabled(element) {
  if (element.textContent) {
    document.$("#btn_reader_read").state.disabled = false;
  } else {
    document.$("#btn_reader_read").state.disabled = true;
  }
}
