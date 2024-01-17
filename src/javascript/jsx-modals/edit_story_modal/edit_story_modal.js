export class EditStoryModal extends Element {
  storyId;
  storyRow;
  storyRowElement;
  callStory;
  story;
  storyDisabled = true;
  close;

  this(props) {
    this.storyId = props.storyId;
    this.storyRow = props.storyRow;
    this.storyRowElement = props.storyRowElement;
    this.callStory = props.callStory;
    this.story = this.callStory("get_story", [this.storyId]);
  }

  render() {
    return (
      <div id="modal-content" style="height:*">
        <label id="lbl_story_title">Story title</label>
        <br />
        <input
          class="dark"
          id="inp_story_title"
          type="text"
          style="width:*;"
          value={this.story["name"]}
        ></input>
        <br />
        <label id="lbl_story_rating">Rating</label>
        <br />
        <input
          class="dark"
          id="inp_story_rating"
          type="text"
          style="width:*;"
          value={this.story["rating"]}
        ></input>
        <br />
        <label id="lbl_story_tags">Tags</label>
        <br />
        <input
          class="dark"
          id="inp_story_tags"
          type="text"
          style="width:*;"
          value={this.story["tags"]}
        ></input>
        <br />
        <label id="lbl_story_desc">Story description</label>
        <richtext class="dark" id="inp_story_desc" style="width:*;height:*;">
          <toolbar class="dark">
            <button class="dark bold"></button>
            <button class="dark italic"></button>
            <button class="dark sub"></button>
            <button class="dark sup"></button>
            <button class="dark del"></button>
            <button class="dark underline"></button>
            <button class="dark code"></button>
          </toolbar>
          <htmlarea class="dark">{this.story["desc"]}</htmlarea>
        </richtext>
        <button class="dark" id="btn_story_save" disabled={this.storyDisabled}>
          Save story
        </button>
      </div>
    );
  }

  save_story() {
    const title = document.$("#inp_story_title").textContent;
    const desc = document.$("#inp_story_desc > htmlarea").textContent;
    const rating = document.$("#inp_story_rating").textContent;
    const tags = document.$("#inp_story_tags").value ? 1 : 0;
    this.callStory("save_story_details", [
      this.storyId,
      title,
      desc,
      rating,
      tags,
    ]);
    this.storyRow.rating = rating;
    this.storyRow.tags = tags;
    if (title) {
      this.storyRow.name = title;
      this.storyRowElement.$("td[name]").textContent = title;
    }
    this.storyRowElement.$("td[rating]").textContent = rating || 0;
    this.storyRowElement.$("td[tags]").textContent = nsfw || 0;
    this.storyPicker.updateList();
    this.close();
  }

  "on change at #inp_story_title, #inp_story_rating, #inp_story_tags, #inp_story_desc > htmlarea"() {
    this.componentUpdate({ storyDisabled: false });
  }

  "on click at #btn_story_save"() {
    this.saveChapter();
  }
}
