export class EditChapterModal extends Element {
  chapterId;
  chapterRow;
  chapterRowElement;
  callStory;
  chapter;
  saveDisabled = true;
  close;
  chapterStatuses = ["reading", "downloaded", "completed"];

  this(props) {
    this.chapterId = props.chapterId;
    this.chapterRow = props.chapterRow;
    this.chapterRowElement = props.chapterRowElement;
    this.callStory = props.callStory;
    this.chapter = this.callStory("get_chapter", [this.chapterId]);
  }

  render() {
    return (
      <div id="modal-content" style="height:*">
        <label id="lbl_chapter_title">Chapter title</label>
        <br />
        <input
          class="dark mt-1 mb-1"
          id="inp_chapter_title"
          type="text"
          style="width:*;"
          value={this.chapter["name"]}
        ></input>
        <br />
        <label id="lbl_chapter_status">Chapter status</label>
        <br />
        <select
          class="dark mt-1 mb-1"
          id="sel_chapter_status"
          style="width:*;"
          value={this.chapter["status"]}
        >
          {this.chapterStatuses.map((status) => (
            <option class="dark">{status}</option>
          ))}
        </select>
        <br />
        <label id="lbl_chapter_desc">Chapter description</label>
        <richtext id="inp_chapter_desc" class="dark" style="width:*;height:*;">
          <toolbar class="dark">
            <button class="dark bold"></button>
            <button class="dark italic"></button>
            <button class="dark sub"></button>
            <button class="dark sup"></button>
            <button class="dark del"></button>
            <button class="dark underline"></button>
            <button class="dark code"></button>
          </toolbar>
          <htmlarea class="dark">{this.chapter["desc"]}</htmlarea>
        </richtext>
        <button id="btn_chapter_save" class="dark" disabled={this.saveDisabled}>
          Save chapter
        </button>
      </div>
    );
  }

  saveChapter() {
    const title = this.$("#inp_chapter_title").textContent;
    const desc = this.$("#inp_chapter_desc > htmlarea").textContent;
    this.callStory("save_chapter_details", [this.chapterId, title, desc]);
    this.chapterRow.name = title;
    this.chapterRowElement.$("td[name]").textContent = title;
    this.close();
  }

  "on change at #inp_chapter_title, #inp_chapter_desc > htmlarea"() {
    this.componentUpdate({ saveDisabled: false });
  }

  "on click at #btn_chapter_save"() {
    this.saveChapter();
  }
}
