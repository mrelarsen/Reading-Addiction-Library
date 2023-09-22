const { chapterId, chapterRow, chapterStatus, chapterRowElement, callStory } =
  Window.this.parameters;

const chapterStatuses = ["reading", "downloaded", "completed"];

document.ready = () => {
  const saveBtn = document.$("#btn_chapter_save");
  saveBtn.state.disabled = true;
  chapterStatuses.forEach((status) => {
    document
      .$("#sel_chapter_status")
      .append(<option class="dark">{status}</option>);
  });
  document.$("#sel_chapter_status").value = chapterStatus;
  saveBtn.on("click", () => saveChapter());
  document.on(
    "change",
    "#inp_chapter_title, #sel_chapter_status, #inp_chapter_desc > htmlarea",
    () => (saveBtn.state.disabled = false)
  );
  setChapterDetails();
};

function saveChapter() {
  const title = document.$("#inp_chapter_title").textContent;
  const status = document.$("#sel_chapter_status").value;
  const desc = document.$("#inp_chapter_desc > htmlarea").textContent;
  callStory("save_chapter_details", [chapterId, title, desc, status]);
  chapterRow.name = title;
  chapterRow.status = status;
  chapterRowElement.$("td[name]").textContent = title;
  chapterRowElement.$("td[status]").textContent = status;
  Window.this.close();
}

function setChapterDetails() {
  if (chapterId < 1) return;
  const chapter = callStory("get_chapter", [chapterId]);
  document.$("#inp_chapter_title").textContent = chapter["name"];
  document.$("#inp_chapter_desc > htmlarea").textContent = chapter["desc"];
}
