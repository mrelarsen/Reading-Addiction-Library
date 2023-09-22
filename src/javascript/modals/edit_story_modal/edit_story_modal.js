const { storyId, storyRow, storyRowElement, callStory, storyPicker } =
  Window.this.parameters;

document.ready = () => {
  const saveBtn = document.$("#btn_story_save");
  saveBtn.state.disabled = true;
  saveBtn.on("click", () => save_story());
  document.on(
    "change",
    "#inp_story_title, #inp_story_rating, #inp_story_tags, #inp_story_desc > htmlarea",
    () => (saveBtn.state.disabled = false)
  );
  setStoryDetails();
};

function save_story() {
  const title = document.$("#inp_story_title").textContent;
  const desc = document.$("#inp_story_desc > htmlarea").textContent;
  const rating = document.$("#inp_story_rating").textContent;
  const tags = document.$("#inp_story_tags").textContent;
  callStory("save_story_details", [storyId, title, desc, rating, tags]);
  storyRow.rating = rating;
  storyRow.tags = tags;
  if (title) {
    storyRow.name = title;
    storyRowElement.$("td[name]").textContent = title;
  }
  storyRowElement.$("td[rating]").textContent = rating || 0;
  storyRowElement.$("td[tags]").textContent = tags;
  storyPicker.updateList();
  Window.this.close();
}

function setStoryDetails() {
  if (!(storyId > 0)) return;
  const story = callStory("get_story", [storyId]);
  document.$("#inp_story_title").textContent = story["name"];
  document.$("#inp_story_tags").textContent = story["tags"] || "";
  document.$("#inp_story_rating").textContent =
    story["rating"] == "None" ? "0" : story["rating"] || "0";
  document.$("#inp_story_desc > htmlarea").textContent = story["desc"];
}
